###############################################################################################################
## RL Testing Script (SAC) for SmartCommunitySimulator
###############################################################################################################

import sys
import os

import time
import numpy as np
import pandas as pd

from stable_baselines3 import SAC

###############################################################################################################
## Import Custom Packages
###############################################################################################################

# Adding paths to find local modules
paths_to_add = [
    r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Modules",
    r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\SmartComSim",
]

for p in paths_to_add:
    if p not in sys.path and os.path.isdir(p):
        sys.path.append(p)

from Exp_Modules.Exp_Config_Module import *
from Exp_Modules.Exp_MPC_RL_Helpers import *
from Exp_Modules.Exp_RL_Utilities_Module import *  # you can plug callbacks/utilities here if you want

from SmartComSim import SmartCommunity_Simulator as SC_Plant

###############################################################################################################
## Experiment RL Testing - User Inputs
###############################################################################################################

# -------------------- Community Specifications -------------------- #
COMMUNITY_TYPE   = "House"      # "House", "Community"
GRID_TYPE        = "Off-Grid"   # "Off-Grid", "On-Grid"
CONTROLLER_TYPE  = "RL-Testing" # IMPORTANT: "MPC", "RL-Training", "RL-Testing"

LOAD_DATA_INITIALIZE    = False
WEATHER_DATA_INITIALIZE = False

# Planning Horizon for RL
RL_HORIZON_HOURS = 24

# Seed for deterministic reset (optional)
RL_TEST_SEED = 123

# This should match the RESULTS_ROOT + RL folder structure from training
RL_MODEL_ROOT = r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\RL\Trainer"

# Name of the RL run (must match training)
rl_run_name  = f"RL_SAC_{COMMUNITY_TYPE}_{GRID_TYPE}"

# Path to the saved final SAC model (from training script)
model_path = os.path.join(RL_MODEL_ROOT, "RL", rl_run_name, "sac_hems_final.zip")

###############################################################################################################
## Build Config and Initialize Environment
###############################################################################################################

# --------------------------------------------------
# 1) Build experiment configuration
# --------------------------------------------------
Config = Exp_Configuration_Generator(
    COMMUNITY_TYPE,
    GRID_TYPE,
    CONTROLLER_TYPE,
    LOAD_DATA_INITIALIZE,
    WEATHER_DATA_INITIALIZE,
)

# Extract SmartComSim parameters from Config
simulation_params                           = Config["simulation_params"]
community_params                            = Config["community_params"]
plant_initial_conditions                    = Config["plant_initial_conditions"]
simulation_period                           = Config["simulation_period"]
plant_dynamic_params                        = Config["plant_dynamic_params"]
data_paths                                  = Config["data_paths"]
result_filefolder_paths                     = Config["result_filefolder_paths"]
simulation_ObservationActionSpace_Functions = Config["simulation_ObservationActionSpace_Functions"]
simulation_RewardTerminateTruncate_Functions = Config["simulation_RewardTerminateTruncate_Functions"]

# --------------------------------------------------
# 2) Create a single SmartCommunitySimulator instance
# --------------------------------------------------
SC_Gainesville_Irma = SC_Plant.SmartCommunitySimulator(
    simulation_params=simulation_params,
    community_params=community_params,
    plant_initial_conditions=plant_initial_conditions,
    simulation_period=simulation_period,
    plant_dynamic_params=plant_dynamic_params,
    data_paths=data_paths,
    result_filefolder_paths=result_filefolder_paths,
    simulation_ObservationActionSpace_Functions=simulation_ObservationActionSpace_Functions,
    simulation_RewardTerminateTruncate_Functions=simulation_RewardTerminateTruncate_Functions,
)

# Reset environment at the start of the test rollout
# observation, info = env.reset(seed=RL_TEST_SEED)

###############################################################################################################
## Load Trained SAC Policy
###############################################################################################################

if not os.path.isfile(model_path):
    raise FileNotFoundError(f"Trained SAC model not found at: {model_path}")

print("\n===================== RL TESTING SETUP =====================")
print(f"Community Type         : {COMMUNITY_TYPE}")
print(f"Grid Type              : {GRID_TYPE}")
print(f"Controller Type        : {CONTROLLER_TYPE}")
print(f"Using model            : {model_path}")
print("============================================================\n")

model = SAC.load(model_path)  # env not strictly required for predict()

###############################################################################################################
## RL Rollout Loop (Deterministic Policy) + Timing
###############################################################################################################

# Getting Total Simulation Steps for MPC (We initialize SmartSimCom with weather/load data with DataLen+MPC_HORIZON_HOURS)
Total_Steps = SC_Gainesville_Irma.Simulation_Steps_Total

FileRes_Min = SC_Gainesville_Irma.simulation_params["FileRes"]

TimeSteps_MPC_Horizon = int(RL_HORIZON_HOURS * (60/FileRes_Min))

Total_Simulation_Steps = Total_Steps - TimeSteps_MPC_Horizon

total_rl_time = 0.0
Total_Simulation_Steps = 0  # actual steps taken

for ii in range(Total_Simulation_Steps):

    # -------------------------------
    # Start timer for RL policy computation
    # -------------------------------
    t0 = time.perf_counter()

    # SAC policy: deterministic action for evaluation
    action, _ = model.predict(observation, deterministic=True)

    # -------------------------------
    # End timer for RL policy computation
    # -------------------------------
    t1 = time.perf_counter()
    total_rl_time += (t1 - t0)

    # Step through environment
    observation, reward, terminated, truncated, info = SC_Gainesville_Irma.step(action)
    Total_Simulation_Steps += 1

    # Stop if episode ends (due to internal termination or truncation)
    if terminated or truncated:
        break

# ------------------------------------------------------------
# After the loop: compute average RL policy time
# ------------------------------------------------------------
if Total_Simulation_Steps > 0:
    avg_rl_time = total_rl_time / Total_Simulation_Steps
else:
    avg_rl_time = 0.0

print("\n===================== RL POLICY TIMING SUMMARY =====================")
print(f"Total RL Policy Computation Time : {total_rl_time:.6f} seconds")
print(f"Average RL Time per Step         : {avg_rl_time:.6f} seconds")
print(f"Total Simulation Steps (executed): {Total_Simulation_Steps}")
print("====================================================================\n")

###############################################################################################################
## Saving Sim Data
###############################################################################################################

SC_Gainesville_Irma.SmartCommunity_SimData_Func()

###############################################################################################################
## Saving Sim Performance Data
###############################################################################################################

Performance_DF = SC_Gainesville_Irma.SmartCommunity_PerformanceComputer_Func()

print("\n================= Performance DataFrame (RL) =================")
print(Performance_DF)
print("==============================================================\n")

###############################################################################################################
## Plotting the Environment [default -> minimal = "Yes"]
###############################################################################################################

SC_Gainesville_Irma.render()  # default minimal="Yes" in your render implementation

###############################################################################################################
## Closing the Environment
###############################################################################################################

SC_Gainesville_Irma.close()

print("Environment closed. RL testing script completed.")
