###############################################################################################################
## Import Desired Packages
###############################################################################################################

import sys
import os

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

from Exp_RL_Utilities_Module import *

###############################################################################################################
## Experiment Configuration Module - Custom Constants
###############################################################################################################

def Exp_Configuration_Generator(COMMUNITY_TYPE, GRID_TYPE, CONTROLLER_TYPE, LOAD_DATA_INITIALIZE, WEATHER_DATA_INITIALIZE):
    

    if LOAD_DATA_INITIALIZE:
        LoadDataType = 1
    else:
        LoadDataType = 2

    if WEATHER_DATA_INITIALIZE:
        WeatherDataType = 1
    else:
        WeatherDataType = 2

    if (COMMUNITY_TYPE == "House" and  GRID_TYPE == "Off-Grid"  and CONTROLLER_TYPE == "MPC"):  # SingleHouse_OffGrid_MPC_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Single House Off-Grid MPC
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "SingleHouse_OffGrid_MPC",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 0,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 1,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "Default",  # Default ; User-Defined
            "ActionSpace_Type": "Default",  # Default ; User-Defined
            "History_Flag": True,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 0,  # Houses with just PV
            "N_Bat": 0,  # Houses with just Battery
            "N_None": 0,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2017,
            "StartMonth": 9,
            "StartDay": 11,
            "StartTime": 0.0,
            "EndYear": 2017,
            "EndMonth": 9,
            "EndDay": 18,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "SingleHouse_OffGrid_MPC_",
            "SimulationData_FileName": "SimulationData_SingleHouse_OffGrid_MPC",
            "SimulationPerformanceData_FileName": "PerformanceData_SingleHouse_OffGrid_MPC",
            "LoadData_FileName": "SingleHouse_LoadData_PVBat_1_Bat_0_PV_0_None_0_MPC",
            "WeatherData_FileName": "WeatherData_Gainesville_2017_Irma_OneWeek_MPC",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_SingleHouse_OffGrid_MPC"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2017_To_2017_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": None,
            "ActionSpace_Function": None,
            "Observation_Generator_Function": None,
            "Action_Generator_Function": None
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": None,
            "Terminate_Function": None,
            "Truncate_Function": None
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }

    if (COMMUNITY_TYPE == "House" and  GRID_TYPE == "On-Grid" and  CONTROLLER_TYPE == "MPC"):  # SingleHouse_OnGrid_MPC_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Single House On-Grid MPC
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "SingleHouse_OnGrid_MPC",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 1,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 0,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "Default",  # Default ; User-Defined
            "ActionSpace_Type": "Default",  # Default ; User-Defined
            "History_Flag": True,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 0,  # Houses with just PV
            "N_Bat": 0,  # Houses with just Battery
            "N_None": 0,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2017,
            "StartMonth": 9,
            "StartDay": 11,
            "StartTime": 0.0,
            "EndYear": 2017,
            "EndMonth": 9,
            "EndDay": 18,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "SingleHouse_OnGrid_MPC_",
            "SimulationData_FileName": "SimulationData_SingleHouse_OnGrid_MPC",
            "SimulationPerformanceData_FileName": "PerformanceData_SingleHouse_OnGrid_MPC",
            "LoadData_FileName": "SingleHouse_LoadData_PVBat_1_Bat_0_PV_0_None_0_MPC",
            "WeatherData_FileName": "WeatherData_Gainesville_2017_Irma_OneWeek_MPC",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_SingleHouse_OnGrid_MPC"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2017_To_2017_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": None,
            "ActionSpace_Function": None,
            "Observation_Generator_Function": None,
            "Action_Generator_Function": None
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": None,
            "Terminate_Function": None,
            "Truncate_Function": None
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }

    if (COMMUNITY_TYPE == "Community" and  GRID_TYPE == "Off-Grid" and CONTROLLER_TYPE == "MPC"):  # MultiHouse_OffGrid_MPC_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Multi House Off-Grid MPC
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "MultiHouse_OffGrid_MPC",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 0,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 1,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "Default",  # Default ; User-Defined
            "ActionSpace_Type": "Default",  # Default ; User-Defined
            "History_Flag": True,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 1,  # Houses with just PV
            "N_Bat": 1,  # Houses with just Battery
            "N_None": 1,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2017,
            "StartMonth": 9,
            "StartDay": 11,
            "StartTime": 0.0,
            "EndYear": 2017,
            "EndMonth": 9,
            "EndDay": 18,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "MultiHouse_OffGrid_MPC_",
            "SimulationData_FileName": "SimulationData_MultiHouse_OffGrid_MPC",
            "SimulationPerformanceData_FileName": "PerformanceData_MultiHouse_OffGrid_MPC",
            "LoadData_FileName": "MultiHouse_LoadData_PVBat_1_Bat_1_PV_1_None_1_MPC",
            "WeatherData_FileName": "WeatherData_Gainesville_2017_Irma_OneWeek_MPC",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_MultiHouse_OffGrid_MPC"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2017_To_2017_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": None,
            "ActionSpace_Function": None,
            "Observation_Generator_Function": None,
            "Action_Generator_Function": None
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": None,
            "Terminate_Function": None,
            "Truncate_Function": None
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }

    if (COMMUNITY_TYPE == "Community" and  GRID_TYPE == "On-Grid" and CONTROLLER_TYPE == "MPC"):  # MultiHouse_OnGrid_MPC_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Multi House On-Grid MPC
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "MultiHouse_OnGrid_MPC",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 1,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 0,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "Default",  # Default ; User-Defined
            "ActionSpace_Type": "Default",  # Default ; User-Defined
            "History_Flag": True,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 1,  # Houses with just PV
            "N_Bat": 1,  # Houses with just Battery
            "N_None": 1,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2017,
            "StartMonth": 9,
            "StartDay": 11,
            "StartTime": 0.0,
            "EndYear": 2017,
            "EndMonth": 9,
            "EndDay": 18,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "MultiHouse_OnGrid_MPC_",
            "SimulationData_FileName": "SimulationData_MultiHouse_OnGrid_MPC",
            "SimulationPerformanceData_FileName": "PerformanceData_MultiHouse_OnGrid_MPC",
            "LoadData_FileName": "MultiHouse_LoadData_PVBat_1_Bat_1_PV_1_None_1_MPC",
            "WeatherData_FileName": "WeatherData_Gainesville_2017_Irma_OneWeek_MPC",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_MultiHouse_OnGrid_MPC"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2017_To_2017_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": None,
            "ActionSpace_Function": None,
            "Observation_Generator_Function": None,
            "Action_Generator_Function": None
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": None,
            "Terminate_Function": None,
            "Truncate_Function": None
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }

    if (COMMUNITY_TYPE == "House" and  GRID_TYPE == "Off-Grid" and CONTROLLER_TYPE == "RL-Training"):  # SingleHouse_OffGrid_RLTraining_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Single House Off-Grid RL-Training
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "SingleHouse_OffGrid_RLTraining",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 0,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 1,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "User-Defined",  # Default ; User-Defined
            "ActionSpace_Type": "User-Defined",  # Default ; User-Defined
            "History_Flag": False,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 0,  # Houses with just PV
            "N_Bat": 0,  # Houses with just Battery
            "N_None": 0,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2016,
            "StartMonth": 1,
            "StartDay": 1,
            "StartTime": 0.0,
            "EndYear": 2016,
            "EndMonth": 12,
            "EndDay": 25,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "SingleHouse_OffGrid_RLTraining_",
            "SimulationData_FileName": "SimulationData_SingleHouse_OffGrid_RLTraining",
            "SimulationPerformanceData_FileName": "PerformanceData_SingleHouse_OffGrid_RLTraining",
            "LoadData_FileName": "SingleHouse_LoadData_PVBat_1_Bat_0_PV_0_None_0_RLTraining",
            "WeatherData_FileName": "WeatherData_Gainesville_2016_Irma_RLTraining",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_SingleHouse_OffGrid_RLTraining"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2016_To_2016_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": SingleHouse_OffGrid_RL_ObservationSpace_Function,
            "ActionSpace_Function": SingleHouse_OffGrid_RL_ActionSpace_Function,
            "Observation_Generator_Function": SingleHouse_OffGrid_RL_Observation_Generator_Function,
            "Action_Generator_Function": SingleHouse_OffGrid_RL_Action_Generator_Function
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": SingleHouse_OffGrid_RL_Reward_Function,
            "Terminate_Function": SingleHouse_OffGrid_RL_Terminate_Function,
            "Truncate_Function": SingleHouse_OffGrid_RL_Truncate_Function
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }

    if (COMMUNITY_TYPE == "House" and  GRID_TYPE == "On-Grid" and CONTROLLER_TYPE == "RL-Training"):  # SingleHouse_OnGrid_RLTraining_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Single House On-Grid RL-Training
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "SingleHouse_OnGrid_RLTraining",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 1,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 0,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "User-Defined",  # Default ; User-Defined
            "ActionSpace_Type": "User-Defined",  # Default ; User-Defined
            "History_Flag": False,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 0,  # Houses with just PV
            "N_Bat": 0,  # Houses with just Battery
            "N_None": 0,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2016,
            "StartMonth": 1,
            "StartDay": 1,
            "StartTime": 0.0,
            "EndYear": 2016,
            "EndMonth": 12,
            "EndDay": 25,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "SingleHouse_OnGrid_RLTraining_",
            "SimulationData_FileName": "SimulationData_SingleHouse_OnGrid_RLTraining",
            "SimulationPerformanceData_FileName": "PerformanceData_SingleHouse_OnGrid_RLTraining",
            "LoadData_FileName": "SingleHouse_LoadData_PVBat_1_Bat_0_PV_0_None_0_RLTraining",
            "WeatherData_FileName": "WeatherData_Gainesville_2016_Irma_RLTraining",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_SingleHouse_OnGrid_RLTraining"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2016_To_2016_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": SingleHouse_OnGrid_RL_ObservationSpace_Function,
            "ActionSpace_Function": SingleHouse_OnGrid_RL_ActionSpace_Function,
            "Observation_Generator_Function": SingleHouse_OnGrid_RL_Observation_Generator_Function,
            "Action_Generator_Function": SingleHouse_OnGrid_RL_Action_Generator_Function
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": SingleHouse_OnGrid_RL_Reward_Function,
            "Terminate_Function": SingleHouse_OnGrid_RL_Terminate_Function,
            "Truncate_Function": SingleHouse_OnGrid_RL_Truncate_Function
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }

    if (COMMUNITY_TYPE == "Community" and  GRID_TYPE == "Off-Grid" and CONTROLLER_TYPE == "RL-Training"):  # MultiHouse_OffGrid_RLTraining_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Multi House Off-Grid RL-Training
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "MultiHouse_OffGrid_RLTraining",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 0,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 1,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "User-Defined",  # Default ; User-Defined
            "ActionSpace_Type": "User-Defined",  # Default ; User-Defined
            "History_Flag": False,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 1,  # Houses with just PV
            "N_Bat": 1,  # Houses with just Battery
            "N_None": 1,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2016,
            "StartMonth": 1,
            "StartDay": 1,
            "StartTime": 0.0,
            "EndYear": 2016,
            "EndMonth": 12,
            "EndDay": 25,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "MultiHouse_OffGrid_RLTraining_",
            "SimulationData_FileName": "SimulationData_MultiHouse_OffGrid_RLTraining",
            "SimulationPerformanceData_FileName": "PerformanceData_MultiHouse_OffGrid_RLTraining",
            "LoadData_FileName": "MultiHouse_LoadData_PVBat_1_Bat_0_PV_0_None_0_RLTraining",
            "WeatherData_FileName": "WeatherData_Gainesville_2016_Irma_RLTraining",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_MultiHouse_OffGrid_RLTraining"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2016_To_2016_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": MultiHouse_OffGrid_RL_ObservationSpace_Function,
            "ActionSpace_Function": MultiHouse_OffGrid_RL_ActionSpace_Function,
            "Observation_Generator_Function": MultiHouse_OffGrid_RL_Observation_Generator_Function,
            "Action_Generator_Function": MultiHouse_OffGrid_RL_Action_Generator_Function
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": MultiHouse_OffGrid_RL_Reward_Function,
            "Terminate_Function": MultiHouse_OffGrid_RL_Terminate_Function,
            "Truncate_Function": MultiHouse_OffGrid_RL_Truncate_Function
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }

    if (COMMUNITY_TYPE == "Community" and  GRID_TYPE == "On-Grid" and CONTROLLER_TYPE == "RL-Training"):  # MultiHouse_OnGrid_RLTraining_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Multi House On-Grid RL-Training
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "MultiHouse_OnGrid_RLTraining",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 1,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 0,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "User-Defined",  # Default ; User-Defined
            "ActionSpace_Type": "User-Defined",  # Default ; User-Defined
            "History_Flag": False,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 1,  # Houses with just PV
            "N_Bat": 1,  # Houses with just Battery
            "N_None": 1,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2016,
            "StartMonth": 1,
            "StartDay": 1,
            "StartTime": 0.0,
            "EndYear": 2016,
            "EndMonth": 12,
            "EndDay": 25,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "MultiHouse_OnGrid_RLTraining_",
            "SimulationData_FileName": "SimulationData_MultiHouse_OnGrid_RLTraining",
            "SimulationPerformanceData_FileName": "PerformanceData_MultiHouse_OnGrid_RLTraining",
            "LoadData_FileName": "MultiHouse_LoadData_PVBat_1_Bat_0_PV_0_None_0_RLTraining",
            "WeatherData_FileName": "WeatherData_Gainesville_2016_Irma_RLTraining",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_MultiHouse_OnGrid_RLTraining"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2016_To_2016_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": MultiHouse_OnGrid_RL_ObservationSpace_Function,
            "ActionSpace_Function": MultiHouse_OnGrid_RL_ActionSpace_Function,
            "Observation_Generator_Function": MultiHouse_OnGrid_RL_Observation_Generator_Function,
            "Action_Generator_Function": MultiHouse_OnGrid_RL_Action_Generator_Function
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": MultiHouse_OnGrid_RL_Reward_Function,
            "Terminate_Function": MultiHouse_OnGrid_RL_Terminate_Function,
            "Truncate_Function": MultiHouse_OnGrid_RL_Truncate_Function
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }

    if (COMMUNITY_TYPE == "House" and  GRID_TYPE == "Off-Grid" and CONTROLLER_TYPE == "RL-Testing"):  # SingleHouse_OffGrid_RLTesting_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Single House Off-Grid RL-Testing
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "SingleHouse_OffGrid_RLTesting",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 0,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 1,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "User-Defined",  # Default ; User-Defined
            "ActionSpace_Type": "User-Defined",  # Default ; User-Defined
            "History_Flag": True,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 0,  # Houses with just PV
            "N_Bat": 0,  # Houses with just Battery
            "N_None": 0,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2017,
            "StartMonth": 9,
            "StartDay": 11,
            "StartTime": 0.0,
            "EndYear": 2017,
            "EndMonth": 9,
            "EndDay": 18,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "SingleHouse_OffGrid_RLTesting_",
            "SimulationData_FileName": "SimulationData_SingleHouse_OffGrid_RLTesting",
            "SimulationPerformanceData_FileName": "PerformanceData_SingleHouse_OffGrid_RLTesting",
            "LoadData_FileName": "SingleHouse_LoadData_PVBat_1_Bat_0_PV_0_None_0_RLTesting",
            "WeatherData_FileName": "WeatherData_Gainesville_2017_Irma_RLTesting",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_SingleHouse_OffGrid_RLTesting"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2017_To_2017_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": SingleHouse_OffGrid_RL_ObservationSpace_Function,
            "ActionSpace_Function": SingleHouse_OffGrid_RL_ActionSpace_Function,
            "Observation_Generator_Function": SingleHouse_OffGrid_RL_Observation_Generator_Function,
            "Action_Generator_Function": SingleHouse_OffGrid_RL_Action_Generator_Function
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": SingleHouse_OffGrid_RL_Reward_Function,
            "Terminate_Function": SingleHouse_OffGrid_RL_Terminate_Function,
            "Truncate_Function": SingleHouse_OffGrid_RL_Truncate_Function
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }

    if (COMMUNITY_TYPE == "House" and  GRID_TYPE == "On-Grid" and CONTROLLER_TYPE == "RL-Testing"):  # SingleHouse_OnGrid_RLTesting_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Single House On-Grid RL-Testing
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "SingleHouse_OnGrid_RLTesting",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 1,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 0,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "User-Defined",  # Default ; User-Defined
            "ActionSpace_Type": "User-Defined",  # Default ; User-Defined
            "History_Flag": True,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 0,  # Houses with just PV
            "N_Bat": 0,  # Houses with just Battery
            "N_None": 0,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2017,
            "StartMonth": 9,
            "StartDay": 11,
            "StartTime": 0.0,
            "EndYear": 2017,
            "EndMonth": 9,
            "EndDay": 18,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "SingleHouse_OnGrid_RLTesting_",
            "SimulationData_FileName": "SimulationData_SingleHouse_OnGrid_RLTesting",
            "SimulationPerformanceData_FileName": "PerformanceData_SingleHouse_OnGrid_RLTesting",
            "LoadData_FileName": "SingleHouse_LoadData_PVBat_1_Bat_0_PV_0_None_0_RLTesting",
            "WeatherData_FileName": "WeatherData_Gainesville_2016_Irma_RLTesting",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_SingleHouse_OnGrid_RLTesting"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2017_To_2017_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": SingleHouse_OnGrid_RL_ObservationSpace_Function,
            "ActionSpace_Function": SingleHouse_OnGrid_RL_ActionSpace_Function,
            "Observation_Generator_Function": SingleHouse_OnGrid_RL_Observation_Generator_Function,
            "Action_Generator_Function": SingleHouse_OnGrid_RL_Action_Generator_Function
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": SingleHouse_OnGrid_RL_Reward_Function,
            "Terminate_Function": SingleHouse_OnGrid_RL_Terminate_Function,
            "Truncate_Function": SingleHouse_OnGrid_RL_Truncate_Function
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }

    if (COMMUNITY_TYPE == "Community" and  GRID_TYPE == "Off-Grid" and CONTROLLER_TYPE == "RL-Testing"):  # MultiHouse_OffGrid_RLTesting_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Multi House Off-Grid RL-Testing
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "MultiHouse_OffGrid_RLTesting",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 0,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 1,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "User-Defined",  # Default ; User-Defined
            "ActionSpace_Type": "User-Defined",  # Default ; User-Defined
            "History_Flag": True,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 1,  # Houses with just PV
            "N_Bat": 1,  # Houses with just Battery
            "N_None": 1,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2017,
            "StartMonth": 9,
            "StartDay": 11,
            "StartTime": 0.0,
            "EndYear": 2017,
            "EndMonth": 9,
            "EndDay": 18,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "MultiHouse_OffGrid_RLTesting_",
            "SimulationData_FileName": "SimulationData_MultiHouse_OffGrid_RLTesting",
            "SimulationPerformanceData_FileName": "PerformanceData_MultiHouse_OffGrid_RLTesting",
            "LoadData_FileName": "MultiHouse_LoadData_PVBat_1_Bat_0_PV_0_None_0_RLTesting",
            "WeatherData_FileName": "WeatherData_Gainesville_2016_Irma_RLTesting",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_MultiHouse_OffGrid_RLTesting"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2017_To_2017_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": MultiHouse_OffGrid_RL_ObservationSpace_Function,
            "ActionSpace_Function": MultiHouse_OffGrid_RL_ActionSpace_Function,
            "Observation_Generator_Function": MultiHouse_OffGrid_RL_Observation_Generator_Function,
            "Action_Generator_Function": MultiHouse_OffGrid_RL_Action_Generator_Function
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": MultiHouse_OffGrid_RL_Reward_Function,
            "Terminate_Function": MultiHouse_OffGrid_RL_Terminate_Function,
            "Truncate_Function": MultiHouse_OffGrid_RL_Truncate_Function
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }

    if (COMMUNITY_TYPE == "Community" and  GRID_TYPE == "On-Grid" and CONTROLLER_TYPE == "RL-Testing"):  # MultiHouse_OnGrid_RLTesting_Config
        #-------------------------------------------------------------------------------------------------------------#
        # Multi House On-Grid RL-Testing
        #-------------------------------------------------------------------------------------------------------------#

        Config = {
        # -------------------- Simulation Step Sizes (User-defined inputs only) -------------------- #
        "simulation_params" : {
            "Simulation_Name": "MultiHouse_OnGrid_RLTesting",
            "FileRes": 10.0,  # in Minutes
            "SmartCommunity_ControllerType": 2,  # 1 = Smart Local Controller ; 2 = Dumb Local Controller
            "Simulation_ModeType": 1,  # 0 - Off-Grid, 1 - On-Grid
            "OffGrid_Simulation_ModeType": 0,  # 1 - With AC Start-up constraint ; 0 - Without AC Start-up constraint
            "SimulationType": 0,  # Single Large House Simulation type
            "LoadDataType": LoadDataType,  # 1 = Preprocessed Pecan Street data ; 2 = .mat File exists
            "WeatherDataType": WeatherDataType,  # 1 = Preprocessed NSRDB File ; 2 = .mat File exists
            "Single_House_Plotting_Index": 1,  # House index for single-house plotting
            "ObservationSpace_Type": "User-Defined",  # Default ; User-Defined
            "ActionSpace_Type": "User-Defined",  # Default ; User-Defined
            "History_Flag": True,  # Captures State Action Histories if True
        },

        # -------------------- Community Specification -------------------- #
        "community_params" : {
            "N_PV_Bat": 1,  # Houses with both PV and Battery
            "N_PV": 1,  # Houses with just PV
            "N_Bat": 1,  # Houses with just Battery
            "N_None": 1,  # Houses with neither PV nor Battery
        },

        # -------------------- Plant Initial Conditions -------------------- #
        "plant_initial_conditions" : {
            "T_AC_Base": 24.0,  # Base AC Temperature
            "T_House_Variance": 0.5,  # Variance in house temperature
            "N1": 1.0,  # User-defined Battery Max Charging Factor
        },

        # -------------------- Simulation Period Specification -------------------- #
        "simulation_period" : {
            "StartYear": 2017,
            "StartMonth": 9,
            "StartDay": 11,
            "StartTime": 0.0,
            "EndYear": 2017,
            "EndMonth": 9,
            "EndDay": 18,
            "EndTime": 24.0,
        },

        # -------------------- Folder Paths -------------------- #
        "result_filefolder_paths" : {
            "Plot_FileName_Stem": "MultiHouse_OnGrid_RLTesting_",
            "SimulationData_FileName": "SimulationData_MultiHouse_OnGrid_RLTesting",
            "SimulationPerformanceData_FileName": "PerformanceData_MultiHouse_OnGrid_RLTesting",
            "LoadData_FileName": "MultiHouse_LoadData_PVBat_1_Bat_0_PV_0_None_0_RLTesting",
            "WeatherData_FileName": "WeatherData_Gainesville_2016_Irma_RLTesting",
            "Results_FolderPath": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\Results_MultiHouse_OnGrid_RLTesting"
        },

        # -------------------- Weather & Load Data Paths -------------------- #
        "data_paths" : {
            "WeatherDataFile_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\WeatherData\ProcessedFiles\Gainesville_Florida\Res_10\Gainesville_2017_To_2017_WeatherData_NSRDB_30minTo10minRes.csv",
            "LoadDataFolder_Path": r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\data\LoadData\ProcessedFiles\10minute_data_austin_HouseWise",
            
        },

        # -------------------- Simulation Observation/Action Space/Generator Functions (User-Defined)-------------------- #
        "simulation_ObservationActionSpace_Functions" : {
            "ObservationSpace_Function": MultiHouse_OnGrid_RL_ObservationSpace_Function,
            "ActionSpace_Function": MultiHouse_OnGrid_RL_ActionSpace_Function,
            "Observation_Generator_Function": MultiHouse_OnGrid_RL_Observation_Generator_Function,
            "Action_Generator_Function": MultiHouse_OnGrid_RL_Action_Generator_Function
        },

        # -------------------- Simulation Reward/Terminate/Truncate Functions (User-Defined)-------------------- #
        "simulation_RewardTerminateTruncate_Functions" : {
            "Reward_Function": MultiHouse_OnGrid_RL_Reward_Function,
            "Terminate_Function": MultiHouse_OnGrid_RL_Terminate_Function,
            "Truncate_Function": MultiHouse_OnGrid_RL_Truncate_Function
        },

        # ---------------------------- Simulation HVAC/DER Parameters ----------------------------- #
        "plant_dynamic_params" : {
            "Lat": 29.65, # Latitude of Community Location (+ -> Northern Hemishphere; - -> Souththern Hemishphere)
            "Long": -82.32, # Longitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "Ltm": 60, # Time Zone Logitude of Community Location (+ -> Eastern Hemishphere; - -> Western Hemishphere)
            "AC_COP_Factor": 1.0,  # Placeholder for AC Coefficient of Performance [> 0.0][depending on the type of AC, gets multiplied by base COP of 3.33]
            "ACLoad_Power_Factor": 1.0,  # Placeholder for AC Load Power Factor [> 0.0][depending type of AC, get multiplied by base AC power of 3000W]
            "T_AC_SetPoint": 24.0,  # Base AC Temperature Setpoint
            "T_AC_DeadBand": 1.0,  # Deadband for AC cooling mode
            "T_AC_HeatingMode_DeadBand": 5.0,  # Deadband for AC heating mode
            "AC_StartUp_LRA_Factor": 5.0,  # Startup LRA (Locked Rotor Amperage) Factor [>= 1.0][Gives the factor for AC startup Power]
            "PV_RatedPower_Factor": 1.0,  # Rated Power Factor for PV system [> 0.0][depending the PV installation, get multiplied to the base PV of 10kW]
            "Battery_Energy_Max_Factor": 1.0  # Battery Max Energy Factor [> 0.0][depending on the size of battery, gets multiplied to base battery of 13.5kWh (Tesla Home Battery)]
        },

        }          

    return Config

