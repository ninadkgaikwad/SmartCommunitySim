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
    "Simulation_Name": "OffGrid_Baseline_WOACSC",
    "FileRes": 10.0,  # in Minutes
    "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
    "Simulation_ModeType": 0,  # 0 - Off-Grid, 1 - On-Grid
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
    "Plot_FileName_Stem": "Gainesville_OffGrid_Baseline_WOACSC_",
    "SimulationData_FileName": "SimulationData_Gainesville_OffGrid_Baseline_WOACSC",
    "SimulationPerformanceData_FileName": "PerformanceData_Gainesville_OffGrid_Baseline_WOACSC",
    "LoadData_FileName": "PecanStreet_LoadData_PVBat_1_Bat_1_PV_1_None_1",
    "WeatherData_FileName": "Gainesville_Irma_OneWeek",
    "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\25_SmartCommunitySim\code\Examples\Results_OffGrid_Baseline_WOACSC"
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
    "Lat": -1.0, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
    "Long": -1.0, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
    "Ltm": -1.0, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
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
## Creating Smart Community Simulator Object
###############################################################################################################

# Initializating Smart Community Simulator Object
SC_Gainesville_Irma = SC_Plant.SmartCommunitySimulator(simulation_params, community_params, plant_initial_conditions, simulation_period, plant_dynamic_params, data_paths, result_filefolder_paths, simulation_ObservationActionSpace_Functions, simulation_RewardTerminateTruncate_Functions)

###############################################################################################################
## Accessing Disturbance Data from Constructed Simulator Object
###############################################################################################################

# Weather Data Disturbance
# Retrieve weather disturbance data (MATLAB double arrays)
Ws = np.array(SC_Gainesville_Irma.Ws).flatten()  # Wind speed
T_am = np.array(SC_Gainesville_Irma.T_am).flatten()  # Ambient temperature
GHI = np.array(SC_Gainesville_Irma.GHI).flatten()  # Global Horizontal Irradiance
DNI = np.array(SC_Gainesville_Irma.DNI).flatten()  # Direct Normal Irradiance

# Time vector assuming consistent simulation timestep
time_steps = np.arange(len(Ws))

# Plotting the weather disturbances
import matplotlib.pyplot as plt

plt.figure(figsize=(14, 10))

# Wind Speed plot
plt.subplot(4, 1, 1)
plt.plot(Ws, label='Wind Speed (m/s)', color='blue')
plt.ylabel('Wind Speed (m/s)')
plt.title('Weather Disturbance Data')
plt.legend()

# Ambient Temperature plot
plt.subplot(4, 1, 2)
plt.plot(T_am, label='Ambient Temp (°C)', color='red')
plt.ylabel('Temperature (°C)')
plt.legend()

# GHI plot
plt.subplot(4, 1, 3)
plt.plot(GHI, label='Global Horizontal Irradiance (W/m²)', color='orange')
plt.ylabel('GHI (W/m²)')
plt.legend()

# DNI plot
plt.subplot(4, 1, 4)
plt.plot(DNI, label='Direct Normal Irradiance (W/m²)', color='green')
plt.xlabel('Time Step')
plt.ylabel('DNI (W/m²)')
plt.legend()

plt.suptitle('Weather Disturbance Data from Smart Community Simulator')
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()

# Load Data Disturbance

# Extract load disturbance data from constructed simulator object
E_LoadData = np.array(SC_Gainesville_Irma.E_LoadData)  # shape: [timesteps, 8 prioritized loads, houses (ordered as PV_Bat -> Bat -> PV -> None)]
E_Load_Desired = np.array(SC_Gainesville_Irma.E_Load_Desired)  # Total load [timesteps, houses (ordered as PV_Bat -> Bat -> PV -> None)]

E_LoadData = E_LoadData[:,9:,:] # The first 9 columns are not Load Data

# Determine dimensions
num_timesteps, num_loads, num_houses = E_LoadData.shape

# Plot total load (E_Load_Desired) for each house as subplots
fig, axs = plt.subplots(num_houses, 1, figsize=(14, 4*num_houses), sharex=True)
for house_idx in range(num_houses):
    axs[house_idx].plot(E_Load_Desired[:, house_idx], label='Total Load (Desired)', color='orange')
    axs[house_idx].set_title(f'Total Desired Load Profile for House {house_idx + 1}')
    axs[house_idx].set_ylabel('Load (kWh)')
    axs[house_idx].legend()
    axs[house_idx].grid(True)

plt.xlabel('Time Steps')
plt.tight_layout()
plt.show()

# Plot individual prioritized loads for each house in a 4x2 subplot grid
for house_idx in range(num_houses):
    fig, axs = plt.subplots(4, 2, figsize=(16, 12), sharex=True)
    axs_flat = axs.flatten()
    for load_idx in range(num_loads):
        axs_flat[load_idx].plot(E_LoadData[:, load_idx, house_idx], label=f'Load {load_idx + 1}')
        axs_flat[load_idx].set_ylabel('Load (kWh)')
        axs_flat[load_idx].legend()
        axs_flat[load_idx].grid(True)

    plt.suptitle(f'Individual Prioritized Loads for House {house_idx + 1}')
    plt.xlabel('Time Steps')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

###############################################################################################################
## Closing the Environment
###############################################################################################################

## Close the Environment
SC_Gainesville_Irma.close()
