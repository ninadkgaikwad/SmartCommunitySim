###############################################################################################################
## Import Desired Packages
###############################################################################################################
import sys
import os

import matlab.engine
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import matplotlib.pyplot as plt

import scipy.io as sio

###############################################################################################################
## Import Desired Packages - From Smart Community Package
###############################################################################################################

# Add the parent directory (Code) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from SmartComSim import SmartCommunity_Simulator as SC_Plant

from SmartComSim import SmartCommunity_DefaultControllers as SC_DefCon

###############################################################################################################
## Smart Community Simulator Class - User Inputs
###############################################################################################################

# -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
simulation_params = {
    "Simulation_Name": "OnGrid_Baseline",
    "FileRes": 10.0,  # in Minutes
    "SmartCommunity_ControllerType": 1,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
    "Simulation_ModeType": 1,  # 0 - Off-Grid, 1 - On-Grid
    "OffGrid_Simulation_ModeType": 0,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
    "SimulationType": 0,  # Single Large House Simulation type
    "LoadDataType": 2,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
    "WeatherDataType": 2,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
    "Single_House_Plotting_Index": 1,  # House index for single-house plotting
    "ObservationSpace_Type": "Default",  # Default ; User-Defined
    "ActionSpace_Type": "Default",  # Default ; User-Defined
}

# -------------------- Community Specification -------------------- #
community_params = {
    "N_PV_Bat": 1,  # Houses with both PV and Battery
    "N_PV": 1,  # Houses with just PV
    "N_Bat": 1,  # Houses with just Battery
    "N_None": 1,  # Houses with neither PV nor Battery
}

# -------------------- Plant Initial Conditions -------------------- #
plant_initial_conditions = {
    "T_AC_Base": 24.0,  # Base AC Temperature
    "T_House_Variance": 0.5,  # Variance in house temperature
    "N1": 1.0,  # User-defined Battery Max Charging Factor
}

# -------------------- Simulation Period Specification -------------------- #
simulation_period = {
    "StartYear": 2017,
    "StartMonth": 9,
    "StartDay": 11,
    "StartTime": 0.0,
    "EndYear": 2017,
    "EndMonth": 9,
    "EndDay": 18,
    "EndTime": 24.0,
}

# -------------------- Folder Paths -------------------- #
result_filefolder_paths = {
    "Plot_FileName_Stem": "Gainesville_OnGrid_Baseline_",
    "SimulationData_FileName": "SimulationData_Gainesville_OnGrid_Baseline",
    "SimulationPerformanceData_FileName": "PerformanceData_Gainesville_OnGrid_Baseline",
    "LoadData_FileName": "PecanStreet_LoadData_PVBat_1_Bat_1_PV_1_None_1",
    "WeatherData_FileName": "Gainesville_Irma_OneWeek",
    "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\25_SmartCommunitySim\code\Examples\Results_OnGrid_Baseline"
}

# -------------------- Weather & Load Data Paths -------------------- #
data_paths = {
    "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\25_SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2017_To_2017_WeatherData_NSRDB_30minTo10minRes.csv",
    "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\25_SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
    
}

# -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
simulation_ObservationActionSpace_Functions = {
    "ObservationSpace_Function": None,
    "ActionSpace_Function": None,
    "Observation_Generator_Function": None,
    "Action_Generator_Function": None
}

# -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
simulation_RewardTerminateTruncate_Functions = {
    "Reward_Function": None,
    "Terminate_Function": None,
    "Truncate_Function": None
}

# ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
plant_dynamic_params = {
    "Lat": 18.17, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
    "Long": -66.74, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
    "Ltm": -60.0, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
    "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
    "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
    "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
    "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
    "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
    "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
    "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
    "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
}

###############################################################################################################
## Smart Community Default Controller Class - User Inputs
###############################################################################################################

Controller_Parameters = {
    "SmartCommunity_ControllerType": 1,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
    "Simulation_ModeType": 1,  # 0 - Off-Grid, 1 - On-Grid
}

