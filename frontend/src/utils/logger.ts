import { appDataDir, resolveResource } from '@tauri-apps/api/path';
import { createDir, writeFile, readTextFile } from '@tauri-apps/api/fs';
import { join } from '@tauri-apps/api/path';
import { open } from '@tauri-apps/api/shell';
import { invoke } from '@tauri-apps/api/tauri';

// Log levels
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

/**
 * Detect if we're running in development mode
 * In development: running with `tauri dev`
 * In production: running as bundled app
 */
async function isDevelopmentMode(): Promise<boolean> {
  try {
    // Check if we're running on localhost (development server)
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

    // In development mode, the URL typically contains localhost
    // In production mode, it's usually a tauri:// protocol or file://
    const isDev = isLocalhost || window.location.protocol === 'http:';

    return isDev;
  } catch {
    // Fallback: assume production if we can't determine
    return false;
  }
}

// Logger configuration
interface LoggerConfig {
  logToConsole: boolean;
  logToFile: boolean;
  logLevel: LogLevel;
  maxLogSize: number; // in bytes
  batchSize: number; // number of messages to batch before writing to file
  flushInterval: number; // milliseconds between forced flushes
  overrideConsole: boolean; // whether to override console methods
}

// Default configuration
const defaultConfig: LoggerConfig = {
  logToConsole: true,
  logToFile: true,
  logLevel: LogLevel.INFO,
  maxLogSize: 5 * 1024 * 1024, // 5MB
  batchSize: 10, // batch 10 messages before writing
  flushInterval: 5000, // flush every 5 seconds
  overrideConsole: false // don't override console by default
};

class Logger {
  private config: LoggerConfig;
  private logDir: string | null = null;
  private logFilePath: string | null = null;
  private initialized = false;
  private messageQueue: string[] = [];
  private flushTimer: ReturnType<typeof setTimeout> | null = null;
  private isWriting = false;

  constructor(config: Partial<LoggerConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
  }

  /**
   * Initialize the logger
   */
  async init(): Promise<void> {
    if (this.initialized) return;

    try {
      const isDev = await isDevelopmentMode();

      // Use the same directory structure as backend logs for consistency
      // Match the backend's environment-based path logic exactly:
      // Development: backend/logs (relative to project root)
      // Production: %APPDATA%/kvs/logs/

      if (isDev) {
        // Development mode: try multiple approaches to find backend/logs directory
        let backendLogsFound = false;

        // Try different path patterns that might work with Tauri's working directory
        const pathsToTry = [
          await join('..', '..', 'backend', 'logs'),  // From frontend/src-tauri/target/debug
          await join('..', 'backend', 'logs'),        // From frontend/src-tauri
          await join('backend', 'logs'),              // From project root
          await join('..', '..', '..', 'backend', 'logs'), // From deeper nested structure
        ];

        for (const pathToTry of pathsToTry) {
          try {
            // Test if we can create the directory to verify the path works
            await createDir(pathToTry, { recursive: true });
            this.logDir = pathToTry;
            console.log(`[DEBUG_LOG] Development mode: Successfully using backend/logs directory: ${this.logDir}`);
            backendLogsFound = true;
            break;
          } catch (error) {
            console.log(`[DEBUG_LOG] Development mode: Failed to use path ${pathToTry}: ${error}`);
            continue;
          }
        }

        if (!backendLogsFound) {
          console.warn('Could not use any backend/logs directory path, falling back to appdata');
          // Fallback: use appdata directory even in development
          const appDataDirPath = await appDataDir();
          this.logDir = await join(appDataDirPath, 'kvs', 'logs');
          console.log(`[DEBUG_LOG] Development mode: Fallback to AppData directory: ${this.logDir}`);
        }
      } else {
        // Production mode: use %APPDATA%/kvs/logs/ (same as backend)
        const appDataDirPath = await appDataDir();
        this.logDir = await join(appDataDirPath, 'kvs', 'logs');
        console.log(`[DEBUG_LOG] Production mode: Using AppData directory: ${this.logDir}`);
      }

      // Ensure logDir is not null before proceeding
      if (!this.logDir) {
        throw new Error('Failed to initialize log directory');
      }

      await createDir(this.logDir, { recursive: true });
      this.logFilePath = await join(this.logDir, 'frontend.log');

      // Set up flush timer if logging to file is enabled
      if (this.config.logToFile) {
        this.setupFlushTimer();
      }

      this.initialized = true;

      this.info(`Logger initialized in ${isDev ? 'development' : 'production'} mode`);
      this.info(`Log directory: ${this.logDir}`);
    } catch (error) {
      console.error('Failed to initialize logger:', error);
    }
  }

