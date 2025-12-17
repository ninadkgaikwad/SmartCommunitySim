###############################################################################################################
## Import Desired Packages
###############################################################################################################

import sys
import os

import time
from itertools import product
import pandas as pd
import numpy as np

###############################################################################################################
## Import Custom Packages
###############################################################################################################

# Adding paths to find local modules

paths_to_add = [
    r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Modules",
    r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code",
]

for p in paths_to_add:
    if p not in sys.path and os.path.isdir(p):
        sys.path.append(p)

from Exp_Config_Module import *
from Exp_MPC_Controllers_Module import *

from SmartComSim import SmartCommunity_Simulator as SC_Plant

###############################################################################################################
## Experiment MPC - User Inputs
###############################################################################################################

# -------------------- Community Specifications -------------------- #
COMMUNITY_TYPE = "Community"  # "House", "Community",  

GRID_TYPE = "On-Grid"  #  "Off-Grid", "On-Grid",

CONTROLLER_TYPE = "MPC"  # "MPC", "RL-Training", "RL-Testing",

LOAD_DATA_INITIALIZE = False,  # True = Initialize Load Data ; False = Do not Initialize Load Data

WEATHER_DATA_INITIALIZE = False,  # True = Initialize Weather Data ; False = Do not Initialize Weather Data

# -------------------- MPC Controller - Parameters -------------------- #

MPC_HORIZON_HOURS = 24 # In Hours the Planning Horizon for MPC

# - Single House Off-Grid


# - Single House On-Grid


# - Multi House Off-Grid


# - Single House On-Grid


###############################################################################################################
## Experiment MPC - Processing
###############################################################################################################

# ----------------------------------------------------------------------------------------------------------- #
# Create Config for Initial Data Creation
# ----------------------------------------------------------------------------------------------------------- #

Config = Exp_Configuration_Generator(COMMUNITY_TYPE, GRID_TYPE, CONTROLLER_TYPE, LOAD_DATA_INITIALIZE, WEATHER_DATA_INITIALIZE)

# Get SmartSimCom Parameters from Config
simulation_params = Config["simulation_params"]
community_params = Config["community_params"]
plant_initial_conditions = Config["plant_initial_conditions"]
simulation_period = Config["simulation_period"]
plant_dynamic_params = Config["plant_dynamic_params"]
data_paths = Config["data_paths"]
result_filefolder_paths = Config["result_filefolder_paths"]
simulation_ObservationActionSpace_Functions = Config["simulation_ObservationActionSpace_Functions"]
simulation_RewardTerminateTruncate_Functions = Config["simulation_RewardTerminateTruncate_Functions"]

# ----------------------------------------------------------------------------------------------------------- #
# Initializating Smart Community Simulator Object
# ----------------------------------------------------------------------------------------------------------- #

SC_Gainesville_Irma = SC_Plant.SmartCommunitySimulator(simulation_params, community_params, plant_initial_conditions, simulation_period, plant_dynamic_params, data_paths, result_filefolder_paths, simulation_ObservationActionSpace_Functions, simulation_RewardTerminateTruncate_Functions)

# ----------------------------------------------------------------------------------------------------------- #
# Basic Computation
# ----------------------------------------------------------------------------------------------------------- #

# Getting Total Simulation Steps for MPC (We initialize SmartSimCom with weather/load data with DataLen+MPC_HORIZON_HOURS)
Total_Steps = SC_Gainesville_Irma.Simulation_Steps_Total

FileRes_Min = SC_Gainesville_Irma.simulation_params["FileRes"]

TimeSteps_MPC_Horizon = int(MPC_HORIZON_HOURS * (60/FileRes_Min))

N = TimeSteps_MPC_Horizon

Total_Simulation_Steps = Total_Steps - TimeSteps_MPC_Horizon

# Getting 
cp = SC_Gainesville_Irma.Community_Params

N_House  = int(cp["N_House"])
N_PV_Bat = int(cp["N_PV_Bat"])
N_Bat    = int(cp["N_Bat"])
N_PV     = int(cp["N_PV"])
N_None   = int(cp["N_None"])

