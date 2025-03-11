###############################################################################################################
## Import Desired Packages
###############################################################################################################

import os
import matlab.engine
import gymnasium as gym
from gymnasium import spaces
import numpy as np

###############################################################################################################
## Smart Community Default Controllers Class - Gymnasium
###############################################################################################################

class SmartCommunityDefaultController:
    def __init__(self, env, parameter_dict, disturbance_dict):
        """
        Initialize the policy with given parameters and disturbances.
        :param env: The gymnasium environment.
        :param parameter_dict: Dictionary containing controller, plant, community, and simulation parameters.
        :param disturbance_dict: Dictionary containing weather and load disturbances.
        """       

        # Setting MATLAB Engine from Environment to self
        self.eng = env.eng

        # Setting Environment to self
        self.env = env

        # Setting Controller Parameters to self
        self.SmartCommunity_ControllerType = parameter_dict["Controller_Parameters"]["SmartCommunity_ControllerType"]
        self.Simulation_ModeType = parameter_dict["Controller_Parameters"]["Simulation_ModeType"]

        # Setting Other Parameters to self
        self.HEMSPlant_Params = parameter_dict["Plant_Parameters"]
        self.Community_Params = parameter_dict["Community_Parameters"]
        self.Simulation_Params = parameter_dict["Simulation_Parameters"]
        
        # Setting Weather Disturbances to self
        self.Ws = disturbance_dict["Weather_Disturbance"]["Ws"]
        self.T_am = disturbance_dict["Weather_Disturbance"]["T_am"]
        self.GHI = disturbance_dict["Weather_Disturbance"]["GHI"]
        self.DNI = disturbance_dict["Weather_Disturbance"]["DNI"]

        # Setting Load Disturbances to self
        self.E_LoadData = disturbance_dict["Load_Disturbance"]["E_LoadData"]
        self.E_Load_Desired = disturbance_dict["Load_Disturbance"]["E_Load_Desired"]
    
    def act(self, observation):
        """
        Select an action based on the observation and internal parameters.
        :param observation: The current state observation from the environment.
        :return: Action to be taken.
        """

        # Creating current Time Iter Plant Disturbance
        W_k_Plant = self._Controller_DisturbanceGenerator_Func()

        # Getting other input for 
        Simulation_ModeType = self.Simulation_ModeType
        SmartCommunity_ControllerType = self.SmartCommunity_ControllerType         
        HEMSPlant_Params = self.HEMSPlant_Params
        Community_Params = self.Community_Params
        Simulation_Params = self.Simulation_Params

        # Getting Plant State
        X_k_Plant = matlab.double(observation.tolist())

        # Getting action from the Default Controller
        action = self.eng.HEMS_Controller_Func(Simulation_ModeType, SmartCommunity_ControllerType, X_k_Plant,W_k_Plant,HEMSPlant_Params,Community_Params,Simulation_Params, nargout=1)

        # Adhering to Default Action Space
        action = np.array(action)

        return action
    
    def _Controller_DisturbanceGenerator_Func(self):

        # Weather Data
        Ws = self.Ws
        T_am = self.T_am
        GHI = self.GHI
        DNI = self.DNI

        # Load Data
        E_Load_Desired = self.E_Load_Desired
        E_LoadData = self.E_LoadData

        # Time Iter
        Time_Iter  =self.env.time_iter

        # Call MATLAB function
        W_k_Plant = self.eng.HEMS_Controller_DisturbanceGenerator_Func(Ws, T_am, GHI, DNI, E_Load_Desired, E_LoadData, Time_Iter, nargout=1)

        return W_k_Plant
    
    