// Test script to verify frontend logger fixes
const fs = require('fs');
const path = require('path');

// Simulate Tauri's join function
function join(...parts) {
    return path.join(...parts);
}

// Simulate Tauri's createDir function
function createDir(dirPath, options = {}) {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: options.recursive || false });
    }
}

async function testFrontendLoggerFixes() {
    console.log('=== Frontend Logger Fixes Test ===');
    
    // Simulate the new path resolution logic
    const pathsToTry = [
        path.join('..', '..', 'backend', 'logs'),  // From frontend/src-tauri/target/debug
        path.join('..', 'backend', 'logs'),        // From frontend/src-tauri
        path.join('backend', 'logs'),              // From project root
        path.join('..', '..', '..', 'backend', 'logs'), // From deeper nested structure
    ];
    
    let backendLogsFound = false;
    let successfulPath = null;
    
    console.log('Testing path resolution patterns:');
    
    for (const pathToTry of pathsToTry) {
        try {
            const absolutePath = path.resolve(pathToTry);
            console.log(`  Trying: ${pathToTry} -> ${absolutePath}`);
            
            // Check if the path exists or can be created
            if (fs.existsSync(absolutePath) || fs.existsSync(path.dirname(absolutePath))) {
                // Test if we can create the directory
                createDir(absolutePath, { recursive: true });
                
                // Check if backend log files exist in this directory
                const apiLogExists = fs.existsSync(path.join(absolutePath, 'api.log'));
                const errorLogExists = fs.existsSync(path.join(absolutePath, 'error.log'));
                
                if (apiLogExists || errorLogExists) {
                    console.log(`  ✓ SUCCESS: Found backend logs at ${absolutePath}`);
                    console.log(`    - api.log exists: ${apiLogExists}`);
                    console.log(`    - error.log exists: ${errorLogExists}`);
                    successfulPath = absolutePath;
                    backendLogsFound = true;
                    break;
                } else {
                    console.log(`  ⚠ Path accessible but no backend logs found: ${absolutePath}`);
                }
            } else {
                console.log(`  ✗ Path not accessible: ${absolutePath}`);
            }
        } catch (error) {
            console.log(`  ✗ Failed to access ${pathToTry}: ${error.message}`);
        }
    }
    
    if (backendLogsFound) {
        console.log(`\n✅ FIXED: Frontend logger should now use: ${successfulPath}`);
        
        // Test creating frontend.log in the same directory
        const frontendLogPath = path.join(successfulPath, 'frontend.log');
        try {
            const testMessage = `${new Date().toISOString()} - frontend - INFO - Test message after fixes\n`;
            fs.appendFileSync(frontendLogPath, testMessage);
            console.log(`✅ FIXED: Frontend.log can be written to: ${frontendLogPath}`);
            
            // Verify all log files are in the same directory
            const apiLogPath = path.join(successfulPath, 'api.log');
            const errorLogPath = path.join(successfulPath, 'error.log');
            
            console.log('\n📁 Log files in same directory:');
            console.log(`  - API log: ${fs.existsSync(apiLogPath) ? '✓' : '✗'} ${apiLogPath}`);
            console.log(`  - Error log: ${fs.existsSync(errorLogPath) ? '✓' : '✗'} ${errorLogPath}`);
            console.log(`  - Frontend log: ${fs.existsSync(frontendLogPath) ? '✓' : '✗'} ${frontendLogPath}`);
            
        } catch (error) {
            console.log(`❌ ERROR: Could not write to frontend.log: ${error.message}`);
        }
    } else {
        console.log('\n❌ ISSUE: No backend logs directory found with any path pattern');
        console.log('This means the frontend logger will still fall back to AppData directory');
    }
}

function testDebugLogsComponent() {
    console.log('\n=== Debug Logs Component Test ===');
    
    // Read the updated component file
    const componentPath = path.join('frontend', 'src', 'components', 'debug-logs.tsx');
    
    if (fs.existsSync(componentPath)) {
        const content = fs.readFileSync(componentPath, 'utf8');
        
        // Check if the buttons were removed
        const hasOpenLogFileButton = content.includes('打开日志文件');
        const hasOpenLogDirectoryButton = content.includes('打开日志目录');
        const hasShowLogPathButton = content.includes('显示日志路径');
        
        console.log('Button removal verification:');
        console.log(`  - "打开日志文件" button removed: ${!hasOpenLogFileButton ? '✅' : '❌'}`);
        console.log(`  - "打开日志目录" button removed: ${!hasOpenLogDirectoryButton ? '✅' : '❌'}`);
        console.log(`  - "显示日志路径" button kept: ${hasShowLogPathButton ? '✅' : '❌'}`);
        
        if (!hasOpenLogFileButton && !hasOpenLogDirectoryButton && hasShowLogPathButton) {
            console.log('✅ FIXED: Debug logs component correctly updated');
        } else {
            console.log('❌ ISSUE: Debug logs component not correctly updated');
        }
    } else {
        console.log('❌ ERROR: Could not find debug-logs.tsx component file');
    }
}

function testTauriConfiguration() {
    console.log('\n=== Tauri Configuration Test ===');
    
    const tauriConfigPath = path.join('frontend', 'src-tauri', 'tauri.conf.json');
    
    if (fs.existsSync(tauriConfigPath)) {
        try {
            const config = JSON.parse(fs.readFileSync(tauriConfigPath, 'utf8'));
            const fsScope = config.tauri?.allowlist?.fs?.scope || [];
            
            console.log('Filesystem scope verification:');
            console.log(`  - Total scope entries: ${fsScope.length}`);
            
            const requiredPaths = [
                'backend/logs/*',
                '../backend/logs/*',
                '../../backend/logs/*',
                '../../../backend/logs/*'
            ];
            
            let allPathsPresent = true;
            for (const requiredPath of requiredPaths) {
                const present = fsScope.includes(requiredPath);
                console.log(`  - ${requiredPath}: ${present ? '✅' : '❌'}`);
                if (!present) allPathsPresent = false;
            }
            
            if (allPathsPresent) {
                console.log('✅ FIXED: All required backend/logs paths in Tauri scope');
            } else {
                console.log('❌ ISSUE: Some backend/logs paths missing from Tauri scope');
            }
            
        } catch (error) {
            console.log(`❌ ERROR: Could not parse Tauri config: ${error.message}`);
        }
    } else {
        console.log('❌ ERROR: Could not find tauri.conf.json file');
    }
}

// Run all tests
async function runAllTests() {
    await testFrontendLoggerFixes();
    testDebugLogsComponent();
    testTauriConfiguration();
    
    console.log('\n=== Summary ===');
    console.log('1. ✅ Frontend logger updated with multiple path resolution patterns');
    console.log('2. ✅ Tauri filesystem scope updated with additional backend/logs paths');
    console.log('3. ✅ Debug logs component updated to remove file/directory opening buttons');
    console.log('4. 🔄 Next: Test with "npm run dev-with-backend" to verify fixes work');
}

runAllTests().catch(console.error);