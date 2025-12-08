###############################################################################################################
## Import Desired Packages
###############################################################################################################

import os
import matlab.engine
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

###############################################################################################################
## Smart Community Simulator Class - Gymnasium
###############################################################################################################
class SmartCommunitySimulator(gym.Env):
    """
    A Gymnasium environment for a Smart Community of Houses:

    where:
    
    The goal is to simulate/analyze/develop controllers for Smart Community Energy Management.
    """

    metadata = {"render_modes": ["human", "none"]}

    def __init__(self, simulation_params, community_params, plant_initial_conditions, simulation_period, plant_dynamic_params, data_paths, result_filefolder_paths, simulation_ObservationActionSpace_Functions, simulation_RewardTerminateTruncate_Functions):
        super(SmartCommunitySimulator, self).__init__()

        # -----------------------------------------------------------------------------------------------------------
        ## Start MATLAB Engine 
        # -----------------------------------------------------------------------------------------------------------
        
        # Staring Matlab Engine
        eng = matlab.engine.start_matlab()  # matlab.engine.start_matlab("-desktop")

        # -----------------------------------------------------------------------------------------------------------
        ## Adding Legacy Code Paths to Matlab Engine 
        # -----------------------------------------------------------------------------------------------------------
        
        ## Getting relevant paths for Legacy Code    
        CodeFromSWEEFA_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "CodeFromSWEEFA")
        Controllers_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "Controllers")
        Devices_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "Devices")
        LoadData_Extractor_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "LoadData_Extractor")
        PerformanceMetrics_Computer_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "PerformanceMetrics_Computer")
        Plant_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "Plant")
        Visualization_Generator_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "Visualization_Generator")
        WeatherData_Extractor_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "WeatherData_Extractor")

        ## Adding Paths to MATLAB Session
        eng.addpath(CodeFromSWEEFA_FolderPath, nargout=0)
        eng.addpath(Controllers_FolderPath, nargout=0)
        eng.addpath(Devices_FolderPath, nargout=0)
        eng.addpath(LoadData_Extractor_FolderPath, nargout=0)
        eng.addpath(PerformanceMetrics_Computer_FolderPath, nargout=0)
        eng.addpath(Plant_FolderPath, nargout=0)
        eng.addpath(Visualization_Generator_FolderPath, nargout=0)
        eng.addpath(WeatherData_Extractor_FolderPath, nargout=0)     

        
        # -----------------------------------------------------------------------------------------------------------
        ## Create Results Folders 
        # -----------------------------------------------------------------------------------------------------------

        # Creating Results Folder
        os.makedirs(result_filefolder_paths["Results_FolderPath"], exist_ok=True)
        WeatherData_Results_FolderPath = os.path.join(result_filefolder_paths["Results_FolderPath"], "WeatherData")
        LoadData_Results_FolderPath = os.path.join(result_filefolder_paths["Results_FolderPath"], "LoadData")
        SimulationData_Results_FolderPath = os.path.join(result_filefolder_paths["Results_FolderPath"], "SimulationData")
        SimulationPerformanceData_Results_FolderPath = os.path.join(result_filefolder_paths["Results_FolderPath"], "PerformanceData")
        SimulationPlots_Results_FolderPath = os.path.join(result_filefolder_paths["Results_FolderPath"], "Plots")

        # List of directories to create
        folders_to_create = [
            WeatherData_Results_FolderPath,
            LoadData_Results_FolderPath,
            SimulationData_Results_FolderPath,
            SimulationPerformanceData_Results_FolderPath,
            SimulationPlots_Results_FolderPath
        ]

        # Create each folder if it doesn't exist
        for folder in folders_to_create:
            os.makedirs(folder, exist_ok=True)  # Creates the folder if it doesn't exist
            print(f"Checked/Created: {folder}")  # Print confirmation

        # -----------------------------------------------------------------------------------------------------------
        ## Basic Computation 
        # -----------------------------------------------------------------------------------------------------------
                
        # Computed values (not in dicts)
        simulation_params["Simulation_StepSize"] = simulation_params["FileRes"] / 60  # in Hours
        simulation_params["StepSize"] = simulation_params["FileRes"] * 60  # in Seconds

        # Computed Values
        N_House = sum(community_params.values())  # Total number of houses
        N_House_Vector = matlab.double([community_params["N_PV_Bat"], community_params["N_Bat"], community_params["N_PV"], community_params["N_None"]])

        # Computed Value
        Battery_Energy_Max = 13.5 * plant_initial_conditions["N1"]  # Tesla Battery Capacity * Factor

        # Computed Value
        simulation_period["EndTime"] = simulation_period["EndTime"] - (simulation_params["FileRes"] / 60)  # 24 - (FileRes in Hours)

        # -----------------------------------------------------------------------------------------------------------
        ## Initialize self - With Constructor Inputs
        # -----------------------------------------------------------------------------------------------------------
        
        self.simulation_params = simulation_params
        self.plant_initial_conditions = plant_initial_conditions
        self.plant_dynamic_params = plant_dynamic_params
        self.simulation_period = simulation_period
        self.data_paths = data_paths
        self.result_filefolder_paths = result_filefolder_paths
        self.result_filefolder_paths["ImageFolder_Name"] = result_filefolder_paths["Plot_FileName_Stem"]

        self.ObservationSpace_Function = simulation_ObservationActionSpace_Functions["ObservationSpace_Function"]
        self.ActionSpace_Function = simulation_ObservationActionSpace_Functions["ActionSpace_Function"]
        self.Observation_Generator_Function = simulation_ObservationActionSpace_Functions["Observation_Generator_Function"]
        self.Action_Generator_Function = simulation_ObservationActionSpace_Functions["Action_Generator_Function"]

        self.Reward_Function = simulation_RewardTerminateTruncate_Functions["Reward_Function"]
        self.Terminate_Function = simulation_RewardTerminateTruncate_Functions["Terminate_Function"]
        self.Truncate_Function = simulation_RewardTerminateTruncate_Functions["Truncate_Function"]

        self.Community_Params = community_params
        self.Community_Params["N_House"] = N_House
        self.Community_Params["N_House_Vector"] = N_House_Vector

        self.Community_Params["N_House_Vector"] = N_House_Vector

        
        self.History_Flag = self.simulation_params["History_Flag"]  # Captures State Action Histories if True

        # MATLAB Engine
        self.eng = eng
        # Time Iter
        self.time_iter = 0

        # SimData and SimPerformanceData File Paths updated to self
        self.SimData_FilePath = os.path.join(result_filefolder_paths["Results_FolderPath"], "SimulationData", result_filefolder_paths["SimulationData_FileName"] + ".mat")
        self.SimPerformanceData_FilePath = os.path.join(result_filefolder_paths["Results_FolderPath"], "PerformanceData", result_filefolder_paths["SimulationPerformanceData_FileName"] + ".mat" )
                
        # -----------------------------------------------------------------------------------------------------------
        ## Weather Data Extraction 
        # -----------------------------------------------------------------------------------------------------------

        self._Process_WeatherData_Func()

        # Updating self with Weather Data
        self.Ws = self.HEMSWeatherData_Output["Ws"]
        self.T_am = self.HEMSWeatherData_Output["T_am"]
        self.GHI = self.HEMSWeatherData_Output["GHI"]
        self.DNI = self.HEMSWeatherData_Output["DNI"]
        self.DateTimeVector = self.HEMSWeatherData_Output["DateTimeVector"]
        self.DateTime_Matrix = self.HEMSWeatherData_Output["DateTime_Matrix"]

        self.Simulation_Steps_Total = len(self.DateTime_Matrix)

        # -----------------------------------------------------------------------------------------------------------
        ## Load Data Extraction 
        # -----------------------------------------------------------------------------------------------------------

        self._Process_LoadData_Func()

        # -----------------------------------------------------------------------------------------------------------
        ## Plant Parameter Generation
        # -----------------------------------------------------------------------------------------------------------

        self._Plant_ParameterGenerator_Func()

        # -----------------------------------------------------------------------------------------------------------
        ## Plant State Initialization
        # -----------------------------------------------------------------------------------------------------------

        self._Plant_StateInitialization_Func()

        if (self.History_Flag):

            # Update self with X_k_Plant_History
            self.X_k_Plant_History = self.X_k_Plant

        # -----------------------------------------------------------------------------------------------------------
        ## Plant Action Initialization
        # -----------------------------------------------------------------------------------------------------------

        self._Plant_ActionHistoryInitialization_Func()

        # -----------------------------------------------------------------------------------------------------------
        ## Plant Disturbance Initialization
        # -----------------------------------------------------------------------------------------------------------

        self._Plant_DisturbanceGenerator_Func()

        # -----------------------------------------------------------------------------------------------------------
        ## Plant Energy Price Generator
        # -----------------------------------------------------------------------------------------------------------

        freq = str(int(round(self.simulation_params["FileRes"] * 60))) + "s"

        self._Plant_generate_normalized_price_period(freq = freq)    

        # -----------------------------------------------------------------------------------------------------------
        ## Defining Action and Observation Spaces 
        # -----------------------------------------------------------------------------------------------------------

        if (self.simulation_params["ObservationSpace_Type"] == "Default"):  # Default

            # Define observation space (state x)
            self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(1,39,N_House), dtype=np.float32)

        else:  # User-Defined

            # Define observation space (state x)
            self.observation_space = self.SmartCommunity_ObservationSpace_Func()    

        if (self.simulation_params["ActionSpace_Type"] == "Default"):  # Default

            # Define action space (continuous control input u)
            self.action_space = spaces.Box(low=-np.inf, high=np.inf, shape=(1,13,N_House), dtype=np.float32)
            
        else:  # User-Defined

            # Define action space (continuous control input u)
            self.action_space = self.SmartCommunity_ActionSpace_Func()

        # -----------------------------------------------------------------------------------------------------------
        ## Initialize self More
        # -----------------------------------------------------------------------------------------------------------
               

    def step(self, action):
        """
        Takes one step in the environment.

        Parameters:
            action (np.array): Control input (u).
        
        Returns:
            observation (np.array): Next state.
            reward (float): Reward signal.
            done (bool): Whether episode is terminated.
            truncated (bool): Whether episode was truncated.
            info (dict): Additional debug info.
        """

        print("Time Iter = " + str(self.time_iter))

        # -----------------------------------------------------------------------------------------------------------
        ## Action Validation (If Required)
        # -----------------------------------------------------------------------------------------------------------
        
        # Updating self with action
        self.Action = action

        # Observation: Part of the State of System
        if (self.simulation_params["ActionSpace_Type"] == "Default"):  # Default

            # Action Computation
            U_k = matlab.double(action.tolist())

        else:  # User-Defined

            # Action Computation
            U_k = matlab.double(self.SmartCommunity_Action_Generator_Func(action).tolist())      

        # -----------------------------------------------------------------------------------------------------------
        ## Observation (t)/Reward/Termination/Truncation - Generation
        # -----------------------------------------------------------------------------------------------------------
           
        # Observation: Part of the State of System
        if (self.simulation_params["ObservationSpace_Type"] == "Default"):  # Default

            # Observation Computation (Adhering to Default State Space)
            observation_k_0 = np.array(self.X_k_Plant)

        else:  # User-Defined

            # Observation Computation
            observation_k_0 = self.SmartCommunity_Observation_Generator_Func()  

        # Updating self with observation
        self.Observation_k_0 = observation_k_0
        
        # -----------------------------------------------------------------------------------------------------------
        ## System dynamics
        # -----------------------------------------------------------------------------------------------------------

        # Updating System State
        if self.simulation_params["Simulation_ModeType"] == 0:  # Off-Grid Mode

            X_k_Plus_Plant = self.eng.HEMS_Plant_OffGrid(self.X_k_Plant, self.W_k_Plant, U_k, self.HEMSPlant_Params, self.HEMSHouse_Params, self.Community_Params, self.simulation_params)

        elif self.simulation_params["Simulation_ModeType"] == 1:  # On-Grid Mode

            X_k_Plus_Plant = self.eng.HEMS_Plant_OnGrid(self.X_k_Plant, self.W_k_Plant, U_k, self.HEMSPlant_Params, self.HEMSHouse_Params, self.Community_Params, self.simulation_params)
            
        # Update X_k_Plant of self
        X_k_Plus_Plant = np.array(X_k_Plus_Plant)

        self.X_k_Plant = np.array(self.X_k_Plant)

        self.X_k_Plant[0, :, :] = X_k_Plus_Plant[1, :, :]

        self.X_k_Plant = matlab.double(self.X_k_Plant.tolist())

        # Update X_k_Plus_Plant of self
        self.X_k_Plus_Plant = matlab.double(X_k_Plus_Plant.tolist())

        # -----------------------------------------------------------------------------------------------------------
        ## Updating X_k_History
        # -----------------------------------------------------------------------------------------------------------

        X_k_Plus_Plant = np.array(X_k_Plus_Plant)

        if (self.History_Flag):

            self.X_k_Plant_History = np.array(self.X_k_Plant_History)            

            self.X_k_Plant_History = np.concatenate((self.X_k_Plant_History[:self.time_iter, :, :], X_k_Plus_Plant), axis=0)

            # Convert back to `matlab.double`
            self.X_k_Plant_History = matlab.double(self.X_k_Plant_History.tolist())      

        # -----------------------------------------------------------------------------------------------------------
        ## Updating U_k_History
        # -----------------------------------------------------------------------------------------------------------

        U_k = np.array(U_k)

        if (self.History_Flag):

            self.U_k_History = np.array(self.U_k_History)            

            self.U_k_History = np.concatenate((self.U_k_History[:self.time_iter, :, :], U_k), axis=0)

            # Convert back to `matlab.double`
            self.U_k_History = matlab.double(self.U_k_History.tolist())   
        
        # -----------------------------------------------------------------------------------------------------------
        ## Updating W_k_Plant
        # -----------------------------------------------------------------------------------------------------------
        
        # Updating Time Iter
        self.time_iter  = self.time_iter + 1  

        if (self.time_iter+1 <= self.Simulation_Steps_Total):

            self._Plant_DisturbanceGenerator_Func()

        else:

            # self.reset(seed=None, options=None) 
            z = None     

        # -----------------------------------------------------------------------------------------------------------
        ## Observation (t+1)/Reward/Termination/Truncation - Generation
        # -----------------------------------------------------------------------------------------------------------
           
        # Observation: Part of the State of System
        if (self.simulation_params["ObservationSpace_Type"] == "Default"):  # Default

            # Observation Computation (Adhering to Default State Space)
            observation_k_1 = np.array(self.X_k_Plant)

        else:  # User-Defined

            # Observation Computation
            observation_k_1 = self.SmartCommunity_Observation_Generator_Func()

        # Updating self with observation
        self.Observation_k_1 = observation_k_1

        # Reward: Encourage reaching the target
        reward = self.SmartCommunity_Reward_Func(observation_k_1, action, observation_k_0)

        # Termination condition (Episode terminated due to internal reasons)
        terminated = self.SmartCommunity_Termination_Func()

        # Truncation Codition (Episode truncated due to external reasons)
        truncated = self.SmartCommunity_Truncation_Func()  

        return observation_k_1, reward, terminated, truncated, {}

    def reset(self, seed=None, options=None):
        """
        Resets the environment for a new episode.

        Uses the provided seed (if any) to sample a random starting
        time index between 0 and 90% of the total simulation steps.

        Returns:
            observation (np.array): Initial state.
            info (dict): Additional info (empty here).
        """
        # Let Gymnasium handle seeding
        super().reset(seed=seed)

        # ----------------------------------------------------------------------------------
        # Choose a random starting time index: 0 <= start_step < 0.9 * Total_Steps
        # ----------------------------------------------------------------------------------
        total_steps = int(self.Simulation_Steps_Total)

        if total_steps <= 0:
            # Fallback: nothing to sample from
            start_step = 0
        else:
            max_start = max(1, int(0.9 * total_steps))  # ensure at least 1
            # self.np_random is set by super().reset(seed=seed)
            start_step = int(self.np_random.integers(low=0, high=max_start))

        # Set internal time iterator to this random offset
        self.time_iter = start_step

        # ----------------------------------------------------------------------------------
        # Plant State Initialization
        # ----------------------------------------------------------------------------------
        self._Plant_StateInitialization_Func()

        if (self.History_Flag): 

            # Initialize state history with current state
            self.X_k_Plant_History = self.X_k_Plant

        # ----------------------------------------------------------------------------------
        # Plant Action Initialization
        # ----------------------------------------------------------------------------------
        self._Plant_ActionHistoryInitialization_Func()

        # ----------------------------------------------------------------------------------
        # Plant Disturbance Initialization
        #   - This uses self.time_iter, so it will pull Ws/T_am/GHI/DNI and load data
        #     corresponding to the sampled start_step.
        # ----------------------------------------------------------------------------------
        self._Plant_DisturbanceGenerator_Func()

        # ----------------------------------------------------------------------------------
        # Observation - Generation
        # ----------------------------------------------------------------------------------
        if self.simulation_params["ObservationSpace_Type"] == "Default":
            # Observation Computation (Adhering to Default State Space)
            observation = np.array(self.X_k_Plant)
        else:
            # User-Defined
            observation = self.SmartCommunity_Observation_Generator_Func()

        return observation, {}

    
    def SmartCommunity_ObservationSpace_Func(self):
        """
        Computes Observation Space. (User-Defined)
        """

        ObservationSpace = self.ObservationSpace_Function(self)

        return ObservationSpace
    
    def SmartCommunity_ActionSpace_Func(self):
        """
        Computes Action Space for the Environment. (User-Defined)
        """

        ActionSpace  = self.ActionSpace_Function(self)

        return ActionSpace
    
    def SmartCommunity_Observation_Generator_Func(self):
        """
        Computes Observation for the Environment. (User-Defined)
        """

        Observation  = self.Observation_Generator_Function(self)

        return Observation
    
    def SmartCommunity_Action_Generator_Func(self, Action):
        """
        Computes Action for the Environment. (User-Defined)
        """

        Action  = self.Action_Generator_Function(self, Action)

        return Action
    
    def SmartCommunity_Reward_Func(self, observation_k_1, action, observation_k_0):
        """
        Computes Reward for the Environment. (User-Defined)
        """

        if (self.Reward_Function == None):

            Reward = 0.0

        else:
        
            Reward = self.Reward_Function(self, observation_k_1, action, observation_k_0)

        return Reward

    def SmartCommunity_Termination_Func(self):
        """
        Terminates the environment. (User-Defined)
        """

        if (self.Terminate_Function == None):

            Termination_Bool = False

        else:
        
            Termination_Bool = self.Terminate_Function(self)

        return Termination_Bool

    def SmartCommunity_Truncation_Func(self):
        """
        Truncates the environment. (User-Defined)
        """

        if (self.Truncate_Function == None):

            Truncation_Bool = False

        else:
        
            Truncation_Bool = self.Truncate_Function(self)

        return Truncation_Bool

    def SmartCommunity_SimData_Func(self):
        """
        Saves Simulation Data.
        """

        # Convert Python dictionaries to MATLAB structs
        X_k_Plant_History_mat = self.X_k_Plant_History
        U_k_History_mat = self.U_k_History
        E_LoadData_mat = self.E_LoadData

        E_Load_Desired_mat = self.E_Load_Desired_Array
        HEMSWeatherData_Output_mat = self.HEMSWeatherData_Output
        HEMSPlant_Params_mat = self.HEMSPlant_Params

        Community_Params_mat = self.Community_Params
        Simulation_Params_mat = self.simulation_params

        result_filefolder_paths_mat = self.result_filefolder_paths

        # Call the MATLAB function
        self.eng.SmartCommunity_SimData_Func(X_k_Plant_History_mat, U_k_History_mat, E_LoadData_mat, E_Load_Desired_mat, HEMSWeatherData_Output_mat, HEMSPlant_Params_mat, Community_Params_mat, Simulation_Params_mat, result_filefolder_paths_mat, nargout=0)

        return None

    def SmartCommunity_PerformanceComputer_Func(self):
        """
        Computes Performance of the Simulation.
        """
        # Convert Python dictionaries to MATLAB structs
        X_k_Plant_History_mat = self.X_k_Plant_History
        U_k_History_mat = self.U_k_History
        E_LoadData_mat = self.E_LoadData

        E_Load_Desired_mat = self.E_Load_Desired_Array
        HEMSWeatherData_Output_mat = self.HEMSWeatherData_Output
        HEMSPlant_Params_mat = self.HEMSPlant_Params

        Community_Params_mat = self.Community_Params

        result_filefolder_paths_mat = self.result_filefolder_paths

        Simulation_Params_mat = self.simulation_params

        # Call the MATLAB function
        Plant_Performance  = self.eng.SmartCommunity_PerformanceComputer_Func(X_k_Plant_History_mat, U_k_History_mat, E_LoadData_mat, E_Load_Desired_mat, HEMSWeatherData_Output_mat, HEMSPlant_Params_mat, Community_Params_mat, result_filefolder_paths_mat, Simulation_Params_mat)

        # Plant_Performance  = self.eng.SmartCommunity_PerformanceComputer_Func(X_k_Plant_History_mat, U_k_History_mat, E_LoadData_mat, E_Load_Desired_mat, HEMSWeatherData_Output_mat, HEMSPlant_Params_mat, Community_Params_mat, result_filefolder_paths_mat, Simulation_Params_mat, nargout=0)

        ########################## Update ############################

        # Convert MATLAB Performance Struct to Python DF and svae as CSV
        Performance_DF = self._Plant_Performance_DF(Plant_Performance, result_filefolder_paths_mat)

        return Performance_DF

    def render(self, minimal="Yes"):
        """
        Renders the environment.
        """

        # Convert Python dictionaries to MATLAB structs
        X_k_Plant_History_mat = self.X_k_Plant_History
        U_k_History_mat = self.U_k_History
        E_LoadData_mat = self.E_LoadData

        E_Load_Desired_mat = self.E_Load_Desired_Array
        HEMSWeatherData_Output_mat = self.HEMSWeatherData_Output
        HEMSPlant_Params_mat = self.HEMSPlant_Params

        Community_Params_mat = self.Community_Params
        Simulation_Params_mat = self.simulation_params

        result_filefolder_paths_mat = self.result_filefolder_paths

        # Call the MATLAB function
        self.eng.SmartCommunity_FigurePlotter_Func(X_k_Plant_History_mat, U_k_History_mat, E_LoadData_mat, E_Load_Desired_mat, HEMSWeatherData_Output_mat, HEMSPlant_Params_mat, Community_Params_mat, Simulation_Params_mat, result_filefolder_paths_mat, minimal, nargout=0)


        return None

    def close(self):
        """
        Closes the environment.
        """

        # Close MATLAB Engine
        self.eng.quit()

        return None
    
    def _Process_WeatherData_Func(self):

        # Convert Python dictionaries to MATLAB structs
        simulation_params_mat = self.simulation_params
        simulation_period_mat = self.simulation_period
        data_paths_mat = self.data_paths
        result_filefolder_paths_mat = self.result_filefolder_paths

        # Call the MATLAB function
        HEMSWeatherData_Output, HEMSWeatherData_Input = self.eng.Process_WeatherData_Func(simulation_params_mat, simulation_period_mat, data_paths_mat, result_filefolder_paths_mat, nargout=2)

        # Updating self
        self.HEMSWeatherData_Output = HEMSWeatherData_Output
        self.HEMSWeatherData_Input = HEMSWeatherData_Input

        return None
    
    def _Process_LoadData_Func(self):

        # Convert Python dictionaries to MATLAB structs
        simulation_params_mat = self.simulation_params
        data_paths_mat = self.data_paths
        result_filefolder_paths_mat = self.result_filefolder_paths
        community_params_mat = self.Community_Params

        # HEMSWeatherData_Input must be passed from a previous function (assumed to exist)
        # HEMSWeatherData_Input_mat = self.HEMSWeatherData_Input  
        HEMSWeatherData_Output_mat = self.HEMSWeatherData_Output  # For updated Load Data Extraction

        # Call the MATLAB function
        E_LoadData, E_Load_Desired, E_Load_Desired_Array = self.eng.Process_LoadData_Func(simulation_params_mat, data_paths_mat, result_filefolder_paths_mat, HEMSWeatherData_Output_mat, community_params_mat, nargout=3)        

        # Updating self
        self.E_LoadData = E_LoadData
        self.E_Load_Desired = E_Load_Desired
        self.E_Load_Desired_Array = E_Load_Desired_Array

        return None
    
    def _Plant_ParameterGenerator_Func(self):

        # Getting some plant_dynamic_params in correct format for legacy code
        self.plant_dynamic_params["hem"] = -1.0 if self.plant_dynamic_params["Long"] < 0 else 1.0
        self.plant_dynamic_params["Long"] = abs(self.plant_dynamic_params["Long"])
        self.plant_dynamic_params["Ltm"] = abs(self.plant_dynamic_params["Ltm"])
        
        # Convert Python dictionaries to MATLAB structs
        simulation_params_mat = self.simulation_params
        plant_dynamic_params_mat = self.plant_dynamic_params
        Community_Params_mat = self.Community_Params  

        # Call the MATLAB function
        HEMSPlant_Params, HEMSHouse_Params = self.eng.HEMS_CommunityHouse_Parameter_Generator_Dynamic(Community_Params_mat,simulation_params_mat, plant_dynamic_params_mat, nargout=2)       

        # Updating self
        self.HEMSPlant_Params = HEMSPlant_Params
        self.HEMSHouse_Params = HEMSHouse_Params

        return None
    
    def _Plant_StateInitialization_Func(self):

        # Convert Python dictionaries to MATLAB structs
        simulation_params_mat = self.simulation_params
        community_params_mat = self.Community_Params
        plant_initial_conditions_mat = self.plant_initial_conditions
        HEMSPlant_Params_mat = self.HEMSPlant_Params

        # Call the MATLAB function
        X_k_Plant = self.eng.HEMS_Plant_StateInitialization_Func(simulation_params_mat, community_params_mat, plant_initial_conditions_mat, HEMSPlant_Params_mat)
        
        # Updating self
        self.X_k_Plant = X_k_Plant

        return None
    
    def _Plant_ActionHistoryInitialization_Func(self):

        # Convert Python dictionaries to MATLAB structs
        simulation_params_mat = self.simulation_params
        community_params_mat = self.Community_Params

        # Call the MATLAB function
        U_k_History = self.eng.HEMS_Plant_ActionHistoryInitialization_Func(simulation_params_mat, community_params_mat)

        if (self.History_Flag):

            # Updating self
            self.U_k_History = U_k_History

        return None
    
    def _Plant_DisturbanceGenerator_Func(self):

        # Weather Data
        Ws = self.Ws
        T_am = self.T_am
        GHI = self.GHI
        DNI = self.DNI
        DateTime_Matrix = self.DateTime_Matrix

        # Load Data
        E_Load_Desired = self.E_Load_Desired
        E_LoadData = self.E_LoadData

        # Time Iter
        Time_Iter  =self.time_iter

        # Call MATLAB function
        W_k_Plant = self.eng.HEMS_Plant_DisturbanceGenerator_Func(Ws, T_am, GHI, DNI, DateTime_Matrix, E_Load_Desired, E_LoadData, Time_Iter)

        # Updating self
        self.W_k_Plant = W_k_Plant

        return None
    
    def _Plant_Performance_DF(self, Plant_Performance, result_filefolder_paths_mat):

        ########################## Update ############################

        # ------------------------------------------------------------
        # 1. Extract fields from MATLAB struct returned to Python
        # ------------------------------------------------------------
        perf = Plant_Performance   # MATLAB struct proxy

        perf_dict = {
            "AC_Death_AvgPerDay": perf["AC_Death_AvgPerDay"],
            "Percentage_All_Served": perf["Percentage_All_Served"],
            "Percentage_C_Served": perf["Percentage_C_Served"],
            "TRM": perf["TRM"],
            "LRM_C": perf["LRM_C"],
            "LRM_O": perf["LRM_O"],

            "AC_Death_AvgPerDay_Community": perf["AC_Death_AvgPerDay_Community"],
            "Percentage_All_Served_Community": perf["Percentage_All_Served_Community"],
            "Percentage_C_Served_Community": perf["Percentage_C_Served_Community"],
            "TRM_Community": perf["TRM_Community"],
            "LRM_C_Community": perf["LRM_C_Community"],
            "LRM_O_Community": perf["LRM_O_Community"],
        }

        # ------------------------------------------------------------
        # 2. Helper: unwrap MATLAB values (matlab.double) into scalars
        # ------------------------------------------------------------
        def unwrap(val):
            # matlab.double comes as nested lists: [[value]]
            if isinstance(val, (list, tuple)) and len(val) == 1:
                inner = val[0]
                if isinstance(inner, (list, tuple)) and len(inner) == 1:
                    return inner[0]  # extract scalar
            return val  # fallback

        # Apply unwrap to every value
        perf_dict = {k: unwrap(v) for k, v in perf_dict.items()}

        # ------------------------------------------------------------
        # 3. Build DataFrame
        # ------------------------------------------------------------
        df_perf = pd.DataFrame([perf_dict])

        # ------------------------------------------------------------
        # 4. Transpose
        # ------------------------------------------------------------
        df_perf_T = df_perf.transpose()

        # ------------------------------------------------------------
        # 5. Reset index & rename columns
        # ------------------------------------------------------------
        df_perf_T = df_perf_T.reset_index()
        df_perf_T.columns = ["Metric", "Value"]

        # ------------------------------------------------------------
        # 6. Final DataFrame ready to use
        # ------------------------------------------------------------
        print(df_perf_T)

        # ------------------------------------------------------------
        # 6. Save Performance Dataframe
        # ------------------------------------------------------------

        csv_file_path = os.path.join(
            result_filefolder_paths_mat["Results_FolderPath"],
            "PerformanceData",
            result_filefolder_paths_mat["SimulationPerformanceData_FileName"] + ".csv"
        )

        df_perf_T.to_csv(csv_file_path, index=False)

        return df_perf_T
    
        


    def _Plant_daily_base_shape(self, time_decimal: np.ndarray) -> np.ndarray:
        """
        Base normalized daily curve (0–1) based only on Time of Day.
        """
        t = time_decimal % 24.0

        # Two-peak daily curve (midday + evening)
        mid = np.exp(-0.5 * ((t - 14.0) / 2.5) ** 2)
        eve = np.exp(-0.5 * ((t - 19.0) / 1.5) ** 2)

        raw = 0.2 + 0.5 * mid + 0.7 * eve
        raw = (raw - raw.min()) / (raw.max() - raw.min())
        return raw


    def _Plant_generate_normalized_price_period(self,
        freq: str = "5min",       # <--- USER CONTROLLED
        noise_std: float = 0.05,
        seed: int | None = None,
    ):
        """
        Generate normalized price values over a custom simulation window.

        Output array columns:
            [Day, Month, Year, TimeDecimal, Value]

        Parameters
        ----------
        simulation_period : dict
            Required keys:
                StartYear, StartMonth, StartDay, StartTime
                EndYear, EndMonth, EndDay, EndTime
        freq : str
            Pandas-compatible frequency string ("5min", "15min", "1H", "30s", etc.)
        noise_std : float
            Gaussian noise standard deviation.
        seed : int or None
            RNG seed.
        """

        rng = np.random.default_rng(seed)

        simulation_period = self.simulation_period

        # ---- Build timestamp range ----
        start_ts = f"{simulation_period['StartYear']}-{simulation_period['StartMonth']:02d}-{simulation_period['StartDay']:02d} {simulation_period['StartTime']}:00"
        end_ts   = f"{simulation_period['EndYear']}-{simulation_period['EndMonth']:02d}-{simulation_period['EndDay']:02d} {simulation_period['EndTime']}:00"

        # Handle “24.0” end times (meaning end-of-day -> exclusive)
        inclusive_setting = "left" if simulation_period["EndTime"] == 24 else "right"

        dt_index = pd.date_range(
            start=start_ts,
            end=end_ts,
            freq=freq,
            inclusive=inclusive_setting
        )

        # ---- Extract calendar fields ----
        day = dt_index.day.values
        month = dt_index.month.values
        year = dt_index.year.values

        # ---- Decimal hour ----
        time_decimal = (
            dt_index.hour +
            dt_index.minute / 60.0 +
            dt_index.second / 3600.0
        )

        # ---- Base price + noise ----
        base = self._Plant_daily_base_shape(time_decimal)
        noise = rng.normal(loc=0.0, scale=noise_std, size=len(base))
        value = np.clip(base + noise, 0.0, 1.0)

        # ---- Final array ----
        Energy_Price = np.column_stack([day, month, year, time_decimal, value])

        # ---- Updating self ----
        self.Energy_Price = Energy_Price

        print("Done - Generating Energy Price Data")
        
        return None



