@echo off
REM Quick Install Script for cycleuser/Skills (Windows)
REM Usage: curl -sSL https://raw.githubusercontent.com/cycleuser/Skills/main/quick-install.bat | cmd

setlocal enabledelayedexpansion

set REPO_URL=https://github.com/cycleuser/Skills
set INSTALL_DIR=%USERPROFILE%\.opencode\skills

echo ========================================
echo   Skills Installer
echo ========================================
echo.

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is required but not installed.
    exit /b 1
)

REM Create installation directory
echo Creating installation directory: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Download installer
echo Downloading installer...
curl -sSL "%REPO_URL%/raw/main/install.py" -o %TEMP%\skills_install.py

REM Run installer
echo Running installer...
python %TEMP%\skills_install.py install

REM Cleanup
del /f %TEMP%\skills_install.py 2>nul

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Skills installed to: %INSTALL_DIR%
echo.
echo Quick Start:
echo   /skills              - List all skills
echo   /skill ^<name^>        - Load a skill
echo.
echo For more info: https://github.com/cycleuser/Skills

endlocal