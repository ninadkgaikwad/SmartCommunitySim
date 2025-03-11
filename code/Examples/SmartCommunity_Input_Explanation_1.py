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
## Accessing Input Parameters from Constructed Simulator Object
###############################################################################################################

print("\n--- Smart Community Simulator Initialization Details ---")

# Simulation parameters define the overall configuration and type of simulation.
print("Simulation Parameters:", SC_Gainesville_Irma.simulation_params)
for key, value in SC_Gainesville_Irma.simulation_params.items():
    print(f"  {key}: {value}")  # Detailed parameter descriptions provided in initial setup
    # Simulation_Name: Identifier for simulation scenario
    # FileRes: Output file resolution in minutes
    # SmartCommunity_ControllerType: Type of controller (1: Smart, 2: Dumb)
    # Simulation_ModeType: Simulation mode (0: Off-Grid, 1: On-Grid)
    # OffGrid_Simulation_ModeType: Constraint on AC startup (0: Without, 1: With constraint)
    # SimulationType: Simulation type (0: Single Large House)
    # LoadDataType: Load data source (1: Preprocessed, 2: MAT file)
    # WeatherDataType: Weather data source (1: Preprocessed, 2: MAT file)
    # Single_House_Plotting_Index: Index for house-specific plotting
    # ObservationSpace_Type: Type of observation space (Default/User-defined)
    # ActionSpace_Type: Type of action space (Default/User-Defined)

print("Community Parameters:", SC_Gainesville_Irma.Community_Params)
for key, value in SC_Gainesville_Irma.Community_Params.items():
    print(f"  {key}: {value}")
    # N_PV_Bat: Houses with both PV and Battery
    # N_PV: Houses with only PV
    # N_Bat: Houses with only Battery
    # N_None: Houses without PV or Battery

print("Plant Initial Conditions:", SC_Gainesville_Irma.plant_initial_conditions)
for key, value in SC_Gainesville_Irma.plant_initial_conditions.items():
    print(f"  {key}: {value}")
    # T_AC_Base: Base AC temperature setting
    # T_House_Variance: Variance in initial house temperature
    # N1: Battery max charging factor

print("Plant Dynamic Parameters:", SC_Gainesville_Irma.plant_dynamic_params)
for key, value in SC_Gainesville_Irma.plant_dynamic_params.items():
    print(f"  {key}: {value}")
    # Lat: Latitude of location
    # Long: Longitude of location
    # Ltm: Time zone longitude
    # AC_COP_Factor: AC coefficient of performance factor
    # ACLoad_Power_Factor: AC load power scaling factor
    # T_AC_SetPoint: AC temperature setpoint
    # T_AC_DeadBand: Temperature deadband for AC cooling
    # T_AC_HeatingMode_DeadBand: Deadband for heating mode
    # AC_StartUp_LRA_Factor: Factor for AC startup power
    # PV_RatedPower_Factor: PV system rated power scaling factor
    # Battery_Energy_Max_Factor: Battery max energy scaling factor

print("Data Paths:", SC_Gainesville_Irma.data_paths)
for key, value in SC_Gainesville_Irma.data_paths.items():
    print(f"  {key}: {value}")
    # WeatherDataFile_Path: Path to weather data file
    # LoadDataFolder_Path: Path to load data folder

print("Simulation Period:", SC_Gainesville_Irma.simulation_period)
for key, value in SC_Gainesville_Irma.simulation_period.items():
    print(f"  {key}: {value}")
    # StartYear, StartMonth, StartDay, StartTime: Start of simulation period
    # EndYear, EndMonth, EndDay, EndTime: End of simulation period

print("Result File and Folder Paths:", SC_Gainesville_Irma.result_filefolder_paths)
for key, value in SC_Gainesville_Irma.result_filefolder_paths.items():
    print(f"  {key}: {value}")
    # Plot_FileName_Stem: Filename stem for plots
    # SimulationData_FileName: Filename for simulation data
    # SimulationPerformanceData_FileName: Filename for performance data
    # LoadData_FileName: Filename for load data
    # WeatherData_FileName: Filename for weather data
    # Results_FolderPath: Path for simulation results

# User-defined functions and MATLAB Engine status
print("Observation Space Function:", SC_Gainesville_Irma.ObservationSpace_Function)  # Defines how observations are structured or returned
print("Action Space Function:", SC_Gainesville_Irma.ActionSpace_Function)  # Defines the set of possible actions
print("Observation Generator Function:", SC_Gainesville_Irma.Observation_Generator_Function)  # Generates observations dynamically
print("Action Generator Function:", SC_Gainesville_Irma.Action_Generator_Function)  # Generates possible actions dynamically
print("Reward Function:", SC_Gainesville_Irma.Reward_Function)  # Computes reward for reinforcement learning
print("Terminate Function:", SC_Gainesville_Irma.Terminate_Function)  # Determines conditions for simulation termination
print("Truncate Function:", SC_Gainesville_Irma.Truncate_Function)  # Determines conditions for simulation truncation
print("MATLAB Engine Status:", "Initialized" if SC_Gainesville_Irma.eng else "Not Initialized")  # Checks if MATLAB integration is active
print("Simulation Time Step Counter:", SC_Gainesville_Irma.time_iter)  # Tracks simulation progress in discrete steps


