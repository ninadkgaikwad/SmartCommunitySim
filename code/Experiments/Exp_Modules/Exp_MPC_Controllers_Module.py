###############################################################################################################
## Import Desired Packages
###############################################################################################################

import sys
import os

import numpy as np
import casadi as ca

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

from Exp_MPC_RL_Helpers import *
from Exp_MPC_Solver_Options import *
from Exp_MPC_Optimization_Formulations_Module import *

###############################################################################################################
## Experiment MPC Controllers Module - Custom Functions
###############################################################################################################

#-------------------------------------------------------------------------------------------------------------#
# Single House Off-Grid RL
#-------------------------------------------------------------------------------------------------------------#

def SingleHouse_OffGrid_MPC_Controller(SmartComSim_Object, MPC_Parameters):

    """
    Single House Off-Grid MPC controller using CasADi (skeleton).

    SmartComSim_Object : SmartCommunitySimulator
        Running environment instance.
    MPC_Parameters : dict
        MPC configuration (horizon, weights, warm-start, solver options, etc.).
    """

    env = SmartComSim_Object
    
    # =================================================================================
    # =================================================================================
    # INTIIAL DATA GATHERING 
    # =================================================================================
    # =================================================================================

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_mpc_context(env, MPC_Parameters)

    Epsilon = ctx["Epsilon"]

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # RC disturbances + discrete-time model
    # =================================================================================

    RC_data = compute_singlehouse_RC_data_from_ctx(ctx) 

    T_sol_w = RC_data["T_sol_w"]
    T_sol_r = RC_data["T_sol_r"]
    Q_solar = RC_data["Q_solar"]

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_mpc_inputs(
        ctx      = ctx,
        E_PV     = E_PV,
        T_sol_w  = T_sol_w,
        T_sol_r  = T_sol_r,
        Q_solar  = Q_solar,
    )    
    
    # =================================================================================
    # =================================================================================
    # OPTIMIZATION PROBLEM FORMULATION AND SOLUTION
    # =================================================================================
    # =================================================================================

    Solution_Dict_np, Solution_Dict_List, Initial_DecisionVariables, N_House, N_PV_Bat, N_Bat, E_l_Array = Exp_SingleMultiHouse_OffGrid_NoFairness_GurobiPy_MPC_Formulation(ctx, RC_data, reshaped)
    
    # =================================================================================
    # =================================================================================
    # SOLUTION TO ACTION GENERATION
    # =================================================================================
    # =================================================================================

    Action = Exp_SingleMultiHouse_OffGrid_MPC_Sol_To_Action_Generator(Solution_Dict_np, N_House, N_PV_Bat, N_Bat, E_l_Array, Epsilon)


    return Action, Initial_DecisionVariables, Solution_Dict_np, Solution_Dict_List

#-------------------------------------------------------------------------------------------------------------#
# Single House On-Grid RL
#-------------------------------------------------------------------------------------------------------------#

def SingleHouse_OnGrid_MPC_Controller(SmartComSim_Object, MPC_Parameters):


    env = SmartComSim_Object
    
    # =================================================================================
    # =================================================================================
    # INTIIAL DATA GATHERING 
    # =================================================================================
    # =================================================================================

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_mpc_context(env, MPC_Parameters)

    Epsilon = ctx["Epsilon"]

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # RC disturbances + discrete-time model
    # =================================================================================

    RC_data = compute_singlehouse_RC_data_from_ctx(ctx)

    T_sol_w = RC_data["T_sol_w"]
    T_sol_r = RC_data["T_sol_r"]
    Q_solar = RC_data["Q_solar"]

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_mpc_inputs(
        ctx      = ctx,
        E_PV     = E_PV,
        T_sol_w  = T_sol_w,
        T_sol_r  = T_sol_r,
        Q_solar  = Q_solar,
    )

    # =================================================================================
    # =================================================================================
    # OPTIMIZATION PROBLEM FORMULATION AND SOLUTION
    # =================================================================================
    # =================================================================================

    Solution_Dict_np, Solution_Dict_List, Initial_DecisionVariables, N_House, N_PV_Bat, N_Bat, E_l_Array  = Exp_SingleMultiHouse_OnGrid_NoFairness_GurobiPy_MPC_Formulation(ctx, RC_data, reshaped)

    # =================================================================================
    # =================================================================================
    # SOLUTION TO ACTION GENERATION
    # =================================================================================
    # =================================================================================

    Action = Exp_SingleMultiHouse_OnGrid_MPC_Sol_To_Action_Generator(Solution_Dict_np, N_House, N_PV_Bat, N_Bat, E_l_Array, Epsilon)

    return Action, Initial_DecisionVariables, Solution_Dict_np, Solution_Dict_List

