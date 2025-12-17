@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ===============================================================
REM  research_mode.bat
REM
REM  Purpose:
REM   - Prepare Windows for research workloads
REM   - Reduce background RAM / thread / handle pressure
REM   - Set numerical library thread limits
REM
REM  SAFE GUARANTEES:
REM   - Does NOT disable Windows Defender
REM   - Does NOT disable svchost / core OS services
REM   - Does NOT remove GPU drivers
REM   - Explorer restart is OPTIONAL
REM ===============================================================

echo.
echo ===============================================================
echo   RESEARCH MODE - SYSTEM PREPARATION
echo ===============================================================
echo.

REM -------------------- THREAD LIMIT SELECTION --------------------
echo Choose thread limit for THIS session:
echo   [1] 4   threads  (very safe, low memory)
echo   [2] 8   threads  (RECOMMENDED)
echo   [3] 16  threads  (heavy linear algebra)
echo.

set /p TLCHOICE=Enter choice (1/2/3) [default=2]:

if "%TLCHOICE%"=="3" (
    set TLVAL=16
) else if "%TLCHOICE%"=="1" (
    set TLVAL=4
) else (
    set TLVAL=8
)

REM Apply thread limits
set OMP_NUM_THREADS=%TLVAL%
set MKL_NUM_THREADS=%TLVAL%
set OPENBLAS_NUM_THREADS=%TLVAL%
set NUMEXPR_NUM_THREADS=%TLVAL%
set VECLIB_MAXIMUM_THREADS=%TLVAL%

echo.
echo Thread limits set to %TLVAL% threads:
echo   OMP_NUM_THREADS=%OMP_NUM_THREADS%
echo   MKL_NUM_THREADS=%MKL_NUM_THREADS%
echo   OPENBLAS_NUM_THREADS=%OPENBLAS_NUM_THREADS%
echo   NUMEXPR_NUM_THREADS=%NUMEXPR_NUM_THREADS%
echo.

REM -------------------- MEMORY BEFORE -----------------------------
echo [Before] Memory status:
powershell -NoProfile -Command ^
  "$os=Get-CimInstance Win32_OperatingSystem; " ^
  "$total=[math]::Round($os.TotalVisibleMemorySize/1MB,1); " ^
  "$free=[math]::Round($os.FreePhysicalMemory/1MB,1); " ^
  "Write-Host ('  Total RAM (GB): ' + $total); " ^
  "Write-Host ('  Free  RAM (GB): ' + $free);"
echo.

REM -------------------- PROCESS KILL HELPER ------------------------
set KILL=taskkill /F /IM

echo Cleaning background processes...

REM -------------------- BROWSERS ----------------------------------
choice /M "Close Chrome and Edge (recommended before experiments)?"
if errorlevel 2 goto SKIP_BROWSERS
%KILL% chrome.exe >nul 2>&1
%KILL% msedge.exe >nul 2>&1
echo Browsers closed.
echo.
:SKIP_BROWSERS

REM -------------------- CLOUD / COMMUNICATION ---------------------
%KILL% Dropbox.exe >nul 2>&1
%KILL% OneDrive.exe >nul 2>&1
%KILL% Teams.exe >nul 2>&1
%KILL% ms-teams.exe >nul 2>&1
%KILL% Discord.exe >nul 2>&1
%KILL% Slack.exe >nul 2>&1
%KILL% PhoneExperienceHost.exe >nul 2>&1

REM -------------------- DELL TELEMETRY / SUPPORT ------------------
%KILL% SupportAssistAgent.exe >nul 2>&1
%KILL% SupportAssist.exe >nul 2>&1
%KILL% DellDataVault.exe >nul 2>&1
%KILL% DellDataVaultCollector.exe >nul 2>&1
%KILL% DDVDataCollector.exe >nul 2>&1
%KILL% DellAnalytics.exe >nul 2>&1
%KILL% Dell.TechHub.exe >nul 2>&1
%KILL% DellInstrumentation.exe >nul 2>&1
%KILL% Dell.D3.WinSvc.exe >nul 2>&1

REM -------------------- NVIDIA OVERLAY (NOT DRIVERS) --------------
%KILL% NVIDIA Share.exe >nul 2>&1
%KILL% nvsphelper64.exe >nul 2>&1

echo Background cleanup complete.
echo.

REM -------------------- OPTIONAL: RESTART EXPLORER ----------------
choice /M "Restart Windows Explorer (safe)?"
if errorlevel 2 goto SKIP_EXPLORER
echo Restarting Explorer...
taskkill /F /IM explorer.exe >nul 2>&1
start explorer.exe
echo Explorer restarted.
echo.
:SKIP_EXPLORER

REM -------------------- OPTIONAL: CLOSE SEARCH UI -----------------
choice /M "Close Windows Search UI (SearchHost/SearchApp)?"
if errorlevel 2 goto SKIP_SEARCH
%KILL% SearchHost.exe >nul 2>&1
%KILL% SearchApp.exe >nul 2>&1
echo Search UI closed.
echo.
:SKIP_SEARCH

REM -------------------- MEMORY AFTER ------------------------------
echo [After] Memory status:
powershell -NoProfile -Command ^
  "$os=Get-CimInstance Win32_OperatingSystem; " ^
  "$total=[math]::Round($os.TotalVisibleMemorySize/1MB,1); " ^
  "$free=[math]::Round($os.FreePhysicalMemory/1MB,1); " ^
  "Write-Host ('  Total RAM (GB): ' + $total); " ^
  "Write-Host ('  Free  RAM (GB): ' + $free);"
echo.

echo ===============================================================
echo RESEARCH MODE READY
echo
echo - Thread limit: %TLVAL%
echo - Launch Anaconda Prompt / CMD from THIS window
echo - Activate Conda env and run experiments
echo ===============================================================
echo.
pause
endlocal