  /**
   * Set up the flush timer to periodically write logs to file
   */
  private setupFlushTimer(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }

    this.flushTimer = setInterval(() => {
      this.flush().catch(err => {
        console.error('Failed to flush logs:', err);
      });
    }, this.config.flushInterval);
  }

  /**
   * Flush the message queue to the log file
   */
  private async flush(): Promise<void> {
    if (!this.config.logToFile || !this.logFilePath || !this.initialized || this.isWriting || this.messageQueue.length === 0) {
      return;
    }

    this.isWriting = true;
    let messages: string[] = [];

    try {
      // Get messages to write and clear the queue
      messages = [...this.messageQueue];
      this.messageQueue = [];

      // Join messages with newlines
      const content = messages.join('\n');

      // Create a promise that resolves after a timeout
      const writeTimeoutPromise = new Promise<void>((resolve) => {
        setTimeout(() => {
          console.warn('Log file write timed out');
          resolve();
        }, 1000); // 1 second timeout
      });

      // Race the write operation against the timeout
      await Promise.race([
        writeFile({ path: this.logFilePath, contents: content + '\n' }, { append: true }),
        writeTimeoutPromise
      ]);

      // Only check log size if write was successful and not during cleanup
      // We can determine if we're in cleanup by checking if flushTimer is null
      if (this.flushTimer !== null) {
        // Create a separate timeout for size check
        const sizeCheckTimeoutPromise = new Promise<void>((resolve) => {
          setTimeout(() => {
            console.warn('Log size check timed out during flush');
            resolve();
          }, 500); // 500ms timeout (shorter for size check)
        });

        // Race the size check against its own timeout
        await Promise.race([this.checkLogSize(), sizeCheckTimeoutPromise]);
      }
    } catch (error) {
      console.error('Failed to flush logs:', error);
      // Put the messages back in the queue only if we're not in cleanup
      // During cleanup, it's better to lose some logs than to block the app
      if (this.flushTimer !== null) {
        this.messageQueue = [...messages, ...this.messageQueue];
      }
    } finally {
      this.isWriting = false;
    }
  }

  /**
   * Check if the log file exceeds the maximum size and truncate if necessary
   */
  private async checkLogSize(): Promise<void> {
    if (!this.logFilePath) return;

    try {
      // Create a promise that resolves after a timeout
      const timeoutPromise = new Promise<void>((resolve) => {
        setTimeout(() => {
          console.warn('Log size check timed out');
          resolve();
        }, 1000); // 1 second timeout
      });

      // Race the size check operation against the timeout
      await Promise.race([this.performSizeCheck(), timeoutPromise]);
    } catch (error) {
      console.error('Failed to check log size:', error);
    }
  }

  /**
   * Perform the actual log size check and truncation
   * Separated to allow for timeout handling
   */
  private async performSizeCheck(): Promise<void> {
    if (!this.logFilePath) return;

    try {
      // Read the file content
      const content = await readTextFile(this.logFilePath);

      // Check if it exceeds the max size
      if (content.length > this.config.maxLogSize) {
        // Keep only the last half of the log
        const halfLength = Math.floor(content.length / 2);
        const truncatedLog = content.substring(content.length - halfLength);
        await writeFile({ path: this.logFilePath, contents: truncatedLog });
      }
    } catch (error) {
      console.error('Failed to perform log size check:', error);
      throw error; // Re-throw to be caught by the parent method
    }
  }

  /**
   * Format log message
   */
  private formatLogMessage(level: LogLevel, message: string): string {
    const timestamp = new Date().toISOString();
    return `[${timestamp}] [${level}] ${message}`;
  }

  /**
   * Add log message to queue
   */
  private async writeToFile(formattedMessage: string): Promise<void> {
    if (!this.config.logToFile || !this.initialized) return;

    // Add message to queue
    this.messageQueue.push(formattedMessage);

    // If queue has reached batch size, flush it
    if (this.messageQueue.length >= this.config.batchSize) {
      await this.flush();
    }
  }

  /**
   * Log a message
   */
  private async log(level: LogLevel, message: string): Promise<void> {
    // Skip logging if level is below configured level
    const levels = Object.values(LogLevel);
    if (levels.indexOf(level) < levels.indexOf(this.config.logLevel)) return;

    const formattedMessage = this.formatLogMessage(level, message);

    // Log to console
    if (this.config.logToConsole) {
      switch (level) {
        case LogLevel.DEBUG:
          console.debug(formattedMessage);
          break;
        case LogLevel.INFO:
          console.info(formattedMessage);
          break;
        case LogLevel.WARN:
          console.warn(formattedMessage);
          break;
        case LogLevel.ERROR:
          console.error(formattedMessage);
          break;
      }
    }

    // Log to file
    await this.writeToFile(formattedMessage);
  }

  /**
   * Log debug message
   */
  async debug(message: string): Promise<void> {
    await this.log(LogLevel.DEBUG, message);
  }

  /**
   * Log info message
   */
  async info(message: string): Promise<void> {
    await this.log(LogLevel.INFO, message);
  }

  /**
   * Log warning message
   */
  async warn(message: string): Promise<void> {
    await this.log(LogLevel.WARN, message);
  }

  /**
   * Log error message
   */
  async error(message: string, error?: any): Promise<void> {
    let fullMessage = message;

    if (error) {
      if (error instanceof Error) {
        fullMessage += `: ${error.message}\n${error.stack || ''}`;
      } else {
        fullMessage += `: ${JSON.stringify(error)}`;
      }
    }

    await this.log(LogLevel.ERROR, fullMessage);
  }

  /**
   * Get the path to the logs directory (containing api.log and error.log)
   * @deprecated Use getLogDirectoryPath() instead for clarity
   */
  async getLogFilePath(): Promise<string | null> {
    if (!this.initialized) {
      await this.init();
    }
    return this.logDir;
  }

  /**
   * Get the path to the frontend log file
   */
  async getFrontendLogFilePath(): Promise<string | null> {
    if (!this.initialized) {
      await this.init();
    }
    return this.logFilePath;
  }

  /**
   * Get the path to the log directory
   */
  async getLogDirectoryPath(): Promise<string | null> {
    if (!this.initialized) {
      await this.init();
    }
    return this.logDir;
  }

  /**
   * Open the API log file (api.log) in the default text editor
   */
  async openLogFile(): Promise<boolean> {
    try {
      if (!this.initialized) {
        await this.init();
      }

      if (!this.logDir) {
        console.error('Log directory path not available');
        return false;
      }

      // Open api.log instead of frontend.log as per requirements
      const apiLogPath = await join(this.logDir, 'api.log');

      // Create a promise that resolves after a timeout
      const timeoutPromise = new Promise<boolean>((resolve) => {
        setTimeout(() => {
          console.warn('Opening API log file timed out');
          resolve(false);
        }, 2000); // 2 second timeout
      });

      // Race the open operation against the timeout
      return await Promise.race([
        open(apiLogPath).then(() => true).catch((err) => {
          console.error(`Failed to open API log file (${apiLogPath}):`, err);
          return false;
        }),
        timeoutPromise
      ]);
    } catch (error) {
      console.error('Failed to open API log file:', error);
      return false;
    }
  }

  /**
   * Open the frontend log file in the default text editor
   */
  async openFrontendLogFile(): Promise<boolean> {
    try {
      if (!this.initialized) {
        await this.init();
      }

      if (!this.logFilePath) {
        console.error('Frontend log file path not available');
        return false;
      }

      // Create a promise that resolves after a timeout
      const timeoutPromise = new Promise<boolean>((resolve) => {
        setTimeout(() => {
          console.warn('Opening frontend log file timed out');
          resolve(false);
        }, 2000); // 2 second timeout
      });

      // Race the open operation against the timeout
      return await Promise.race([
        open(this.logFilePath).then(() => true).catch((err) => {
          console.error(`Failed to open frontend log file (${this.logFilePath}):`, err);
          return false;
        }),
        timeoutPromise
      ]);
    } catch (error) {
      console.error('Failed to open frontend log file:', error);
      return false;
    }
  }

  /**
   * Open the log directory in the file explorer
   */
  async openLogDirectory(): Promise<boolean> {
    try {
      if (!this.initialized) {
        await this.init();
      }

      if (!this.logDir) {
        console.error('Log directory path not available');
        return false;
      }

      // Create a promise that resolves after a timeout
      const timeoutPromise = new Promise<boolean>((resolve) => {
        setTimeout(() => {
          console.warn('Opening log directory timed out');
          resolve(false);
        }, 2000); // 2 second timeout
      });

      // Race the open operation against the timeout
      return await Promise.race([
        open(this.logDir).then(() => true).catch((err) => {
          console.error(`Failed to open log directory (${this.logDir}):`, err);
          return false;
        }),
        timeoutPromise
      ]);
    } catch (error) {
      console.error('Failed to open log directory:', error);
      return false;
    }
  }

  /**
   * Clean up resources used by the logger
   */
  async cleanup(): Promise<void> {
    // Clear the flush timer
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }

    // Flush any remaining messages with a timeout to prevent blocking
    try {
      // Create a promise that resolves after a timeout
      const timeoutPromise = new Promise<void>((resolve) => {
        setTimeout(() => {
          console.warn('Logger flush timed out during cleanup');
          resolve();
        }, 1000); // 1 second timeout
      });

      // Race the flush operation against the timeout
      await Promise.race([this.flush(), timeoutPromise]);
    } catch (error) {
      console.error('Error during logger flush:', error);
      // Continue with cleanup even if flush fails
    }
  }
}

// Create and export a singleton instance
export const logger = new Logger({
  overrideConsole: false // Disable console overrides by default to prevent UI freezing
});

// Initialize logger
logger.init().catch(console.error);

// Store original console methods
const originalConsoleLog = console.log;
const originalConsoleInfo = console.info;
const originalConsoleWarn = console.warn;
const originalConsoleError = console.error;
const originalConsoleDebug = console.debug;

// Only override console methods if enabled in config
if (logger['config'].overrideConsole) {
  console.log = function(...args: any[]) {
    originalConsoleLog.apply(console, args);
    logger.info(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : arg).join(' '));
  };

  console.info = function(...args: any[]) {
    originalConsoleInfo.apply(console, args);
    logger.info(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : arg).join(' '));
  };

  console.warn = function(...args: any[]) {
    originalConsoleWarn.apply(console, args);
    logger.warn(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : arg).join(' '));
  };

  console.error = function(...args: any[]) {
    originalConsoleError.apply(console, args);
    logger.error(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : arg).join(' '));
  };

  console.debug = function(...args: any[]) {
    originalConsoleDebug.apply(console, args);
    logger.debug(args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : arg).join(' '));
  };
}

export default logger;
