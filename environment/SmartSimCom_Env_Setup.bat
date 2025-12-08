@echo off
echo ============================================================
echo   Creating SmartComSim RL Conda Environment (Python 3.12.3)
echo ============================================================

REM --------- SET PATHS HERE ------------------------------------
REM Path to your environment YAML file:
SET ENV_YAML="SmartSimCom_Env_File.yml"

REM Path to your MATLAB root folder (CHANGE THIS):
REM Example: SET MATLABROOT="C:\Program Files\MATLAB\R2024a"
SET MATLABROOT="C:\Program Files\MATLAB\R2024b"
REM --------------------------------------------------------------

echo.
echo Using environment file: %ENV_YAML%
echo Using MATLAB root: %MATLABROOT%
echo.

REM --------- STEP 1: Create conda environment -------------------
echo Creating the conda environment...
CALL conda env create -f %ENV_YAML%
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create environment.
    pause
    exit /b
)

echo.
echo Environment smartcomsim_rl created successfully.
echo.

REM --------- STEP 2: Activate environment ------------------------
echo Activating environment SmartComSim_Base...
CALL conda activate SmartComSim_Base
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate environment.
    pause
    exit /b
)

echo.
echo Environment activated successfully.
echo.

REM --------- STEP 3: Install MATLAB Engine -----------------------
echo Installing MATLAB Engine for Python...
cd "%MATLABROOT%\extern\engines\python"

python -m pip install .
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: MATLAB Engine installation failed.
    pause
    exit /b
)

echo.
echo MATLAB Engine installed successfully.
echo.

REM --------- STEP 4: Verify installation -------------------------
echo Verifying imports...

python - <<EOF
import sys
print("Python version:", sys.version)
import numpy, pandas, matplotlib, casadi
print("NumPy:", numpy.__version__)
print("Pandas:", pandas.__version__)
print("Matplotlib:", matplotlib.__version__)
print("CasADi:", casadi.__version__)
import matlab.engine
print("MATLAB Engine detected successfully.")
EOF

echo.
echo ============================================================
echo   SmartComSim RL Environment Setup Complete!
echo   Activate with:
echo        conda activate smartcomsim_rl
echo ============================================================

pause