###############################################################################################################
## Accessing Plant and House Physical Parameters (Some of the Plant parameters are modified through plant_dynamic_params)
###############################################################################################################

# HEMS Plant Parameters dynamically derived for plant configurations like HVAC, PV, and Battery
print("HEMS Plant Parameters:", SC_Gainesville_Irma.HEMSPlant_Params)
for key, value in SC_Gainesville_Irma.HEMSPlant_Params.items():
    print(f"  {key}: {value}")
    # Location_Name: Name of geographic location (e.g., Gainesville_Fl_USA)
    # hem: Hemisphere indicator (1: Eastern Hemisphere, -1: Western Hemisphere)
    # Lat: Latitude in decimal degrees
    # Long: Longitude in decimal degrees
    # TimeZone: Local time zone offset (hours from GMT)
    # Ltm: Local time meridian in degrees
    # ACLoad_Num: Number of AC units
    # ACLoad_Power: Power consumption of each AC unit (Watts)
    # AC_COP: Air Conditioning Coefficient of Performance
    # T_AC_Base: Base setpoint temperature for the AC unit (°C)
    # T_AC_DeadBand: Temperature range within which AC remains inactive (°C)
    # T_AC_HeatingMode_DeadBand: Deadband temperature range in heating mode (°C)
    # AC_Indicator, AC_Indicator1: Operational indicators for AC (binary flags)
    # E_AC: Energy consumed by AC per timestep (kWh)
    # T_AC_max, T_AC_min: Maximum and minimum AC operational temperature thresholds
    # ACLoad_StartUp_Power: Startup power required by AC (kW)
    # PV_TotlaModules_Num: Total number of photovoltaic modules installed
    # PV_RatedPower: Rated power per PV module (Watts)
    # PV_TempCoeff: Temperature coefficient of PV efficiency (% per °C)
    # GHI_Std: Standard Global Horizontal Irradiance (kW/m²)
    # Temp_Std: Standard operating temperature for PV rating (°C)
    # Eff_Inv: Efficiency of PV inverter
    # Uo, U1: Parameters for PV temperature modeling
    # DOD: Depth of Discharge for battery
    # Eff_Charging_Battery: Efficiency of battery during charging
    # Eff_Discharging_Battery: Efficiency of battery during discharging
    # N1: Factor defining maximum battery charging rate
    # MaxRate_Charging, MaxRate_Discharging: Maximum allowable charging/discharging rate (kW)
    # Battery_Energy_Max, Battery_Energy_Min: Maximum and minimum battery energy storage (kWh)
    # MaxRate_Discharging_StartUp: Maximum battery discharge rate during startup conditions (kW)

# House-specific thermal and energy parameters
print("HEMS House Parameters:", SC_Gainesville_Irma.HEMSHouse_Params)
for key, value in SC_Gainesville_Irma.HEMSHouse_Params.items():
    print(f"  {key}: {value}")
    # R_w: External wall thermal resistance (K/W)
    # R_attic: Attic thermal resistance (K/W)
    # R_roof: Roof thermal resistance (K/W)
    # R_im: Internal mass thermal resistance (K/W)
    # R_win: Window thermal resistance (K/W)
    # C_w: External wall thermal capacitance (J/K)
    # C_attic: Attic thermal capacitance (J/K)
    # C_im: Internal mass thermal capacitance (J/K)
    # C_in: Indoor air thermal capacitance (J/K)
    # C1, C2, C3: Additional heat transfer coefficients
    # Human_Num: Number of human occupants
    # Human_Heat: Heat contribution per occupant (W)
    # Appliance_Heat: Heat contribution from appliances (W)
    # Q_ac: AC heat load (W)
    # Cp: Specific heat capacity of air (kJ/kg K)
    # V: Ventilation mass flow rate (m³/s)
    # Den_Air: Density of air (kg/m³)
    # C_oew: Coefficient relating wind speed to infiltration rate
    # SHGC: Solar Heat Gain Coefficient (fraction)
    # Alpha_w, Alpha_r: Radiation absorption coefficients for walls and roof
    # Area_w, Tilt_w, Azi_w: Wall areas, tilt angles, and azimuth orientations (m², degrees)
    # Area_r, Tilt_r, Azi_r: Roof areas, tilt angles, and azimuth orientations (m², degrees)
    # Area_win, Tilt_win, Azi_win: Window areas, tilt angles, and azimuth orientations (m², degrees)
    # ACLoad_Num: Number of AC units
    # ACLoad_Power: Power rating of each AC unit (Watts)
    # AC_COP: Coefficient of performance of AC
    # T_AC_Base: Base setpoint temperature for AC (°C)
    # T_AC_DeadBand: Temperature range within which AC remains inactive (°C)
    # AC_Indicator, AC_Indicator1: Operational indicators for AC (binary flags)

###############################################################################################################
## Closing the Environment
###############################################################################################################

## Close the Environment
SC_Gainesville_Irma.close()