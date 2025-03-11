###############################################################################################################
## Import Desired Packages
###############################################################################################################

import os
import matlab.engine
import gymnasium as gym
from gymnasium import spaces
import numpy as np
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
        eng = matlab.engine.start_matlab("-desktop")  # matlab.engine.start_matlab("-desktop")

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
            self.action_space = self.SmartCommunity_ActionSpace_Func(self)

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
            U_k = self.SmartCommunity_Action_Generator_Func(action)        
        
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

        self.X_k_Plant_History = np.array(self.X_k_Plant_History)
        X_k_Plus_Plant = np.array(X_k_Plus_Plant)

        self.X_k_Plant_History = np.concatenate((self.X_k_Plant_History[:self.time_iter, :, :], X_k_Plus_Plant), axis=0)

        # Convert back to `matlab.double`
        self.X_k_Plant_History = matlab.double(self.X_k_Plant_History.tolist())      

        # -----------------------------------------------------------------------------------------------------------
        ## Updating U_k_History
        # -----------------------------------------------------------------------------------------------------------

        self.U_k_History = np.array(self.U_k_History)
        U_k = np.array(U_k)

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
        ## Observation/Reward/Termination/Truncation - Generation
        # -----------------------------------------------------------------------------------------------------------
           
        # Observation: Part of the State of System
        if (self.simulation_params["ObservationSpace_Type"] == "Default"):  # Default

            # Observation Computation (Adhering to Default State Space)
            observation = np.array(self.X_k_Plant)

        else:  # User-Defined

            # Observation Computation
            observation = self.SmartCommunity_Observation_Generator_Func()

        # Updating self with observation
        self.Observation = observation

        # Reward: Encourage reaching the target
        reward = self.SmartCommunity_Reward_Func()

        # Termination condition (Episode terminated due to internal reasons)
        terminated = self.SmartCommunity_Termination_Func()

        # Truncation Codition (Episode truncated due to external reasons)
        truncated = self.SmartCommunity_Truncation_Func()  

        return observation, reward, terminated, truncated, {}

    def reset(self, seed=None, options=None):
        """
        Resets the environment for a new episode.

        Returns:
            observation (np.array): Initial state.
            info (dict): Additional info (empty here).
        """
        # Resetting Time Iter
        self.time_iter = 0

        # -----------------------------------------------------------------------------------------------------------
        ## Plant State Initialization
        # -----------------------------------------------------------------------------------------------------------

        self._Plant_StateInitialization_Func()

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
        ## Observation - Generation
        # -----------------------------------------------------------------------------------------------------------
           
        # Observation: Part of the State of System
        if (self.simulation_params["ObservationSpace_Type"] == "Default"):  # Default

            # Observation Computation (Adhering to Default State Space)
            observation = np.array(self.X_k_Plant)

        else:  # User-Defined

            # Observation Computation
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
    
    def SmartCommunity_Reward_Func(self):
        """
        Computes Reward for the Environment. (User-Defined)
        """

        if (self.Reward_Function == None):

            Reward = 0.0

        else:
        
            Reward = self.Reward_Function(self)

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
        self.eng.SmartCommunity_PerformanceComputer_Func(X_k_Plant_History_mat, U_k_History_mat, E_LoadData_mat, E_Load_Desired_mat, HEMSWeatherData_Output_mat, HEMSPlant_Params_mat, Community_Params_mat, result_filefolder_paths_mat, Simulation_Params_mat, nargout=0)

        return None

    def render(self):
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
        self.eng.SmartCommunity_FigurePlotter_Func(X_k_Plant_History_mat, U_k_History_mat, E_LoadData_mat, E_Load_Desired_mat, HEMSWeatherData_Output_mat, HEMSPlant_Params_mat, Community_Params_mat, Simulation_Params_mat, result_filefolder_paths_mat, nargout=0)

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


