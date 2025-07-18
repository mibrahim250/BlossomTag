@echo off
echo 🌸 Building BlossomTag - Beautiful PDF Annotation Tool 🌸
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

REM Install/upgrade requirements directly
echo Installing requirements...
pip install --upgrade pip
pip install PySide6>=6.4.0
pip install PyMuPDF>=1.23.0
pip install Pillow>=9.0.0
pip install pytesseract>=0.3.10
pip install pyinstaller>=5.0.0

REM Build with PyInstaller using the spec file
echo.
echo 🔨 Building executable with PyInstaller...
pyinstaller --clean --noconfirm BlossomTag.spec

REM Check if build was successful
if exist "dist\BlossomTag.exe" (
    echo.
    echo ✅ Build successful! 
    echo 📁 Your executable is ready: dist\BlossomTag.exe
    echo 📊 File size: 
    dir dist\BlossomTag.exe | find "BlossomTag.exe"
    echo.
    echo 🎯 Features included:
    echo   • PDF annotation and highlighting
    echo   • Preset management 
    echo   • Tag search functionality
    echo   • High-quality PDF export
    echo   • No external dependencies needed
    echo.
    echo 🚀 Ready to distribute! The exe file is standalone.
    echo.
) else (
    echo.
    echo ❌ Build failed! Check the output above for errors.
    echo 💡 Common fixes:
    echo   • Make sure all .py files are in the same directory
    echo   • Check that all imports work: python main.py
    echo   • Try: pip install --upgrade pyinstaller
    echo.
)

echo.
echo 🌸 Build process complete! 🌸
pause