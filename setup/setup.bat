@echo off
setlocal

echo ==========================================
echo   Mainframe Setup Script
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found.
    echo [*] Downloading Python installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile '%TEMP%\python-installer.exe'"
    echo [*] Running Python installer...
    start /wait %TEMP%\python-installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1
    echo [*] Python installed. Please restart your terminal and run setup.bat again.
    pause
    exit /b 0
)

echo [+] Python found.
python --version

REM Check if pip is installed
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] pip not found. Installing pip...
    python -m ensurepip --default-pip
)

echo [+] pip found.

REM Upgrade pip
echo [*] Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo [*] Installing Python dependencies...
python -m pip install -r requirements.txt

REM Install Impacket scripts
echo [*] Installing Impacket...
python -m pip install impacket

echo [*] Downloading Impacket scripts...
if not exist "core\impacket_scripts" mkdir core\impacket_scripts
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/fortra/impacket/master/impacket/examples/psexec.py' -OutFile 'core\impacket_scripts\psexec.py'"
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/fortra/impacket/master/impacket/examples/wmiexec.py' -OutFile 'core\impacket_scripts\wmiexec.py'"

REM Check for Chocolatey
echo [*] Checking for Chocolatey...
where choco >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Chocolatey not found. Installing Chocolatey...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    echo [*] Chocolatey installed. Please restart your terminal and run setup.bat again.
    pause
    exit /b 0
)

echo [+] Chocolatey found.

REM Install external tools via Chocolatey
echo [*] Installing external tools via Chocolatey...

echo [*] Installing Nmap...
choco install nmap -y

echo [*] Installing Hashcat...
choco install hashcat -y

echo [*] Installing Metasploit...
choco install metasploit -y

REM Check for Node.js (for Vercel image logger)
echo [*] Checking for Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Node.js not found. Please install Node.js from https://nodejs.org/
    echo     The Vercel image logger requires Node.js to deploy.
) else (
    echo [+] Node.js found.
    
    REM Check for Vercel CLI
    echo [*] Checking for Vercel CLI...
    vercel --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [*] Installing Vercel CLI...
        npm install -g vercel
    ) else (
        echo [+] Vercel CLI found.
    )
)

REM Check for Go (for Sherlock and PhoneInfoga)
echo [*] Checking for Go...
go version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Go not found. Please install Go from https://golang.org/dl/
    echo     Sherlock and PhoneInfoga require Go to run.
) else (
    echo [+] Go found.
    
    REM Install Sherlock
    echo [*] Installing Sherlock...
    go install github.com/sundowndev/phoneinfoga@latest 2>nul
    go install github.com/sherlock-project/sherlock@latest 2>nul
)

REM Verify installation
echo.
echo ==========================================
echo   Setup Complete
echo ==========================================
echo [*] Run the tool with: python mainframe.py
echo.
pause
