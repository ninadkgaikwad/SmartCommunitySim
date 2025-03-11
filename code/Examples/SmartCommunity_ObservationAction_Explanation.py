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
## Understanding Default Action and Observation Spaces
###############################################################################################################

# Getting Total Simulation Steps
Total_Sim_Steps = SC_Gainesville_Irma.Simulation_Steps_Total

# Getting Observation Space from Simulator Object
Observation_Space = SC_Gainesville_Irma.observation_space

print("###################### Observation Space #####################")
print(Observation_Space)

# Getting initial observation
Observation_k, info = SC_Gainesville_Irma.reset()

print("###################### Current Observation #####################")
print(Observation_k)

# Note: 
# - This Observation is Default favourable for the Default Controllers which are constructed based on it
# - The Default Observation (type: np.array) is equivalent to self.X_k_Plant/self.X_k_Plus_Plant (type: matlab.double) whose  with shape 
#   [2 (current timestep, next timestep), 39 (All the different variables which define the state of a House), Total Nmber of houses (ordered as PV_Bat -> Bat -> PV -> None)]
# - Description of Columns of Observation
""" 
Column Number	Variable Name

0	            'PV Generation'
1	            'PV Used'
2	            'PV Unused'
3	            'Battery SOC'
4	            'Battery Charging Energy'
5	            'Battery Discharging Energy'
6	            'T_ave'
7	            'T_wall'
8	            'T_attic'
9	            'T_im'
10	            'Energy Consumed by AC'
11	            'Energy Load Consumed Total'
12	            'Energy Load Consumed Load 1'
13	            'Energy Load Consumed Load 2'
14	            'Energy Load Consumed Load 3'
15	            'Energy Load Consumed Load 4'
16	            'Energy Load Consumed Load 5'
17	            'Energy Load Consumed Load 6'
18	            'Energy Load Consumed Load 7'
19	            'Energy Load Consumed Load 8'
20	            'AC ON-OFF Status (current)'
21	            'ON-OFF Status L1'
22	            'ON-OFF Status L2'
23	            'ON-OFF Status L3'
24	            'ON-OFF Status L4'
25	            'ON-OFF Status L5'
26	            'ON-OFF Status L6'
27	            'ON-OFF Status L7'
28	            'ON-OFF Status L8'
29	            'AC ON-OFF Status (previous)'
30	            'ON-OFF Status L1 (previous)'
31	            'ON-OFF Status L2 (previous)'
32	            'ON-OFF Status L3 (previous)'
33	            'ON-OFF Status L4 (previous)'
34	            'ON-OFF Status L5 (previous)'
35	            'ON-OFF Status L6 (previous)'
36	            'ON-OFF Status L7 (previous)'
37	            'ON-OFF Status L8 (previous)'
38	            'Energy from Grid'

 """
# Note: 
# - The above Default Observation can be customized as follows
#   - First:
#       - Write a custom function which has self of the SmartCommunitySimulator Class as the only input argument to generate custom Observation (type: np.array)
#         (self gives you access to all the information to construct a meaningful observation for your application)
#       - Write a custom function which has self of the SmartCommunitySimulator Class as the only input argument to generate custom observation space (type: Gymnasium Box/Dict) matching above function's output
#   - Then:
#       - Set simulation_ObservationActionSpace_Functions["Observation_Generator_Function"] = name_of_your_custom_function 
#       - Set simulation_ObservationActionSpace_Functions["ObservationSpace_Function"] = name_of_your_custom_function 
#       - Set simulation_params["ObservationSpace_Type"] = "User-Defined"

# Getting Action Space from Simulator Object
Action_Space = SC_Gainesville_Irma.action_space

print("###################### Action Space #####################")
print(Action_Space)

# Getting Action from Controller
Action = DefaultController.act(Observation_k)

print("###################### Current Action #####################")
print(Action)

# Note: 
# - This Action is Default 
# - The Default Action (type: np.array) need to be converted to U_k (type: matlab.double) within the simulator so that it can ingest the action 
#   whose  with shape [1 (current timestep), 13 (All the different actions for the DERs/ACs/Loads in the House), Total Nmber of houses (ordered as PV_Bat -> Bat -> PV -> None)]
# - Description of Columns of Observation
""" 
Column Number	Variable Name

0	            'Battery Charging [0,1]'
1	            'Battery Discharging [0,1]'
2	            'AC ON-OFF {0,1}'
3	            'L1 ON-OFF {0,1}'
4	            'L2 ON-OFF {0,1}'
5	            'L3 ON-OFF {0,1}'
6	            'L4 ON-OFF {0,1}'
7	            'L5 ON-OFF {0,1}'
8	            'L6 ON-OFF {0,1}'
9	            'L7 ON-OFF {0,1}'
10	            'L8 ON-OFF {0,1}'
11	            'PV Energy Output [0,1]'
12	            'AC Cooling/Heating Mode {0,1}'

 """
# Note: 
# - The above is the Default Action can be customized as follows
#   - First:
#       - Write a custom function which has self of the SmartCommunitySimulator Class and current action as the input arguments to generate default action (type: np.array)
#         (self gives you access to all the information to construct a meaningful observation for your application)
#       - Write a custom function which has self of the SmartCommunitySimulator Class as the input argument to generate custom action space (type: Gymnasium Box/Dict) matching above function's output
#   - Then:
#       - Set simulation_ObservationActionSpace_Functions["Action_Generator_Function"] = name_of_your_custom_function 
#       - Set simulation_ObservationActionSpace_Functions["ActionSpace_Function"] = name_of_your_custom_function 
#       - Set simulation_params["ActionSpace_Type"] = "User-Defined"

# Step through the Environment based on the Controller Action
Observation_kPlus, reward, terminated, truncated, info = SC_Gainesville_Irma.step(Action)

print("###################### Next Observation #####################")
print(Observation_kPlus)

###############################################################################################################
## X_k_Plant_History and U_k_History
###############################################################################################################

# X_k_Plant_History stores X_k_Plant (type: matlab.double, shape:[Number of Simulation Iterations, 39, Number of Houses]) for each simulation iteration 
X_k_Plant_History = SC_Gainesville_Irma.X_k_Plant_History

# Converting to np.array
X_k_Plant_History = np.array(X_k_Plant_History)

print("###################### X_k_Plant_History #####################")
print(X_k_Plant_History)

# U_k_History stores U_k (Action in default form) (type: matlab.double, shape:[Number of Simulation Iterations, 13, Number of Houses]) for each simulation iteration 
U_k_History = SC_Gainesville_Irma.U_k_History

# Converting to np.array
U_k_History = np.array(U_k_History)

print("###################### U_k_History #####################")
print(U_k_History)

# Note:
# - Every iteration X_k_Plant_History and U_k_History increase by 1 in their 0th axis
# - They are used in self.SmartCommunity_SimData_Func/self.SmartCommunity_PerformanceComputer_Func/self.render
#   - To store simulation data in .mat format (self.SmartCommunity_SimData_Func)
#   - To compute and store simulation performance data (self.SmartCommunity_PerformanceComputer_Func)
#   - To plot time series plots for various simulation variables (self.render)

###############################################################################################################
## Closing the Environment
###############################################################################################################

## Close the Environment
SC_Gainesville_Irma.close()