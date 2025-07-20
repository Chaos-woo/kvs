// Simple test to verify frontend logging works correctly
// This simulates the frontend logger behavior in a Node.js environment

const fs = require('fs');
const path = require('path');
const os = require('os');

// Simulate Tauri's join function
function join(...parts) {
    return path.join(...parts);
}

// Simulate Tauri's appDataDir function
function appDataDir() {
    if (process.platform === 'win32') {
        return path.join(os.homedir(), 'AppData', 'Roaming');
    }
    return os.homedir();
}

// Simulate Tauri's createDir function
function createDir(dirPath, options = {}) {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: options.recursive || false });
    }
}

// Simulate development mode detection
function isDevelopmentMode() {
    // In this test, we'll assume development mode
    return true;
}

async function testFrontendLogging() {
    console.log('=== Frontend Logging Test ===');
    
    const isDev = isDevelopmentMode();
    console.log(`Environment: ${isDev ? 'Development' : 'Production'}`);
    
    let logDir;
    
    if (isDev) {
        // Development mode: use backend/logs directory (same as backend)
        try {
            // Try to use backend/logs relative to current working directory
            logDir = join('backend', 'logs');
            console.log(`Trying to use development log directory: ${logDir}`);
        } catch (error) {
            console.warn('Could not use backend/logs directory, falling back to appdata:', error);
            // Fallback: use appdata directory even in development
            const appDataDirPath = appDataDir();
            logDir = join(appDataDirPath, 'kvs', 'logs');
        }
    } else {
        // Production mode: use %APPDATA%/kvs/logs/ (same as backend)
        const appDataDirPath = appDataDir();
        logDir = join(appDataDirPath, 'kvs', 'logs');
    }
    
    console.log(`Final log directory: ${logDir}`);
    
    // Check if directory exists
    const absoluteLogDir = path.resolve(logDir);
    console.log(`Absolute log directory: ${absoluteLogDir}`);
    
    try {
        createDir(absoluteLogDir, { recursive: true });
        console.log('✓ Log directory created/exists');
        
        // Check if backend log files exist in the same directory
        const apiLogPath = join(absoluteLogDir, 'api.log');
        const errorLogPath = join(absoluteLogDir, 'error.log');
        const frontendLogPath = join(absoluteLogDir, 'frontend.log');
        
        console.log(`API log path: ${apiLogPath}`);
        console.log(`Error log path: ${errorLogPath}`);
        console.log(`Frontend log path: ${frontendLogPath}`);
        
        // Check if files exist
        console.log(`API log exists: ${fs.existsSync(apiLogPath) ? '✓' : '✗'}`);
        console.log(`Error log exists: ${fs.existsSync(errorLogPath) ? '✓' : '✗'}`);
        console.log(`Frontend log exists: ${fs.existsSync(frontendLogPath) ? '✓' : '✗'}`);
        
        // Create a test frontend log entry
        const testMessage = `${new Date().toISOString()} - frontend - INFO - Test frontend log message\n`;
        fs.appendFileSync(frontendLogPath, testMessage);
        console.log('✓ Test message written to frontend.log');
        
        // Verify the message was written
        if (fs.existsSync(frontendLogPath)) {
            const content = fs.readFileSync(frontendLogPath, 'utf8');
            console.log(`Frontend log content (last 100 chars): ${content.slice(-100)}`);
        }
        
    } catch (error) {
        console.error('✗ Error during test:', error);
    }
}

// Run the test
testFrontendLogging().catch(console.error);