#-------------------------------------------------------------------------------------------------------------#
# Multi House Off-Grid RL
#-------------------------------------------------------------------------------------------------------------#

def MultiHouse_OffGrid_MPC_Controller(SmartComSim_Object, MPC_Parameters):


    env = SmartComSim_Object
    
    # =================================================================================
    # =================================================================================
    # INTIIAL DATA GATHERING 
    # =================================================================================
    # =================================================================================

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_mpc_context(env, MPC_Parameters)

    Epsilon = ctx["Epsilon"]

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # RC disturbances + discrete-time model
    # =================================================================================

    RC_data = compute_singlehouse_RC_data_from_ctx(ctx)

    T_sol_w = RC_data["T_sol_w"]
    T_sol_r = RC_data["T_sol_r"]
    Q_solar = RC_data["Q_solar"]

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_mpc_inputs(
        ctx      = ctx,
        E_PV     = E_PV,
        T_sol_w  = T_sol_w,
        T_sol_r  = T_sol_r,
        Q_solar  = Q_solar,
    )

    # =================================================================================
    # =================================================================================
    # OPTIMIZATION PROBLEM FORMULATION AND SOLUTION
    # =================================================================================
    # =================================================================================

    Solution_Dict_np, Solution_Dict_List, Initial_DecisionVariables, N_House, N_PV_Bat, N_Bat, E_l_Array  = Exp_SingleMultiHouse_OffGrid_NoFairness_GurobiPy_MPC_Formulation(ctx, RC_data, reshaped)

    # =================================================================================
    # =================================================================================
    # SOLUTION TO ACTION GENERATION
    # =================================================================================
    # =================================================================================

    Action = Exp_SingleMultiHouse_OffGrid_MPC_Sol_To_Action_Generator(Solution_Dict_np, N_House, N_PV_Bat, N_Bat, E_l_Array, Epsilon)

    return Action, Initial_DecisionVariables, Solution_Dict_np, Solution_Dict_List

#-------------------------------------------------------------------------------------------------------------#
# Multi House On-Grid RL
#-------------------------------------------------------------------------------------------------------------#

def MultiHouse_OnGrid_MPC_Controller(SmartComSim_Object, MPC_Parameters):


    env = SmartComSim_Object
    
    # =================================================================================
    # =================================================================================
    # INTIIAL DATA GATHERING 
    # =================================================================================
    # =================================================================================

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_mpc_context(env, MPC_Parameters)

    Epsilon = ctx["Epsilon"]

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # RC disturbances + discrete-time model
    # =================================================================================

    RC_data = compute_singlehouse_RC_data_from_ctx(ctx)

    T_sol_w = RC_data["T_sol_w"]
    T_sol_r = RC_data["T_sol_r"]
    Q_solar = RC_data["Q_solar"]

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_mpc_inputs(
        ctx      = ctx,
        E_PV     = E_PV,
        T_sol_w  = T_sol_w,
        T_sol_r  = T_sol_r,
        Q_solar  = Q_solar,
    )  

    # =================================================================================
    # =================================================================================
    # OPTIMIZATION PROBLEM FORMULATION AND SOLUTION
    # =================================================================================
    # =================================================================================

    Solution_Dict_np, Solution_Dict_List, Initial_DecisionVariables, N_House, N_PV_Bat, N_Bat, E_l_Array  = Exp_SingleMultiHouse_OnGrid_NoFairness_GurobiPy_MPC_Formulation(ctx, RC_data, reshaped)

    # =================================================================================
    # =================================================================================
    # SOLUTION TO ACTION GENERATION
    # =================================================================================
    # =================================================================================

    Action = Exp_SingleMultiHouse_OnGrid_MPC_Sol_To_Action_Generator(Solution_Dict_np, N_House, N_PV_Bat, N_Bat, E_l_Array, Epsilon)

    return Action, Initial_DecisionVariables, Solution_Dict_np, Solution_Dict_List