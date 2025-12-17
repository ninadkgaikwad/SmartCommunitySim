#!/usr/bin/env bash

echo "============================================================"
echo " Creating SmartComSim RL Conda Environment (Python 3.12.3)"
echo "============================================================"

# -------------------------------
# User-configurable paths
# -------------------------------

# Path to your environment YAML file
ENV_YAML="SmartSimCom_Env_File.yml"

# Path to your MATLAB installation
# Example:
# MATLABROOT="/usr/local/MATLAB/R2024a"
# MATLABROOT="/Applications/MATLAB_R2024a.app"
MATLABROOT="/usr/local/MATLAB/R2024b"

echo ""
echo "Using environment file:     $ENV_YAML"
echo "Using MATLAB root folder:   $MATLABROOT"
echo ""

# -------------------------------
# 1. Create conda environment
# -------------------------------

echo "Creating the conda environment..."
conda env create -f "$ENV_YAML"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create environment."
    exit 1
fi

echo ""
echo "Environment smartcomsim_rl created successfully."
echo ""

# -------------------------------
# 2. Activate environment
# -------------------------------

# Enable conda in this shell session
eval "$(conda shell.bash hook)"

echo "Activating environment SmartComSim_Base..."
conda activate SmartComSim_Base

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate environment."
    exit 1
fi

echo ""
echo "Environment activated successfully."
echo ""

# -------------------------------
# 3. Install MATLAB Engine
# -------------------------------

echo "Installing MATLAB Engine for Python..."
cd "$MATLABROOT/extern/engines/python" || {
    echo "ERROR: Cannot find MATLAB engine directory."
    exit 1
}

python -m pip install .
if [ $? -ne 0 ]; then
    echo "ERROR: MATLAB Engine installation failed."
    exit 1
fi

echo ""
echo "MATLAB Engine installed successfully."
echo ""

# -------------------------------
# 4. Verify installation
# -------------------------------

echo "Verifying Python packages..."

python - <<EOF
import sys
print("Python version:", sys.version)

import numpy, pandas, matplotlib, casadi
print("NumPy:     ", numpy.__version__)
print("Pandas:    ", pandas.__version__)
print("Matplotlib:", matplotlib.__version__)
print("CasADi:    ", casadi.__version__)

import matlab.engine
print("MATLAB Engine detected successfully.")
EOF

echo ""
echo "============================================================"
echo " SmartComSim RL Environment Setup Complete!"
echo " Activate with:"
echo "      conda activate SmartComSim_Base"
echo "============================================================"