N_PV_Total = N_PV_Bat + N_PV
N_Bat_Total = N_PV_Bat + N_Bat
# ----------------------------------------------------------------------------------------------------------- #
# Creating MPC_Parmeters
# ----------------------------------------------------------------------------------------------------------- #

if (COMMUNITY_TYPE == "House" and GRID_TYPE == "Off-Grid"):

    MPC_Parameters = {
        # ---------------- Time / horizon geometry ----------------
        # Number of MPC steps in prediction horizon.
        # Example: 96 = 24h with 15-minute resolution.
        "N_horizon": TimeSteps_MPC_Horizon,

        # How many simulation steps are between MPC optimizations.
        # 1 = re-solve every env.step(), >1 = move open-loop.
        "MPC_StepLengthUsed": 1,

        # Number of decision variables per house per step.
        # For your env — action dimension per house.
        "DecisionVariables_PerHouse": 14,
        "Initial_DecisionVariables": {

                                        # Thermal states (all houses)
                                        "T_wall": [0.0] * (N_House * N),
                                        "T_ave":  [0.0] * (N_House * N),
                                        "T_att":  [0.0] * (N_House * N),
                                        "T_im":   [0.0] * (N_House * N),

                                        # HVAC across all houses
                                        "U_ac":   [0.0] * (N_House * N),

                                        # Battery states & controls (PV+BAT + BAT)
                                        "E_bat":      [0.0] * (N_Bat_Total * N),
                                        "Gamma":      [0.0] * (N_Bat_Total * N),
                                        "theta_bat":  [0.0] * (N_Bat_Total * N),
                                        "f_on":       [0.0] * (N_House * N),
                                        "f_off":      [0.0] * (N_House * N),

                                        # PV variables (PV+BAT + PV)
                                        "g":    [0.0] * (N_PV_Total * N),

                                        # Loads and slack (all houses)
                                        "E_load": [0.0] * (N_House * N),
                                        "eps_h":  [0.0] * (N_House * N),
                                        "eps_l":  [0.0] * (N_House * N),

                                        # Grid (per timestep)
                                    },

        # ---------------- Cost weights (Λ terms) ----------------
        "Lambda_T": 1.0,   # indoor temperature comfort penalty
        "Lambda_E_l": 1.0,   # AC power/energy use
        "Lambda_Bat": 1.0,   # battery cycling / degradation
        "Lambda_E_cri": 1.0,   # reserved / load shedding
        "Lambda_Theta": 1.0,   # reserved
        "Lambda_G": 1.0,   # reserved (community metrics)
        "Lambda_PV": 1.0,   # slack penalty

        # Small slack variable penalty to soften constraints
        "Epsilon": 1e-8,

        # Plot open-loop MPC predictions? (debug)
        "OpenLoop_Plotting_Indicator": 0,
    }

elif (COMMUNITY_TYPE == "House" and GRID_TYPE == "On-Grid"):

    MPC_Parameters = {
        "N_horizon": TimeSteps_MPC_Horizon,
        "MPC_StepLengthUsed": 1,
        "DecisionVariables_PerHouse": 14, # Needs to change
        "Initial_DecisionVariables": {

                                        # Thermal states (all houses)
                                        "T_wall": [0.0] * (N_House * N),
                                        "T_ave":  [0.0] * (N_House * N),
                                        "T_att":  [0.0] * (N_House * N),
                                        "T_im":   [0.0] * (N_House * N),

                                        # HVAC across all houses
                                        "U_ac":   [0.0] * (N_House * N),

                                        # Battery states & controls (PV+BAT + BAT)
                                        "E_bat":      [0.0] * (N_Bat_Total * N),
                                        "Gamma":      [0.0] * (N_Bat_Total * N),

                                        # PV variables (PV+BAT + PV)
                                        "u_pv": [0.0] * (N_PV_Total * N),

                                        # Loads and slack (all houses)
                                        "eps_h":  [0.0] * (N_House * N),

                                        # Grid (per timestep)
                                        "E_g": [0.0] * N,
                                    },

        # ---------------- Cost weights (Λ terms) ----------------
        "Lambda_T": 1.0,   # indoor temperature comfort penalty
        "Lambda_E_l": 1.0,   # AC power/energy use
        "Lambda_Bat": 1.0,   # battery cycling / degradation
        "Lambda_E_cri": 1.0,   # reserved / load shedding
        "Lambda_Theta": 1.0,   # reserved
        "Lambda_G": 1.0,   # reserved (community metrics)
        "Lambda_PV": 1.0,   # slack penalty

        "Epsilon": 1e-8,
        "OpenLoop_Plotting_Indicator": 0,
    }

