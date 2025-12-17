###############################################################################################################
## Import Desired Packages
###############################################################################################################

import sys
import os
from pathlib import Path

import time
from itertools import product
import pandas as pd
import numpy as np

###############################################################################################################
## Import Custom Packages
###############################################################################################################

# Adding paths to find local modules

paths_to_add = [
    r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_FullRun_Modules",
]

for p in paths_to_add:
    if p not in sys.path and os.path.isdir(p):
        sys.path.append(p)

from Exp_RL_Trainer_FullRun_Module import *

###############################################################################################################
## Experiment RL Trainer - User Inputs
###############################################################################################################

# -------------------- Community Specifications -------------------- #
COMMUNITY_TYPE_LIST = ["House", "Community"]
GRID_TYPE_LIST = ["Off-Grid", "On-Grid"]

# -------------------- Output Folder (USER-DEFINED) -------------------- #
OUTPUT_DIR = Path(r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------- Output File Name (DYNAMIC) -------------------- #
csv_name = "Exp_RL_Trainer_FullRun_AvgTime_Results.csv"
csv_path = OUTPUT_DIR / csv_name

###############################################################################################################
## Run Cartesian Product Experiments + Collect Results
###############################################################################################################

results = []

for Community_Type, Grid_Type in product(COMMUNITY_TYPE_LIST, GRID_TYPE_LIST):
    
    print(f"\nRunning Exp_RL_Trainer_FullRun for Community_Type={Community_Type}, Grid_Type={Grid_Type} ...")

    t0 = time.perf_counter()
    try:
        RL_Trainer_Total_Time, Total_Steps = Exp_RL_Trainer_FullRun(Community_Type, Grid_Type)
        RL_Train_Time = RL_Trainer_Total_Time
        RL_Avg_Train_Time = RL_Trainer_Total_Time/Total_Steps
        status = "OK"
        err = ""
    except Exception as e:
        RL_Train_Time = np.nan
        RL_Avg_Train_Time = np.nan
        status = "ERROR"
        err = repr(e)

    wall_time_s = time.perf_counter() - t0

    results.append(
        {
            "Community_Type": Community_Type,
            "Grid_Type": Grid_Type,
            "RL_Total_Train_Time_s": RL_Train_Time,      # returned by your function
            "RL_Avg_Train_Time_s": RL_Avg_Train_Time,  # measured around the call
            "Status": status,
            "Error": err,
        }
    )

# Create DataFrame
df = pd.DataFrame(results)

# Save CSV
df.to_csv(csv_path, index=False)

print("\n================ RESULTS SAVED ================")
print(df)
print(f"\nSaved CSV to: {csv_path}")