###############################################################################################################
## Creating Smart Community Simulator Object
###############################################################################################################

# Initializating Smart Community Simulator Object
SC_Gainesville_Irma = SC_Plant.SmartCommunitySimulator(simulation_params, community_params, plant_initial_conditions, simulation_period, plant_dynamic_params, data_paths, result_filefolder_paths, simulation_ObservationActionSpace_Functions, simulation_RewardTerminateTruncate_Functions)

###############################################################################################################
## Getting Plant/Simulation/Disturbance Data from the Smart Community Simulator Object
###############################################################################################################

# Note: All of the data of the environment relating to the physical characteristics of the Plant and the 
# weather/load disturbances are available through the environment object once it is initialized, it is the
# responsibility of the researcher to utilize this information in the design of their custom controller.

# Here we showcase our default controller utilization in an explicit manner so that it aids in design of 
# custom controllers 

# So we accumalate all the information available through the environment object and use it to instantiate
# our default controller object  

# Getting Plant Information Data
Plant_Parameters = SC_Gainesville_Irma.HEMSPlant_Params
Community_Parameters = SC_Gainesville_Irma.Community_Params

# Getting Simulation Information Data
Simulation_Parameters = SC_Gainesville_Irma.simulation_params

# Creating Parameter Dict
Parameter_Dict = {"Controller_Parameters": Controller_Parameters,
                  "Plant_Parameters": Plant_Parameters,
                  "Community_Parameters": Community_Parameters,
                  "Simulation_Parameters": Simulation_Parameters}

# Getting All Weather Disturbance Data (For all simulation timesteps)
WindSpeed = SC_Gainesville_Irma.Ws
AmbientTemperature = SC_Gainesville_Irma.T_am
GHI = SC_Gainesville_Irma.GHI
DNI = SC_Gainesville_Irma.DNI

# Creating Weather Disturbance Dict
Weather_Disturbance_Dict = {"Ws": WindSpeed,
                            "T_am": AmbientTemperature,
                            "GHI": GHI,
                            "DNI": DNI}

# Getting All Load Disturbance Data (For all simulation timesteps)
LoadData_PriorityWise = SC_Gainesville_Irma.E_LoadData
LoadData_Sum = SC_Gainesville_Irma.E_Load_Desired

# Creating Load Disturbance Dict
Load_Disturbance_Dict = {"E_LoadData": LoadData_PriorityWise,
                         "E_Load_Desired": LoadData_Sum}

# Creating Disturbance Dict
Disturbance_Dict = {"Weather_Disturbance": Weather_Disturbance_Dict,
                    "Load_Disturbance": Load_Disturbance_Dict}

###############################################################################################################
## Creating Smart Community Default Controller Object
###############################################################################################################

# Initializating Smart Community Defaault Controller Object
DefaultController = SC_DefCon.SmartCommunityDefaultController(SC_Gainesville_Irma, Parameter_Dict, Disturbance_Dict)


###############################################################################################################
## Simulation Loop
###############################################################################################################

# Getting Total Simulation Steps
Total_Sim_Steps = SC_Gainesville_Irma.Simulation_Steps_Total

# Getting initial observation
Observation, info = SC_Gainesville_Irma.reset()

# FOR LOOP: For each Sim Step
for ii in range(Total_Sim_Steps):

    # Get Action from Controller
    Action = DefaultController.act(Observation)

    # Step through the Environment based on the Controller Action
    Observation, reward, terminated, truncated, info = SC_Gainesville_Irma.step(Action)

###############################################################################################################
## Saving Sim Data and Sim Performance Data
###############################################################################################################

## Saving Sim Data
SC_Gainesville_Irma.SmartCommunity_SimData_Func()

## Saving Sim Performance Data
SC_Gainesville_Irma.SmartCommunity_PerformanceComputer_Func()

###############################################################################################################
## Getting Sim Data and Sim Performance Data
###############################################################################################################

## Getting Sim Data

