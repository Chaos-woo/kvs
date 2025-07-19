@echo off
echo === KVs builder ===
echo.

echo 1. install dependency...
cd frontend
call npm install
cd ..
cd backend
pip install -r requirements.txt
pip install pyinstaller
cd ..
echo.
echo 2. package backend...
cd backend
python build_backend.py
cd ..

echo.
echo 3. copy backend executable for Tauri...
call copy_backend.bat

echo.
echo 4. package frontend...
cd frontend
call npm run tauri build
cd ..

echo.
echo === build complete! ===
echo to: frontend\src-tauri\target\release\bundle\
echo.
pause
