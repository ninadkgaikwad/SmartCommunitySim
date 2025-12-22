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
    r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\SmartComSim",
]

for p in paths_to_add:
    if p not in sys.path and os.path.isdir(p):
        sys.path.append(p)

from Exp_Config_Module import *
from Exp_MPC_Controllers_Module import *
from Exp_MPC_RL_Helpers import *

from SmartComSim import SmartCommunity_Simulator as SC_Plant

###############################################################################################################
## Experiment Initial Data Creation - User Inputs
###############################################################################################################

COMMUNITY_TYPE_LIST = [
    "House",        # Single house case
    "Community",    # Multi-house community
]

GRID_TYPE_LIST = [
    "Off-Grid",
    "On-Grid",
]

CONTROLLER_TYPE_LIST = [
    "MPC",
    "RL-Training",
    "RL-Testing",
]

LOAD_DATA_INITIALIZE = True,  # True = Initialize Load Data ; False = Do not Initialize Load Data

WEATHER_DATA_INITIALIZE = True,  # True = Initialize Weather Data ; False = Do not Initialize Weather Data

###############################################################################################################
## Experiment Initial Data Creation - Processing
###############################################################################################################

for COMMUNITY_TYPE, GRID_TYPE, CONTROLLER_TYPE in product(COMMUNITY_TYPE_LIST, GRID_TYPE_LIST, CONTROLLER_TYPE_LIST):

    # Create Config for Initial Data Creation
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

    # Initializating Smart Community Simulator Object
    SC_Gainesville_Irma = SC_Plant.SmartCommunitySimulator(simulation_params, community_params, plant_initial_conditions, simulation_period, plant_dynamic_params, data_paths, result_filefolder_paths, simulation_ObservationActionSpace_Functions, simulation_RewardTerminateTruncate_Functions)