# Relative paths based on provided folder structure
SimData_path = SC_Gainesville_Irma.SimData_FilePath

# Load .mat files
simulation_data = sio.loadmat(SimData_path)

# Print keys to see data structure
print("Simulation Data keys:", simulation_data.keys())

# Extracting the Data Object from the loaded .mat file
simulation_data = simulation_data["HEMS_Plant_FigurePlotter_Input"]

# Convert ndarray to dict
simulation_data_dict = {name: simulation_data[name][0, 0] for name in simulation_data.dtype.names}

print("###################### Simulation Data Dict keys #####################")
print("Simulation Data Dict keys:", simulation_data_dict.keys())

# Explanation of Keys/Variables in simulation_data_dict:
#   - 'X_k_Plant_History': History of state variables over all simulation timesteps, storing the plant state at each time.
#   - 'U_k_History': History of control input variables (actions applied to the plant) over all simulation timesteps.
#   - 'E_LoadData': Energy load disturbance data for each prioritized load at each house and each timestep.
#   - 'E_Load_Desired': Total desired energy load for each house at each timestep.
#   - 'HEMSWeatherData_Output': Contains weather data used for simulation, such as wind speed, temperature, solar irradiance.
#   - 'HEMSPlant_Params': Parameters describing HVAC systems, PV generation systems, and battery storage at the plant level.
#   - 'Community_Params': Parameters defining the configuration and size of the simulated community (number of houses, PV, battery configurations, etc.).
#   - 'Baseline_Output_Images_Path': Path to the folder where baseline simulation output images and plots are stored.
#   - 'Single_House_Plotting_Index': Index indicating which house's data should be plotted individually for detailed analysis.
#   - 'Simulation_Params': General parameters controlling the simulation such as simulation mode, time resolution, and controller type.

## Getting Sim Performance Data

# Relative paths based on provided folder structure
SimPerformance_data_path = SC_Gainesville_Irma.SimPerformanceData_FilePath

# Load .mat files
performance_data = sio.loadmat(SimPerformance_data_path)

# Print keys to see data structure
print("Performance Data keys:", performance_data.keys())

# Extracting the Data Object from the loaded .mat file
performance_data = performance_data["Plant_Performance"]

# Convert ndarray to dict
performance_data_dict = {name: performance_data[name][0, 0] for name in performance_data.dtype.names}

# Print keys to see data structure
print("###################### Performance Data Dict keys #####################")
print("Performance Data Dict keys:", performance_data_dict.keys())

# Explanation of Keys/Variables in performance_data_dict:
#    - 'AC_Death_AvgPerDay': Average number of times the house temperature is beyond desired bounds (hrs/day).
#    - 'Percentage_All_Served': Percentage of total loads (both critical and non-critical) served in a given house.
#    - 'Percentage_C_Served': Percentage of critical loads served in a given house.
#    - 'TRM': Thermal Resiliency Metric (1-(AC_Death_AvgPerDay/24)).
#    - 'LRM_C': Load Resiliency Metric for critical loads, indicating reliability specifically for critical appliances (Percentage_C_Served/100).
#    - 'LRM_O': Load Resiliency Metric for other (non-critical) loads, showing reliability for non-critical appliances (Percentage_All_Served/100).
#    - 'AC_Death_AvgPerDay_Community': Community-level average daily AC shutdown frequency.
#    - 'Percentage_All_Served_Community': Percentage of total loads served at the community level (mean Percentage_All_Served).
#    - 'Percentage_C_Served_Community': Percentage of critical loads served at the community level (mean Percentage_C_Served).
#    - 'TRM_Community': Thermal Resiliency Metric at the community level (mean of TRM).
#    - 'LRM_C_Community': Load Resiliency Metric for community-level critical loads (mean of LRM_C).
#    - 'LRM_O_Community': Load Resiliency Metric for community-level non-critical loads (mean of LRM_O). 

###############################################################################################################
## Closing the Environment
###############################################################################################################

## Close the Environment
SC_Gainesville_Irma.close()