elif (COMMUNITY_TYPE == "Community" and GRID_TYPE == "Off-Grid"):

    MPC_Parameters = {
        "N_horizon": TimeSteps_MPC_Horizon,
        "MPC_StepLengthUsed": 1,
        "DecisionVariables_PerHouse": 14,
        "Initial_DecisionVariables": {

                                        # Thermal states (all houses)
                                        "T_wall": [0.0] * (N_House * N),
                                        "T_ave":  [0.0] * (N_House * N),
                                        "T_att":  [0.0] * (N_House * N),
                                        "T_im":   [0.0] * (N_House * N),

                                        # HVAC across all houses
                                        "U_ac":   [0.0] * (N_House * N),

                                        # Battery states & controls (PV+BAT + BAT)
                                        "E_bat":      [0.0] * (N_Bat_Total * N),
                                        "Gamma":      [0.0] * (N_Bat_Total * N),
                                        "theta_bat":  [0.0] * (N_Bat_Total * N),
                                        "f_on":       [0.0] * (N_House * N),
                                        "f_off":      [0.0] * (N_House * N),

                                        # PV variables (PV+BAT + PV)
                                        "g":    [0.0] * (N_PV_Total * N),

                                        # Loads and slack (all houses)
                                        "E_load": [0.0] * (N_House * N),
                                        "eps_h":  [0.0] * (N_House * N),
                                        "eps_l":  [0.0] * (N_House * N),

                                        # Grid (per timestep)
                                    },

        # ---------------- Cost weights (Λ terms) ----------------
        "Lambda_T": 1.0,   # indoor temperature comfort penalty
        "Lambda_E_l": 1.0,   # AC power/energy use
        "Lambda_Bat": 1.0,   # battery cycling / degradation
        "Lambda_E_cri": 1.0,   # reserved / load shedding
        "Lambda_Theta": 1.0,   # reserved
        "Lambda_G": 1.0,   # reserved (community metrics)
        "Lambda_PV": 1.0,   # slack penalty

        "Epsilon": 1e-8,
        "OpenLoop_Plotting_Indicator": 0,
    }

elif (COMMUNITY_TYPE == "Community" and GRID_TYPE == "On-Grid"):

    MPC_Parameters = {
        "N_horizon": TimeSteps_MPC_Horizon,
        "MPC_StepLengthUsed": 1,
        "DecisionVariables_PerHouse": 14, # Needs to change
        "Initial_DecisionVariables": {

                                        # Thermal states (all houses)
                                        "T_wall": [0.0] * (N_House * N),
                                        "T_ave":  [0.0] * (N_House * N),
                                        "T_att":  [0.0] * (N_House * N),
                                        "T_im":   [0.0] * (N_House * N),

                                        # HVAC across all houses
                                        "U_ac":   [0.0] * (N_House * N),

                                        # Battery states & controls (PV+BAT + BAT)
                                        "E_bat":      [0.0] * (N_Bat_Total * N),
                                        "Gamma":      [0.0] * (N_Bat_Total * N),

                                        # PV variables (PV+BAT + PV)
                                        "u_pv": [0.0] * (N_PV_Total * N),

                                        # Loads and slack (all houses)
                                        "eps_h":  [0.0] * (N_House * N),

                                        # Grid (per timestep)
                                        "E_g": [0.0] * N,
                                    },

        # ---------------- Cost weights (Λ terms) ----------------
        "Lambda_T": 1.0,   # indoor temperature comfort penalty
        "Lambda_E_l": 1.0,   # AC power/energy use
        "Lambda_Bat": 1.0,   # battery cycling / degradation
        "Lambda_E_cri": 1.0,   # reserved / load shedding
        "Lambda_Theta": 1.0,   # reserved
        "Lambda_G": 1.0,   # reserved (community metrics)
        "Lambda_PV": 1.0,   # slack penalty

        "Epsilon": 1e-8,
        "OpenLoop_Plotting_Indicator": 0,
    }


