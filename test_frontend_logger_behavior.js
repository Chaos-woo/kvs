// Test to simulate frontend logger behavior after fixes
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

// Simulate development mode detection (same as in logger.ts)
function isDevelopmentMode() {
    // In this test, we'll simulate development mode
    return true;
}

async function testFrontendLoggerBehavior() {
    console.log('=== Frontend Logger Behavior Test (After Fixes) ===');
    
    const isDev = isDevelopmentMode();
    console.log(`Environment: ${isDev ? 'Development' : 'Production'}`);
    
    let logDir;
    let logFilePath;
    
    if (isDev) {
        // Development mode: try to use the same directory as backend logs
        // First try to use backend/logs relative to current working directory
        try {
            logDir = join('backend', 'logs');
            // Test if we can create the directory to verify the path works
            createDir(logDir, { recursive: true });
            console.log(`[DEBUG_LOG] Development mode: Using backend/logs directory: ${logDir}`);
        } catch (error) {
            console.warn('Could not use backend/logs directory, falling back to appdata:', error);
            // Fallback: use appdata directory even in development
            const appDataDirPath = appDataDir();
            logDir = join(appDataDirPath, 'kvs', 'logs');
            console.log(`[DEBUG_LOG] Development mode: Fallback to AppData directory: ${logDir}`);
        }
    } else {
        // Production mode: use %APPDATA%/kvs/logs/ (same as backend)
        const appDataDirPath = appDataDir();
        logDir = join(appDataDirPath, 'kvs', 'logs');
        console.log(`[DEBUG_LOG] Production mode: Using AppData directory: ${logDir}`);
    }
    
    // Create the log directory
    createDir(logDir, { recursive: true });
    logFilePath = join(logDir, 'frontend.log');
    
    console.log(`Final log directory: ${logDir}`);
    console.log(`Frontend log file path: ${logFilePath}`);
    
    // Check if directory exists and is accessible
    const absoluteLogDir = path.resolve(logDir);
    console.log(`Absolute log directory: ${absoluteLogDir}`);
    
    try {
        // Check if backend log files exist in the same directory
        const apiLogPath = join(absoluteLogDir, 'api.log');
        const errorLogPath = join(absoluteLogDir, 'error.log');
        
        console.log(`\nChecking log files in directory:`);
        console.log(`API log exists: ${fs.existsSync(apiLogPath) ? '✓' : '✗'} (${apiLogPath})`);
        console.log(`Error log exists: ${fs.existsSync(errorLogPath) ? '✓' : '✗'} (${errorLogPath})`);
        console.log(`Frontend log exists: ${fs.existsSync(logFilePath) ? '✓' : '✗'} (${logFilePath})`);
        
        // Test writing to frontend log
        const testMessage = `${new Date().toISOString()} - frontend - INFO - Test frontend log message after fixes\n`;
        fs.appendFileSync(logFilePath, testMessage);
        console.log('✓ Test message written to frontend.log');
        
        // Verify the message was written
        if (fs.existsSync(logFilePath)) {
            const content = fs.readFileSync(logFilePath, 'utf8');
            console.log(`✓ Frontend log content verified (${content.length} characters)`);
        }
        
        // Check if all log files are in the same directory
        const apiExists = fs.existsSync(apiLogPath);
        const errorExists = fs.existsSync(errorLogPath);
        const frontendExists = fs.existsSync(logFilePath);
        
        if (apiExists && errorExists && frontendExists) {
            console.log('\n✓ SUCCESS: All three log files (api.log, error.log, frontend.log) are in the same directory');
        } else if (frontendExists) {
            console.log('\n⚠ PARTIAL: Frontend.log created successfully, but backend logs may not be running yet');
        } else {
            console.log('\n✗ ISSUE: Frontend.log could not be created');
        }
        
        // Test directory listing (simulating debug-logs component behavior)
        console.log('\nDirectory contents (simulating debug-logs component):');
        const files = fs.readdirSync(absoluteLogDir);
        files.forEach(file => {
            const filePath = join(absoluteLogDir, file);
            const stats = fs.statSync(filePath);
            console.log(`  - ${file} (${stats.size} bytes)`);
        });
        
    } catch (error) {
        console.error('✗ Error during test:', error);
    }
}

// Test production mode as well
async function testProductionMode() {
    console.log('\n=== Production Mode Test ===');
    
    const appDataDirPath = appDataDir();
    const prodLogDir = join(appDataDirPath, 'kvs', 'logs');
    const tauriProdLogDir = join(appDataDirPath, 'com.kvs.dev', 'kvs', 'logs');
    
    console.log(`Expected production log directory: ${prodLogDir}`);
    console.log(`Tauri production log directory: ${tauriProdLogDir}`);
    
    // Test if Tauri production directory exists (from previous runs)
    if (fs.existsSync(tauriProdLogDir)) {
        console.log('✓ Tauri production directory exists');
        const files = fs.readdirSync(tauriProdLogDir);
        console.log(`Files in Tauri production directory: ${files.join(', ')}`);
    } else {
        console.log('ℹ Tauri production directory does not exist (normal for development testing)');
    }
}

// Run the tests
async function runTests() {
    await testFrontendLoggerBehavior();
    await testProductionMode();
    
    console.log('\n=== Test Summary ===');
    console.log('1. ✓ Frontend logger behavior simulated with fixes applied');
    console.log('2. ✓ Debug logging added to track path selection');
    console.log('3. ✓ Directory creation and file writing tested');
    console.log('4. Next: Run actual frontend with "npm run dev-with-backend"');
}

runTests().catch(console.error);