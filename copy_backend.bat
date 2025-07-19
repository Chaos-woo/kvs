@echo off
echo === Copying backend executable for Tauri sidecar ===
echo.

set BACKEND_SRC=backend\dist\kvs_backend.exe
set TAURI_BIN_DIR=frontend\src-tauri\binaries\kvs_backend-x86_64-pc-windows-msvc.exe

echo Checking if backend executable exists...
if not exist %BACKEND_SRC% (
    echo ERROR: Backend executable not found at %BACKEND_SRC%
    echo Please build the backend first by running: python backend\build_backend.py
    exit /b 1
)

echo Creating Tauri binaries directory...
if not exist frontend\src-tauri\binaries (
    mkdir frontend\src-tauri\binaries
)

echo Copying backend executable to Tauri binaries directory...
copy %BACKEND_SRC% %TAURI_BIN_DIR%

echo.
echo === Copy complete! ===
echo.
