@echo off
echo ============================================
echo   Python 3.10 Virtual Environment Installer
echo ============================================

REM Check if Python 3.10 is available
py -3.10 --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo.
    echo [ERROR] Python 3.10 is not installed or not available as "py -3.10".
    echo Please install Python 3.10 from https://www.python.org/downloads/
    echo and make sure it is added to PATH.
    echo.
    pause
    exit /b 1
)

echo [INFO] Python 3.10 found. Proceeding...

REM Create virtual environment
py -3.10 -m venv venv

REM Activate virtual environment
call venv\Scripts\activate

REM Install required packages
echo [INFO] Installing rvc dependencies...
pip install rvc-python
pip install torch==2.1.1+cu118 torchaudio==2.1.1+cu118 --index-url https://download.pytorch.org/whl/cu118

REM Upgrade pip and install wheel + setuptools first
echo [INFO] Upgrading pip, wheel, setuptools...
pip install --upgrade pip wheel setuptools

REM Install required packages
echo [INFO] Installing other dependencies...
pip install openai
pip install pillow
pip install mss
pip install imagehash
pip install librosa
pip install sounddevice

echo.
echo ============================================
echo   Environment setup complete!
echo   To activate later: call venv\Scripts\activate
echo ============================================
pause
