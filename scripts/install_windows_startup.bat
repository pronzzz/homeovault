@echo off
set "APP_NAME=HomeoVaultServer"
set "PROJECT_DIR=%~dp0.."
set "PYTHON_EXEC=python"

REM Check if python is available
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found in PATH. Please ensure Python is installed and added to PATH.
    pause
    exit /b 1
)

REM Resolve absolute path for PROJECT_DIR
pushd "%PROJECT_DIR%"
set "PROJECT_DIR=%CD%"
popd

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\%APP_NAME%.lnk"

echo Installing HomeoVault Auto-Launch for Windows...
echo Project Directory: %PROJECT_DIR%
echo Startup Folder: %STARTUP_FOLDER%

REM Create VBScript to generate shortcut
set "VBS_SCRIPT=%TEMP%\create_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%VBS_SCRIPT%"
echo sLinkFile = "%SHORTCUT_PATH%" >> "%VBS_SCRIPT%"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%VBS_SCRIPT%"
echo oLink.TargetPath = "python" >> "%VBS_SCRIPT%"
echo oLink.Arguments = "-m uvicorn backend.main:app --host 0.0.0.0 --port 8000" >> "%VBS_SCRIPT%"
echo oLink.WorkingDirectory = "%PROJECT_DIR%" >> "%VBS_SCRIPT%"
echo oLink.Save >> "%VBS_SCRIPT%"

REM Execute VBScript
cscript /nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

echo.
echo Success! HomeoVault shortcut created in Startup folder.
echo You can check it here: %SHORTCUT_PATH%
echo.
pause
