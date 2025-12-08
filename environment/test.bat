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
SET MATLABROOT="C:\Program Files\MATLAB\R2024b"
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