# ----------------------------------------------------------------------------------------------------------- #
## Simulation Loop
# ----------------------------------------------------------------------------------------------------------- #

# Track total MPC computation time
total_mpc_time = 0.0

# FOR LOOP: For each Simulation Step
for ii in range(20):  # Total_Simulation_Steps

    # -------------------------------
    # Print - Iteration Information
    # -------------------------------

    percent_done = 100.0 * (ii + 1) / Total_Simulation_Steps

    print(
        f"[Step {ii+1:6d}/{Total_Simulation_Steps}] "
        f"({percent_done:6.2f}%) | "
        f"Community={COMMUNITY_TYPE} | "
        f"Grid={GRID_TYPE} | "
        f"Controller={CONTROLLER_TYPE}"
    )

    # -------------------------------
    # Start timer for MPC computation
    # -------------------------------
    t0 = time.perf_counter()

    # Creating MPC_Parameters
    if (COMMUNITY_TYPE == "House" and GRID_TYPE == "Off-Grid"):

        Action, Initial_DecisionVariables, _, _ = SingleHouse_OffGrid_MPC_Controller(SC_Gainesville_Irma, MPC_Parameters)

    elif (COMMUNITY_TYPE == "House" and GRID_TYPE == "On-Grid"):

        Action, Initial_DecisionVariables, _, _  = SingleHouse_OnGrid_MPC_Controller(SC_Gainesville_Irma, MPC_Parameters)

    elif (COMMUNITY_TYPE == "Community" and GRID_TYPE == "Off-Grid"):

        Action, Initial_DecisionVariables, _, _  = MultiHouse_OffGrid_MPC_Controller(SC_Gainesville_Irma, MPC_Parameters)

    elif (COMMUNITY_TYPE == "Community" and GRID_TYPE == "On-Grid"):

        Action, Initial_DecisionVariables, _, _  = MultiHouse_OnGrid_MPC_Controller(SC_Gainesville_Irma, MPC_Parameters)

    
    # Warm Start
    MPC_Parameters["Initial_DecisionVariables"] = Initial_DecisionVariables

    # -------------------------------
    # End timer for MPC computation
    # -------------------------------
    t1 = time.perf_counter()
    total_mpc_time += (t1 - t0)

    # Step through the Environment based on the Controller Action
    SC_Gainesville_Irma.step(Action)

# ------------------------------------------------------------
# After the loop: compute average MPC time
# ------------------------------------------------------------
avg_mpc_time = total_mpc_time / Total_Simulation_Steps

print("\n===================== MPC TIMING SUMMARY =====================")
print(f"Total MPC Computation Time : {total_mpc_time:.6f} seconds")
print(f"Average MPC Time per Step  : {avg_mpc_time:.6f} seconds")
print(f"Total Simulation Steps     : {Total_Simulation_Steps}")
print("===============================================================\n")

# ----------------------------------------------------------------------------------------------------------- #
## Saving Sim Data
# ----------------------------------------------------------------------------------------------------------- #

SC_Gainesville_Irma.SmartCommunity_SimData_Func()

# ----------------------------------------------------------------------------------------------------------- #
## Saving Sim Performance Data
# ----------------------------------------------------------------------------------------------------------- #

Performance_DF = SC_Gainesville_Irma.SmartCommunity_PerformanceComputer_Func()

print("\n================= Performance DataFrame =================")
print(Performance_DF)
print("========================================================\n")

# ----------------------------------------------------------------------------------------------------------- #
## Plotting the Environment [default -> minimal = "Yes" -> 5 Plots per Simulation -> Research Paper Style]
# ----------------------------------------------------------------------------------------------------------- #

SC_Gainesville_Irma.render()

# ----------------------------------------------------------------------------------------------------------- #
## Closing the Environment
# ----------------------------------------------------------------------------------------------------------- #

SC_Gainesville_Irma.close()