def Exp_RL_Configuration_Generator():

    # -------------------- Horizon - USER SETUP-------------------- #
    RL_HORIZON_HOURS = 24
    RL_HORIZON_HOUR_AVG = 1
    RL_DATA_RES = 10.0

    # -------------------- Horizon - DERIVED ----------------------- #
    RL_HORIZON_N = int(RL_HORIZON_HOURS * (60 / RL_DATA_RES))
    RL_HORIZON_AVG_N = int(RL_HORIZON_HOUR_AVG * (60 / RL_DATA_RES))

    # -------------------- RL PARAMETERS DICTIONARY ---------------- #
    RL_Parameters = {
        "RL_HORIZON_HOURS": RL_HORIZON_HOURS,
        "RL_HORIZON_HOUR_AVG": RL_HORIZON_HOUR_AVG,
        "RL_DATA_RES": RL_DATA_RES,
        "RL_HORIZON_N": RL_HORIZON_N,
        "RL_HORIZON_AVG_N": RL_HORIZON_AVG_N,

        # Off-grid reward weights
        "OFFGRID_WEIGHTS": {
            "W_T_h":        1.0,
            "W_Ebat":       1.0,
            "W_Ebal":       1.0,
            "W_startup":    1.0,
            "W_surplus":    1.0,
            "W_load":       1.0,
            "W_mode":       1.0,
        },

        # On-grid reward weights
        "ONGRID_WEIGHTS": {
            "W_T_h":        1.0,
            "W_Ebat":       1.0,
            "W_mode":       1.0,
            "W_cost":       1.0,
            "W_PV":         1.0,
            "W_u_pv":       1.0,
        },
    }  

    return RL_Parameters