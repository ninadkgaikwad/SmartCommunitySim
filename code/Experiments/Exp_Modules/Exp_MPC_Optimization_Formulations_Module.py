###############################################################################################################
## Import Desired Packages
###############################################################################################################
import sys
import os

import gurobipy as gp
from gurobipy import GRB

import casadi as ca

import numpy as np
import pandas as pd

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

from MPC_Opt_Model_Diagnostics_Module import *

###############################################################################################################
## Experiment MPC Optimization Formulations - Custom Functions
###############################################################################################################

# =================================================================================
# Single-Multi House Off-Grid - No Fairness MPC Formulation - GurobiPy
# =================================================================================
def Exp_SingleMultiHouse_OffGrid_NoFairness_GurobiPy_MPC_Formulation(ctx, RC_data, reshaped):

    # =================================================================================
    # Unpack context for local use
    # =================================================================================

    # ---- Community sizes ----
    N_House   = ctx["N_House"]
    N_PV_Bat  = ctx["N_PV_Bat"]
    N_Bat     = ctx["N_Bat"]
    N_PV      = ctx["N_PV"]
    N_None    = ctx["N_None"]

    # ---- Initial states (at current MPC call) ----
    T_h_Init     = ctx["T_h_Init"]       # shape (N_House,)
    T_wall_Init  = ctx["T_wall_Init"]
    T_attic_Init = ctx["T_attic_Init"]
    T_im_Init    = ctx["T_im_Init"]

    E_bat_Init   = ctx["E_bat_Init"]     # shape (N_PV_Bat + N_Bat,)
    U_ac_Init    = ctx["U_ac_Init"]      # shape (N_House,)

    # ---- MPC horizon disturbances (W_k_MPC equivalent) ----
    E_l          = ctx["E_l"]             # desired load, horizon window
    E_l_Array    = ctx["E_l_Array"]       # full load stack per house

    Ws           = ctx["Ws"]
    T_am         = ctx["T_am"]
    GHI          = ctx["GHI"]
    DNI          = ctx["DNI"]

    Energy_Price = ctx["Energy_Price"]    

    # ---- Plant & house parameters ----
    # Full dicts if we ever need them:
    plant = ctx["plant"]
    house = ctx["house"]

    # Convenience scalars:
    T_h_Max              = ctx["T_h_Max"]
    T_h_Min              = ctx["T_h_Min"]
    Q_AC                 = ctx["Q_AC"]
    E_AC                 = ctx["E_AC"]
    ACLoad_StartUp_Power = ctx["ACLoad_StartUp_Power"]
    Eff_Inv              = ctx["Eff_Inv"]

    E_bat_Max            = ctx["E_bat_Max"]
    E_bat_Min            = ctx["E_bat_Min"]
    Gamma_Charging       = ctx["Gamma_Charging"]
    Gamma_Discharging    = ctx["Gamma_Discharging"]
    P_bat                = ctx["P_bat"]

    Q_ac                 = ctx["Q_ac"]   # house-level AC thermal power coeff

    # ---- MPC tuning and geometry ----
    N_horizon                 = ctx["N_horizon"]
    MPC_StepLengthUsed        = ctx["MPC_StepLengthUsed"]
    MPC_DecisionVariables_Num = ctx["MPC_DecisionVariables_Num"]
    Initial_DecisionVariables = ctx["Initial_DecisionVariables"]

    Lambda_T = ctx["Lambda_T"]
    Lambda_Bat = ctx["Lambda_Bat"]
    Lambda_E_l = ctx["Lambda_E_l"]
    Lambda_Theta = ctx["Lambda_Theta"]
    Lambda_E_cri = ctx["Lambda_E_cri"]
    Lambda_G = ctx["Lambda_G"]
    Lambda_PV = ctx["Lambda_PV"]

    Epsilon                     = ctx["Epsilon"]
    OpenLoop_Plotting_Indicator = ctx["OpenLoop_Plotting_Indicator"]

    # ---- Simulation step ----
    Simulation_StepSize = ctx["Simulation_StepSize"]

    # ---- Solver options (directly from MPC_Parameters, not in ctx yet) ----
    SolverOptions_Dict = GUROBI_OPTIONS_func()

    # ---- MPC Planning Horizon ----
    N = ctx["N_horizon"]

    # =================================================================================
    # RC disturbances + discrete-time model
    # =================================================================================

    Q_venti_Const = RC_data["Q_venti_Const"]
    Q_infil_Const = RC_data["Q_infil_Const"]

    Q_ihl   = RC_data["Q_ihl"]
    T_sol_w = RC_data["T_sol_w"]
    T_sol_r = RC_data["T_sol_r"]
    Q_solar = RC_data["Q_solar"]

    A_T_h   = RC_data["A_T_h"]
    B_T_h   = RC_data["B_T_h"]

    A_1 = A_T_h[0,0]
    A_2 = A_T_h[0,1]
    A_3 = A_T_h[1,0]
    A_4 = A_T_h[1,1]
    A_5 = A_T_h[1,2]
    A_6 = A_T_h[1,3]
    A_7 = A_T_h[2,1]
    A_8 = A_T_h[2,2]
    A_9 = A_T_h[3,1]
    A_10 = A_T_h[3,3]

    B_1 = B_T_h[0,1]
    B_2 = B_T_h[1,0]
    B_3 = B_T_h[1,3]
    B_4 = B_T_h[1,4]
    B_5 = B_T_h[1,5]
    B_6 = B_T_h[1,6]
    B_7 = B_T_h[2,2]
    B_8 = B_T_h[3,7]


    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    # ---- Unpack reshaped data ----
    T_h_Init     = reshaped["T_h_Init"]
    T_wall_Init  = reshaped["T_wall_Init"]
    T_attic_Init = reshaped["T_attic_Init"]
    T_im_Init    = reshaped["T_im_Init"]

    E_bat_Init   = reshaped["E_bat_Init"]
    U_ac_Init    = reshaped["U_ac_Init"]

    T_am         = reshaped["T_am"]
    Ws           = reshaped["Ws"]
    E_PV         = reshaped["E_PV"]          # now properly reshaped
    T_sol_w      = reshaped["T_sol_w"]
    T_sol_r      = reshaped["T_sol_r"]
    Q_solar      = reshaped["Q_solar"]
    Energy_Price = reshaped["Energy_Price"]

    E_Load_Critical_Reshaped = reshaped["E_Load_Critical_Reshaped"]
    E_l_Reshaped             = reshaped["E_l_Reshaped"]
    E_l_Array                = reshaped["E_l_Array_DC"]

    E_PV_Reshaped            = reshaped["E_PV_Reshaped"]

    Nh_all  = N_House
    Nh_bat  = N_PV_Bat + N_Bat
    Nh_pv   = N_PV_Bat + N_PV

    Continuous = False

    Model_Diagnostics = False

    m = gp.Model("MPC_community")


    # =================================================================================
    # Optimization Variables - Definitions With ub/lb
    # =================================================================================

    # ---- Thermal states (all houses) ----
    T_wall = m.addMVar(Nh_all * N, lb=-GRB.INFINITY, ub= GRB.INFINITY, name="T_wall")
    T_ave  = m.addMVar(Nh_all * N, lb=T_h_Min,   ub= GRB.INFINITY, name="T_ave")
    T_att  = m.addMVar(Nh_all * N, lb=-GRB.INFINITY, ub= GRB.INFINITY, name="T_att")
    T_im   = m.addMVar(Nh_all * N, lb=-GRB.INFINITY, ub= GRB.INFINITY, name="T_im")

    """ # ---- HVAC Control (Binary) ----
    if (Continuous):

        U_ac = m.addMVar(Nh_all * N, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="U_ac")    

    else:
        
        U_ac = m.addMVar(
            Nh_all * N,
            vtype=GRB.BINARY,
            name="U_ac"
        ) """
    

    # ---- Battery vars (only bat+pvbat) ----
    E_bat = m.addMVar(Nh_bat * N,
                    lb=E_bat_Min,
                    ub=E_bat_Max,
                    name="E_bat")

    Gamma = m.addMVar(Nh_bat * N,
                    lb=-1.52,
                    ub=1.0,
                    name="Gamma")
    if (Continuous):

        U_ac = m.addMVar(Nh_all * N, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="U_ac")

        theta_bat = m.addMVar(Nh_bat * N,
                        lb=0.0, ub=1.0,
                        vtype=GRB.CONTINUOUS, name="theta_bat")  # or BINARY
        
        f_on  = m.addMVar(Nh_all * N, lb=0.0, ub=1.0,
                    vtype=GRB.CONTINUOUS, name="f_on")  # or BINARY
        
        f_off = m.addMVar(Nh_all * N, lb=0.0, ub=1.0,
                    vtype=GRB.CONTINUOUS, name="f_off")  # or BINARY

    else:

        # ---- HVAC Control (Binary) ----
        U_ac = m.addMVar(
            Nh_all * N,
            vtype=GRB.BINARY,
            name="U_ac"
        )

        # ---- Battery Mode Binary Variables ----
        theta_bat = m.addMVar(
            Nh_bat * N,
            vtype=GRB.BINARY,
            name="theta_bat"
        )

        f_on = m.addMVar(
            Nh_all * N,
            vtype=GRB.BINARY,
            name="f_on"
        )

        f_off = m.addMVar(
            Nh_all * N,
            vtype=GRB.BINARY,
            name="f_off"
        )

    # g^h(k) – PV power use/export (off-grid version)
    lb_list = []
    ub_list = []

    for i in range(Nh_pv * N):
        lb_list.append(0.0)
        ub_list.append(E_PV_Reshaped[i,0])

    g = m.addMVar(Nh_pv * N, lb=lb_list, ub=ub_list,
                vtype=GRB.CONTINUOUS, name="g")

    # ---- Load and slack (all houses) ----
    lb_list = []
    ub_list = []

    for i in range(Nh_all * N):
        lb_list.append(0.0)
        ub_list.append(E_l_Reshaped[i,0])

    E_load = m.addMVar(Nh_all * N, lb=lb_list, ub=ub_list,
                    vtype=GRB.CONTINUOUS, name="E_load")

    eps_h = m.addMVar(Nh_all * N, lb=0.0, ub=GRB.INFINITY,
                    vtype=GRB.CONTINUOUS, name="eps_h")

    # eps_l lower bound conceptually = \bar E_cri(h,k)
    # In Gurobi, we keep lb = 0 and add constraints eps_l >= barE_cri(h,k)
    lb_list = []
    ub_list = []

    for i in range(Nh_all * N):
        lb_list.append(0.0)
        ub_list.append(E_Load_Critical_Reshaped[i,0])

    eps_l = m.addMVar(Nh_all * N, lb=lb_list, ub=ub_list,
                    vtype=GRB.CONTINUOUS, name="eps_l")

    # =================================================================================
    # Optimization Variables - Warm Start
    # =================================================================================

    T_wall.Start     = Initial_DecisionVariables["T_wall"]
    T_ave.Start      = Initial_DecisionVariables["T_ave"]
    T_att.Start      = Initial_DecisionVariables["T_att"]
    T_im.Start       = Initial_DecisionVariables["T_im"]

    U_ac.Start       = Initial_DecisionVariables["U_ac"]

    E_bat.Start      = Initial_DecisionVariables["E_bat"]
    Gamma.Start      = Initial_DecisionVariables["Gamma"]
    theta_bat.Start  = Initial_DecisionVariables["theta_bat"]
    f_on.Start       = Initial_DecisionVariables["f_on"]
    f_off.Start      = Initial_DecisionVariables["f_off"]

    g.Start          = Initial_DecisionVariables["g"]

    E_load.Start     = Initial_DecisionVariables["E_load"]
    eps_h.Start      = Initial_DecisionVariables["eps_h"]
    eps_l.Start      = Initial_DecisionVariables["eps_l"]

    # =================================================================================
    # Optimization Problem - Objective
    # =================================================================================

    # -------------------------- Single-House Off-Grid ---------------------------------- #

    obj = gp.LinExpr()

    # ---- 1. Terms for ALL HOUSES ----
    for h in range(Nh_all):
        for k in range(N):

            i = h*N + k     # flattened index for eps_h, eps_l, E_load
            weight = (N - k)

            obj += Lambda_T * weight * eps_h[i]
            obj += Lambda_E_cri * weight * eps_l[i]
            obj += -Lambda_E_l * weight * E_load[i]

    # ---- 2. Terms for BATTERY HOUSES ----
    for b in range(Nh_bat):
        for k in range(N):

            j = b*N + k     # flattened index for E_bat, theta_bat
            weight = (N - k)

            obj += -Lambda_Bat * E_bat[j]
            obj +=  Lambda_Theta * theta_bat[j]

    ### Setting up Objective
    # Set final objective
    m.setObjective(obj, GRB.MINIMIZE)   

    # =================================================================================
    # Optimization Problem - Constraints
    # =================================================================================

    # -------------------------- T_wall - Dynamics ---------------------------------- #

    for h in range(Nh_all):
        for k in range(N):  # k = 0..N_MPC-1, state at k+1

            i = h*N + k

            if (k == 0):

                m.addConstr(
                    T_wall[i] == A_1 * T_wall_Init[h,0] + A_2 * T_h_Init[h,0] + B_1 * T_sol_w[k,0],
                    name=f"T1_wall_h{h}_k{k}"
                )

            else:

                m.addConstr(
                    T_wall[i] == A_1 * T_wall[i-1] + A_2 * T_ave[i-1] + B_1 * T_sol_w[k,0],
                    name=f"T1_wall_h{h}_k{k}"
                )

    """ for h in range(Nh_all):
        for k in range(N-1):  # k = 0..N_MPC-1, state at k+1

            i = h*N + k

            m.addConstr(
                T_wall[i+1] == A_1 * T_wall[i] + A_2 * T_ave[i] + B_1 * T_sol_w[k],
                name=f"T1_wall_h{h}_k{k}"
            )

    for h in range(Nh_all):

        i = h*N

        m.addConstr(T_wall[i] == T_wall_Init[h], name=f"Twall_init_h{h}") """

    # -------------------------- T_ave - Dynamics ---------------------------------- #

    # ---- T2 dynamics ----
    for h in range(Nh_all):
        for k in range(N):

            i = h*N + k

            if (k == 0):

                rhs = (
                    A_3 * T_wall_Init[h,0] +
                    A_4 * T_h_Init[h,0]  +
                    A_5 * T_attic_Init[h,0]  +
                    A_6 * T_im_Init[h,0]   +
                    B_2 * T_am[k,0]   +
                    B_3 * Q_ihl     -
                    B_4 * Q_ac * U_ac[i] +
                    B_5 * Q_venti_Const * (T_am[k,0] - T_h_Init[h,0]) +
                    B_6 * Q_infil_Const * Ws[k,0] * (T_am[k,0] - T_h_Init[h,0])
                )

                m.addConstr(
                    T_ave[i] == rhs,
                    name=f"T2_ave_h{h}_k{k}"
                )

            else:

                rhs = (
                    A_3 * T_wall[i-1] +
                    A_4 * T_ave[i-1]  +
                    A_5 * T_att[i-1]  +
                    A_6 * T_im[i-1]   +
                    B_2 * T_am[k]   +
                    B_3 * Q_ihl     -
                    B_4 * Q_ac * U_ac[i] +
                    B_5 * Q_venti_Const * (T_am[k,0] - T_ave[i-1]) +
                    B_6 * Q_infil_Const * Ws[k,0] * (T_am[k,0] - T_ave[i-1])
                )

                m.addConstr(
                    T_ave[i] == rhs,
                    name=f"T2_ave_h{h}_k{k}"
                )

    """ # ---- T2 dynamics ----
    for h in range(Nh_all):
        for k in range(N-1):

            i = h*N + k

            rhs = (
                A_3 * T_wall[i] +
                A_4 * T_ave[i]  +
                A_5 * T_att[i]  +
                A_6 * T_im[i]   +
                B_2 * T_am[k]   +
                B_3 * Q_ihl     -
                B_4 * Q_ac * U_ac[i] +
                B_5 * Q_venti_Const * (T_am[k] - T_ave[i]) +
                B_6 * Q_infil_Const * Ws[k] * (T_am[k] - T_ave[i])
            )

            m.addConstr(
                T_ave[i+1] == rhs,
                name=f"T2_ave_h{h}_k{k}"
            )

    # ---- Initial condition for T_ave ----
    for h in range(Nh_all):

        i = h*N

        m.addConstr(
            T_ave[i] == T_h_Init[h],
            name=f"Tave_init_h{h}"
        ) """

    # -------------------------- T_attic - Dynamics ---------------------------------- #

    # ---- T3 dynamics ----
    for h in range(Nh_all):
        for k in range(N):

            i = h*N + k

            if (k == 0):

                rhs = (
                    A_7 * T_h_Init[h,0] +
                    A_8 * T_attic_Init[h,0] +
                    B_7 * T_sol_r[k,0]
                )

                m.addConstr(
                    T_att[i] == rhs,
                    name=f"T3_att_h{h}_k{k}"
                )

            else:

                rhs = (
                    A_7 * T_ave[i-1] +
                    A_8 * T_att[i-1] +
                    B_7 * T_sol_r[k,0]
                )

                m.addConstr(
                    T_att[i] == rhs,
                    name=f"T3_att_h{h}_k{k}"
                )

    """ # ---- T3 dynamics ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = h*N + k

            rhs = (
                A_7 * T_ave[i] +
                A_8 * T_att[i] +
                B_7 * T_sol_r[k]
            )

            m.addConstr(
                T_att[i+1] == rhs,
                name=f"T3_att_h{h}_k{k}"
            )

    # ---- Initial condition for T_att ----
    for h in range(Nh_all):

        i = h*N

        m.addConstr(
            T_att[i] == T_attic_Init[h],
            name=f"Tatt_init_h{h}"
        ) """

    # -------------------------- T_im - Dynamics ---------------------------------- #

    # ---- T4 dynamics: indoor mass ----
    for h in range(Nh_all):
        for k in range(N):

            i = h*N + k

            if (k == 0):

                rhs = (
                    A_9  * T_h_Init[h,0] +
                    A_10 * T_im_Init[h,0]  +
                    B_8  * Q_solar[k,0]
                )

                m.addConstr(
                    T_im[i] == rhs,
                    name=f"T4_im_h{h}_k{k}"
                )

            else:

                rhs = (
                    A_9  * T_ave[i-1] +
                    A_10 * T_im[i-1]  +
                    B_8  * Q_solar[k,0]
                )

                m.addConstr(
                    T_im[i] == rhs,
                    name=f"T4_im_h{h}_k{k}"
                )

    """ # ---- T4 dynamics: indoor mass ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = h*N + k

            rhs = (
                A_9  * T_ave[i] +
                A_10 * T_im[i]  +
                B_8  * Q_solar[k]
            )

            m.addConstr(
                T_im[i+1] == rhs,
                name=f"T4_im_h{h}_k{k}"
            )

    # ---- Initial condition for T_im ----
    for h in range(Nh_all):

        i = h*N

        m.addConstr(
            T_im[i] == T_im_Init[h],
            name=f"Tim_init_h{h}"
        ) """

    # -------------------------- E_Bat - Dynamics ---------------------------------- #

    # ---- 4) Battery energy dynamics: E_bat^h(k+1) = E_bat^h(k) - Gamma^h(k)*E_bat_Step ----
    for b in range(Nh_bat):
        for k in range(N):

            i = b*N + k   # flattened index for (battery-house b, time k)

            if (k == 0):

                m.addConstr(
                    E_bat[i] == E_bat_Init[b,0] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize),
                    name=f"Ebat_dyn_b{b}_k{k}"
                )

            else:

                m.addConstr(
                    E_bat[i] == E_bat[i-1] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize),
                    name=f"Ebat_dyn_b{b}_k{k}"
                )

    """ # ---- 4) Battery energy dynamics: E_bat^h(k+1) = E_bat^h(k) - Gamma^h(k)*E_bat_Step ----
    for b in range(Nh_bat):
        for k in range(N - 1):

            i = b*N + k   # flattened index for (battery-house b, time k)

            m.addConstr(
                E_bat[i+1] == E_bat[i] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize),
                name=f"Ebat_dyn_b{b}_k{k}"
            )

    # ---- Battery initial condition: E_bat^h(0) ----
    for b in range(Nh_bat):

        i = b*N  # time index k=0

        m.addConstr(
            E_bat[i] == E_bat_Init[b],
            name=f"Ebat_init_b{b}"
        )
    """
    # -------------------------- U_ac on-off - Dynamics ---------------------------------- #

    # U_ac: size Nh_all * N
    # f_on, f_off: size Nh_bat * N
    # U_ac_Init: shape (Nh_all,)

    # (S1) Dynamics:
    # For k = 0: U_ac(h,0) - U_ac_Init(h) - f_on(h,0) + f_off(h,0) = 0
    # For k >= 1: U_ac(h,k) - U_ac(h,k-1) - f_on(h,k) + f_off(h,k) = 0

    for h in range(Nh_all):
        #h = b  # or h = house_of_bat[b] if you have a mapping

        # k = 1..N-1 cases
        for k in range(N):

            i   = h * N + k

            if (k == 0):

                m.addConstr(
                    U_ac[i] - U_ac_Init[h,0] - f_on[i] + f_off[i] == 0.0,
                    name=f"HVAC_switch_dyn_h{h}_k{k}"
                )

            else:

                m.addConstr(
                    U_ac[i] - U_ac[i-1] - f_on[i] + f_off[i] == 0.0,
                    name=f"HVAC_switch_dyn_h{h}_k{k}"
                )
            
    """ for b in range(Nh_all):
        h = b  # or h = house_of_bat[b] if you have a mapping

        # k = 0 case
        i_u_0 = h * N + 0
        i_f_0 = b * N + 0

        m.addConstr(
            U_ac[i_u_0] - U_ac_Init[h] - f_on[i_f_0] + f_off[i_f_0] == 0.0,
            name=f"HVAC_switch_dyn_h{h}_k0"
        )

        # k = 1..N-1 cases
        for k in range(1, N):
            i_u_k   = h * N + k
            i_u_km1 = h * N + (k - 1)
            i_f_k   = b * N + k

            m.addConstr(
                U_ac[i_u_k] - U_ac[i_u_km1] - f_on[i_f_k] + f_off[i_f_k] == 0.0,
                name=f"HVAC_switch_dyn_h{h}_k{k}"
            ) """

    # -------------------------- Energy Balance - OffGrid ---------------------------------- #

    # 5A) Off-grid community energy balance
    for k in range(N):

        expr = gp.LinExpr()

        # + sum_h U_ac(h,k) * E_AC  (HVAC energy)
        for h in range(Nh_all):
            i = h*N + k
            expr += U_ac[i] * E_AC/Eff_Inv

        # - sum_b Gamma(b,k) * E_bat_Step  (battery charge/discharge)
        for b in range(Nh_bat):
            j = b*N + k
            expr -= Gamma[j] * (Gamma_Discharging*Simulation_StepSize)

        # + sum_h E_load(h,k)  (served load)
        for h in range(Nh_all):
            i = h*N + k
            expr += E_load[i]

        # - sum_p g(p,k)  (PV energy used)
        for p in range(Nh_pv):
            l = p*N + k
            expr -= g[l]

        # Off-grid balance: expr = 0
        m.addConstr(expr == 0.0, name=f"Ebalance_off_k{k}")   

    # -------------------------- AC Startup ---------------------------------- #

    for k in range(N):

        lhs = gp.LinExpr()

        # Sum_b f_on(b,k) * P_AC_bar
        for h in range(Nh_all):
            i = h*N + k
            lhs += f_on[i] * ACLoad_StartUp_Power

        # - Sum_b theta_bat(b,k) * P_bat_bar
        for b in range(Nh_bat):
            i = b*N + k
            lhs -= theta_bat[i] * P_bat

        # RHS: total PV energy available over step k
        PV_available_k = E_PV_Reshaped [k,0] * (N_PV + N_PV_Bat) * (1/Simulation_StepSize)

        m.addConstr(
            lhs <= PV_available_k,
            name=f"PV_share_k{k}"
        )


    # -------------------------- AC on-off Complementarity ---------------------------------- #

    # (S2) At most one switch: f_on(h,k) + f_off(h,k) <= 1
    for b in range(Nh_all):
        for k in range(N):
            i_f = b * N + k
            m.addConstr(
                f_on[i_f] + f_off[i_f] <= 1.0,
                name=f"HVAC_switch_one_h{b}_k{k}"
            )

    # -------------------------- T_ave Slack ---------------------------------- #

    for h in range(Nh_all):
        for k in range(N):

            i = h * N + k

            m.addConstr(
                T_ave[i] - eps_h[i] <= T_h_Max,
                name=f"Comfort_h{h}_k{k}"
            )

    # -------------------------- E_l Slack ---------------------------------- #

    for h in range(Nh_all):
        for k in range(N):

            i = h * N + k

            E_cri_i = E_Load_Critical_Reshaped[i, 0]

            # E_load(h,k) + eps_l(h,k) >= E_cri(h,k)
            m.addConstr(
                E_load[i] + eps_l[i] >= E_cri_i,
                name=f"CritLoad_h{h}_k{k}"
            )

    # -------------------------- Bat Discharging Indicator ---------------------------------- #

    for b in range(Nh_bat):
        for k in range(N):
            i = b * N + k   # flattened index for (battery-house b, time k)

            m.addConstr(
                Gamma[i] - theta_bat[i] <= Epsilon,
                name=f"Gamma_theta_link_b{b}_k{k}"
            )

    # =================================================================================
    # Optimization Problem - Model Diagnostics
    # =================================================================================

    if (Model_Diagnostics):

        Exp_GurobiPy_Model_Diagnostic(m, "SingleMultiHouse_OffGrid_Gurobi_MPC_Model.txt")

    # =================================================================================
    # Optimization Problem - Solve
    # =================================================================================

    # Solver Parameter Setup
    m = Exp_apply_gurobi_params(m, SolverOptions_Dict)

    # Solving Optimization Problem
    m.optimize()

    # =================================================================================
    # Creating Initial Decision Variables - For Warm Start
    # =================================================================================

    if ((m.status == GRB.OPTIMAL) or (m.status == GRB.TIME_LIMIT)):

        # =================================================================================
        # Optimization Problem - Get Solution
        # =================================================================================

        ## Off-Grid
        Solution_Dict_np = Exp_Gurobi_unpack_mpc_solution_OffGrid(
            N,
            Nh_all,
            Nh_bat,
            Nh_pv,
            # Gurobi decision variables (MVar objects)
            T_wall,
            T_ave,
            T_att,
            T_im,
            U_ac,
            E_bat,
            Gamma,
            theta_bat,
            f_on,
            f_off,
            g,
            E_load,
            eps_h,
            eps_l
        )        

        Solution_Dict_List = Exp_flatten_solution_dict(Solution_Dict_np)

        # Off-Grid
        Initial_DecisionVariables_New = {
            "T_wall":    Solution_Dict_List["T_wall"],
            "T_ave":     Solution_Dict_List["T_ave"],
            "T_att":     Solution_Dict_List["T_att"],
            "T_im":      Solution_Dict_List["T_im"],
            "U_ac":      Solution_Dict_List["U_ac"],
            "E_bat":     Solution_Dict_List["E_bat"],
            "Gamma":     Solution_Dict_List["Gamma"],
            "theta_bat": Solution_Dict_List["theta_bat"],
            "f_on":      Solution_Dict_List["f_on"],
            "f_off":     Solution_Dict_List["f_off"],
            "g":         Solution_Dict_List["g"],
            "E_load":    Solution_Dict_List["E_load"],
            "eps_h":     Solution_Dict_List["eps_h"],
            "eps_l":     Solution_Dict_List["eps_l"]
        }

    else:
        
        # Off-Grid
        Solution_Dict_np = Exp_convert_OffGrid_solution_to_arrays(Initial_DecisionVariables, 
                                        N, Nh_all, Nh_bat, Nh_pv)

        Solution_Dict_List = Initial_DecisionVariables

        Initial_DecisionVariables_New = Initial_DecisionVariables

    return Solution_Dict_np, Solution_Dict_List, Initial_DecisionVariables_New, N_House, N_PV_Bat, N_Bat, E_l_Array 


# =================================================================================
# Single-Multi House On-Grid - No Fairness MPC Formulation - GurobiPy
# =================================================================================

def Exp_SingleMultiHouse_OnGrid_NoFairness_GurobiPy_MPC_Formulation(ctx, RC_data, reshaped):

    # =================================================================================
    # Unpack context for local use
    # =================================================================================

    # ---- Community sizes ----
    N_House   = ctx["N_House"]
    N_PV_Bat  = ctx["N_PV_Bat"]
    N_Bat     = ctx["N_Bat"]
    N_PV      = ctx["N_PV"]
    N_None    = ctx["N_None"]

    # ---- Initial states (at current MPC call) ----
    T_h_Init     = ctx["T_h_Init"]       # shape (N_House,)
    T_wall_Init  = ctx["T_wall_Init"]
    T_attic_Init = ctx["T_attic_Init"]
    T_im_Init    = ctx["T_im_Init"]

    E_bat_Init   = ctx["E_bat_Init"]     # shape (N_PV_Bat + N_Bat,)
    U_ac_Init    = ctx["U_ac_Init"]      # shape (N_House,)

    # ---- MPC horizon disturbances (W_k_MPC equivalent) ----
    E_l          = ctx["E_l"]             # desired load, horizon window
    E_l_Array    = ctx["E_l_Array"]       # full load stack per house

    Ws           = ctx["Ws"]
    T_am         = ctx["T_am"]
    GHI          = ctx["GHI"]
    DNI          = ctx["DNI"]

    Energy_Price = ctx["Energy_Price"]    

    # ---- Plant & house parameters ----
    # Full dicts if we ever need them:
    plant = ctx["plant"]
    house = ctx["house"]

    # Convenience scalars:
    T_h_Max              = ctx["T_h_Max"]
    T_h_Min              = ctx["T_h_Min"]
    Q_AC                 = ctx["Q_AC"]
    E_AC                 = ctx["E_AC"]
    ACLoad_StartUp_Power = ctx["ACLoad_StartUp_Power"]
    Eff_Inv              = ctx["Eff_Inv"]

    E_bat_Max            = ctx["E_bat_Max"]
    E_bat_Min            = ctx["E_bat_Min"]
    Gamma_Charging       = ctx["Gamma_Charging"]
    Gamma_Discharging    = ctx["Gamma_Discharging"]
    P_bat                = ctx["P_bat"]

    Q_ac                 = ctx["Q_ac"]   # house-level AC thermal power coeff

    # ---- MPC tuning and geometry ----
    N_horizon                 = ctx["N_horizon"]
    MPC_StepLengthUsed        = ctx["MPC_StepLengthUsed"]
    MPC_DecisionVariables_Num = ctx["MPC_DecisionVariables_Num"]
    Initial_DecisionVariables = ctx["Initial_DecisionVariables"]

    Lambda_T = ctx["Lambda_T"]
    Lambda_Bat = ctx["Lambda_Bat"]
    Lambda_E_l = ctx["Lambda_E_l"]
    Lambda_Theta = ctx["Lambda_Theta"]
    Lambda_E_cri = ctx["Lambda_E_cri"]
    Lambda_G = ctx["Lambda_G"]
    Lambda_PV = ctx["Lambda_PV"]

    Epsilon                     = ctx["Epsilon"]
    OpenLoop_Plotting_Indicator = ctx["OpenLoop_Plotting_Indicator"]

    # ---- Simulation step ----
    Simulation_StepSize = ctx["Simulation_StepSize"]

    # ---- Solver options (directly from MPC_Parameters, not in ctx yet) ----
    SolverOptions_Dict = GUROBI_OPTIONS_func()

    # ---- MPC Planning Horizon ----
    N = ctx["N_horizon"]

    # =================================================================================
    # RC disturbances + discrete-time model
    # =================================================================================

    Q_venti_Const = RC_data["Q_venti_Const"]
    Q_infil_Const = RC_data["Q_infil_Const"]

    Q_ihl   = RC_data["Q_ihl"]
    T_sol_w = RC_data["T_sol_w"]
    T_sol_r = RC_data["T_sol_r"]
    Q_solar = RC_data["Q_solar"]

    A_T_h   = RC_data["A_T_h"]
    B_T_h   = RC_data["B_T_h"]

    A_1 = A_T_h[0,0]
    A_2 = A_T_h[0,1]
    A_3 = A_T_h[1,0]
    A_4 = A_T_h[1,1]
    A_5 = A_T_h[1,2]
    A_6 = A_T_h[1,3]
    A_7 = A_T_h[2,1]
    A_8 = A_T_h[2,2]
    A_9 = A_T_h[3,1]
    A_10 = A_T_h[3,3]

    B_1 = B_T_h[0,1]
    B_2 = B_T_h[1,0]
    B_3 = B_T_h[1,3]
    B_4 = B_T_h[1,4]
    B_5 = B_T_h[1,5]
    B_6 = B_T_h[1,6]
    B_7 = B_T_h[2,2]
    B_8 = B_T_h[3,7]


    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    # ---- Unpack reshaped data ----
    T_h_Init     = reshaped["T_h_Init"]
    T_wall_Init  = reshaped["T_wall_Init"]
    T_attic_Init = reshaped["T_attic_Init"]
    T_im_Init    = reshaped["T_im_Init"]

    E_bat_Init   = reshaped["E_bat_Init"]
    U_ac_Init    = reshaped["U_ac_Init"]

    T_am         = reshaped["T_am"]
    Ws           = reshaped["Ws"]
    E_PV         = reshaped["E_PV"]          # now properly reshaped
    T_sol_w      = reshaped["T_sol_w"]
    T_sol_r      = reshaped["T_sol_r"]
    Q_solar      = reshaped["Q_solar"]
    Energy_Price = reshaped["Energy_Price"]

    E_Load_Critical_Reshaped = reshaped["E_Load_Critical_Reshaped"]
    E_l_Reshaped             = reshaped["E_l_Reshaped"]
    E_l_Array                = reshaped["E_l_Array_DC"]

    E_PV_Reshaped            = reshaped["E_PV_Reshaped"]

    Nh_all  = N_House
    Nh_bat  = N_PV_Bat + N_Bat
    Nh_pv   = N_PV_Bat + N_PV

    Continuous = False

    Model_Diagnostics = False

    m = gp.Model("MPC_community")


    # =================================================================================
    # Optimization Variables - Definitions With ub/lb
    # =================================================================================

    # ---- Thermal states (all houses) ----
    T_wall = m.addMVar(Nh_all * N, lb=-GRB.INFINITY, ub= GRB.INFINITY, name="T_wall")
    T_ave  = m.addMVar(Nh_all * N, lb=T_h_Min,   ub= GRB.INFINITY, name="T_ave")
    T_att  = m.addMVar(Nh_all * N, lb=-GRB.INFINITY, ub= GRB.INFINITY, name="T_att")
    T_im   = m.addMVar(Nh_all * N, lb=-GRB.INFINITY, ub= GRB.INFINITY, name="T_im")

    """ # ---- HVAC Control (Binary) ----
    if (Continuous):

        U_ac = m.addMVar(Nh_all * N, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="U_ac")    

    else:
        
        U_ac = m.addMVar(
            Nh_all * N,
            vtype=GRB.BINARY,
            name="U_ac"
        ) """
    

    # ---- Battery vars (only bat+pvbat) ----
    E_bat = m.addMVar(Nh_bat * N,
                    lb=E_bat_Min,
                    ub=E_bat_Max,
                    name="E_bat")

    Gamma = m.addMVar(Nh_bat * N,
                    lb=-1.52,
                    ub=1.0,
                    name="Gamma")
    if (Continuous):

        U_ac = m.addMVar(Nh_all * N, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name="U_ac")

    else:

        # ---- HVAC Control (Binary) ----
        U_ac = m.addMVar(
            Nh_all * N,
            vtype=GRB.BINARY,
            name="U_ac"
        )


    # ---- PV vars (pv+pvbat) ----
    u_pv = m.addMVar(Nh_pv * N, lb=0.0, ub=1.0,
                    vtype=GRB.CONTINUOUS, name="u_pv")  # or BINARY

    eps_h = m.addMVar(Nh_all * N, lb=0.0, ub=GRB.INFINITY,
                    vtype=GRB.CONTINUOUS, name="eps_h")

    # ---- Grid energy (per time) ----
    E_g = m.addMVar(N, lb=-GRB.INFINITY, ub=GRB.INFINITY,
                    vtype=GRB.CONTINUOUS, name="E_g")

    # =================================================================================
    # Optimization Variables - Warm Start
    # =================================================================================

    T_wall.Start     = Initial_DecisionVariables["T_wall"]
    T_ave.Start      = Initial_DecisionVariables["T_ave"]
    T_att.Start      = Initial_DecisionVariables["T_att"]
    T_im.Start       = Initial_DecisionVariables["T_im"]

    U_ac.Start       = Initial_DecisionVariables["U_ac"]

    E_bat.Start      = Initial_DecisionVariables["E_bat"]
    Gamma.Start      = Initial_DecisionVariables["Gamma"]

    u_pv.Start       = Initial_DecisionVariables["u_pv"]

    eps_h.Start      = Initial_DecisionVariables["eps_h"]

    E_g.Start        = Initial_DecisionVariables["E_g"]

    # =================================================================================
    # Optimization Problem - Objective
    # =================================================================================

    

    # -------------------------- Single-House On-Grid ---------------------------------- #

    obj = gp.LinExpr()

    # ---- Grid cost term: sum_k C_g(k) * E_g(k) ----
    for k in range(N):
        obj += Lambda_G * Energy_Price[k,0] * E_g[k]

    # ---- Comfort slack term: + Lambda_T * sum_{h,k} eps_h(h,k) ----
    for h in range(Nh_all):
        for k in range(N):
            i = h*N + k
            obj += Lambda_T * eps_h[i]

    # ---- Battery SoC term: - Lambda_soc * sum_{b,k} E_bat(b,k) ----
    for b in range(Nh_bat):
        for k in range(N):
            j = b*N + k
            obj += -Lambda_Bat * E_bat[j]

    # ---- PV utilization benefit: - Lambda_pv * sum_{p,k} u_pv(p,k)*E_pv_bar(p,k) ----
    for p in range(Nh_pv):
        for k in range(N):
            l       = p*N + k
            E_pv_l  = E_PV_Reshaped[l, 0]   # \overline E_pv^h(k) data

            obj += -Lambda_PV * u_pv[l] * E_pv_l

    ### Setting up Objective
    # Set final objective
    m.setObjective(obj, GRB.MINIMIZE)    

    # =================================================================================
    # Optimization Problem - Constraints
    # =================================================================================

    # -------------------------- T_wall - Dynamics ---------------------------------- #

    for h in range(Nh_all):
        for k in range(N):  # k = 0..N_MPC-1, state at k+1

            i = h*N + k

            if (k == 0):

                m.addConstr(
                    T_wall[i] == A_1 * T_wall_Init[h,0] + A_2 * T_h_Init[h,0] + B_1 * T_sol_w[k,0],
                    name=f"T1_wall_h{h}_k{k}"
                )

            else:

                m.addConstr(
                    T_wall[i] == A_1 * T_wall[i-1] + A_2 * T_ave[i-1] + B_1 * T_sol_w[k,0],
                    name=f"T1_wall_h{h}_k{k}"
                )

    """ for h in range(Nh_all):
        for k in range(N-1):  # k = 0..N_MPC-1, state at k+1

            i = h*N + k

            m.addConstr(
                T_wall[i+1] == A_1 * T_wall[i] + A_2 * T_ave[i] + B_1 * T_sol_w[k],
                name=f"T1_wall_h{h}_k{k}"
            )

    for h in range(Nh_all):

        i = h*N

        m.addConstr(T_wall[i] == T_wall_Init[h], name=f"Twall_init_h{h}") """

    # -------------------------- T_ave - Dynamics ---------------------------------- #

    # ---- T2 dynamics ----
    for h in range(Nh_all):
        for k in range(N):

            i = h*N + k

            if (k == 0):

                rhs = (
                    A_3 * T_wall_Init[h,0] +
                    A_4 * T_h_Init[h,0]  +
                    A_5 * T_attic_Init[h,0]  +
                    A_6 * T_im_Init[h,0]   +
                    B_2 * T_am[k,0]   +
                    B_3 * Q_ihl     -
                    B_4 * Q_ac * U_ac[i] +
                    B_5 * Q_venti_Const * (T_am[k,0] - T_h_Init[h,0]) +
                    B_6 * Q_infil_Const * Ws[k,0] * (T_am[k,0] - T_h_Init[h,0])
                )

                m.addConstr(
                    T_ave[i] == rhs,
                    name=f"T2_ave_h{h}_k{k}"
                )

            else:

                rhs = (
                    A_3 * T_wall[i-1] +
                    A_4 * T_ave[i-1]  +
                    A_5 * T_att[i-1]  +
                    A_6 * T_im[i-1]   +
                    B_2 * T_am[k,0]   +
                    B_3 * Q_ihl     -
                    B_4 * Q_ac * U_ac[i] +
                    B_5 * Q_venti_Const * (T_am[k,0] - T_ave[i-1]) +
                    B_6 * Q_infil_Const * Ws[k,0] * (T_am[k,0] - T_ave[i-1])
                )

                m.addConstr(
                    T_ave[i] == rhs,
                    name=f"T2_ave_h{h}_k{k}"
                )

    """ # ---- T2 dynamics ----
    for h in range(Nh_all):
        for k in range(N-1):

            i = h*N + k

            rhs = (
                A_3 * T_wall[i] +
                A_4 * T_ave[i]  +
                A_5 * T_att[i]  +
                A_6 * T_im[i]   +
                B_2 * T_am[k]   +
                B_3 * Q_ihl     -
                B_4 * Q_ac * U_ac[i] +
                B_5 * Q_venti_Const * (T_am[k] - T_ave[i]) +
                B_6 * Q_infil_Const * Ws[k] * (T_am[k] - T_ave[i])
            )

            m.addConstr(
                T_ave[i+1] == rhs,
                name=f"T2_ave_h{h}_k{k}"
            )

    # ---- Initial condition for T_ave ----
    for h in range(Nh_all):

        i = h*N

        m.addConstr(
            T_ave[i] == T_h_Init[h],
            name=f"Tave_init_h{h}"
        ) """

    # -------------------------- T_attic - Dynamics ---------------------------------- #

    # ---- T3 dynamics ----
    for h in range(Nh_all):
        for k in range(N):

            i = h*N + k

            if (k == 0):

                rhs = (
                    A_7 * T_h_Init[h,0] +
                    A_8 * T_attic_Init[h,0] +
                    B_7 * T_sol_r[k,0]
                )

                m.addConstr(
                    T_att[i] == rhs,
                    name=f"T3_att_h{h}_k{k}"
                )

            else:

                rhs = (
                    A_7 * T_ave[i-1] +
                    A_8 * T_att[i-1] +
                    B_7 * T_sol_r[k,0]
                )

                m.addConstr(
                    T_att[i] == rhs,
                    name=f"T3_att_h{h}_k{k}"
                )

    """ # ---- T3 dynamics ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = h*N + k

            rhs = (
                A_7 * T_ave[i] +
                A_8 * T_att[i] +
                B_7 * T_sol_r[k]
            )

            m.addConstr(
                T_att[i+1] == rhs,
                name=f"T3_att_h{h}_k{k}"
            )

    # ---- Initial condition for T_att ----
    for h in range(Nh_all):

        i = h*N

        m.addConstr(
            T_att[i] == T_attic_Init[h],
            name=f"Tatt_init_h{h}"
        ) """

    # -------------------------- T_im - Dynamics ---------------------------------- #

    # ---- T4 dynamics: indoor mass ----
    for h in range(Nh_all):
        for k in range(N):

            i = h*N + k

            if (k == 0):

                rhs = (
                    A_9  * T_h_Init[h,0] +
                    A_10 * T_im_Init[h,0]  +
                    B_8  * Q_solar[k,0]
                )

                m.addConstr(
                    T_im[i] == rhs,
                    name=f"T4_im_h{h}_k{k}"
                )

            else:

                rhs = (
                    A_9  * T_ave[i-1] +
                    A_10 * T_im[i-1]  +
                    B_8  * Q_solar[k,0]
                )

                m.addConstr(
                    T_im[i] == rhs,
                    name=f"T4_im_h{h}_k{k}"
                )

    """ # ---- T4 dynamics: indoor mass ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = h*N + k

            rhs = (
                A_9  * T_ave[i] +
                A_10 * T_im[i]  +
                B_8  * Q_solar[k]
            )

            m.addConstr(
                T_im[i+1] == rhs,
                name=f"T4_im_h{h}_k{k}"
            )

    # ---- Initial condition for T_im ----
    for h in range(Nh_all):

        i = h*N

        m.addConstr(
            T_im[i] == T_im_Init[h],
            name=f"Tim_init_h{h}"
        ) """

    # -------------------------- E_Bat - Dynamics ---------------------------------- #

    # ---- 4) Battery energy dynamics: E_bat^h(k+1) = E_bat^h(k) - Gamma^h(k)*E_bat_Step ----
    for b in range(Nh_bat):
        for k in range(N):

            i = b*N + k   # flattened index for (battery-house b, time k)

            if (k == 0):

                m.addConstr(
                    E_bat[i] == E_bat_Init[b,0] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize),
                    name=f"Ebat_dyn_b{b}_k{k}"
                )

            else:

                m.addConstr(
                    E_bat[i] == E_bat[i-1] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize),
                    name=f"Ebat_dyn_b{b}_k{k}"
                )

    """ # ---- 4) Battery energy dynamics: E_bat^h(k+1) = E_bat^h(k) - Gamma^h(k)*E_bat_Step ----
    for b in range(Nh_bat):
        for k in range(N - 1):

            i = b*N + k   # flattened index for (battery-house b, time k)

            m.addConstr(
                E_bat[i+1] == E_bat[i] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize),
                name=f"Ebat_dyn_b{b}_k{k}"
            )

    # ---- Battery initial condition: E_bat^h(0) ----
    for b in range(Nh_bat):

        i = b*N  # time index k=0

        m.addConstr(
            E_bat[i] == E_bat_Init[b],
            name=f"Ebat_init_b{b}"
        )
    """
    
    # -------------------------- Energy Balance - OnGrid ---------------------------------- #

    # 5B) On-grid community energy balance with g replaced by u_pv * E_pv
    for k in range(N):

        expr = gp.LinExpr()

        # + sum_h U_ac(h,k) * E_AC  (HVAC)
        for h in range(Nh_all):
            i = h*N + k
            expr += U_ac[i] * E_AC/Eff_Inv

        # - sum_b Gamma(b,k) * E_bat_Step  (battery term)
        for b in range(Nh_bat):
            j = b*N + k
            expr -= Gamma[j] * (Gamma_Discharging*Simulation_StepSize)

        # + sum_h E_load(h,k)  (served load)
        for h in range(Nh_all):
            i = h*N + k
            expr += E_l_Reshaped[i,0]

        # - sum_p u_pv(p,k) * \bar E_pv(p,k)  (PV energy use)
        for p in range(Nh_pv):
            l = p*N + k
            E_pv_l = E_PV_Reshaped[l, 0]  # data
            expr -= u_pv[l] * E_pv_l

        # - E_g(k)  (grid exchange)
        expr -= E_g[k]

        # On-grid balance: expr = 0
        m.addConstr(expr == 0.0, name=f"Ebalance_on_k{k}")

    # -------------------------- T_ave Slack ---------------------------------- #

    for h in range(Nh_all):
        for k in range(N):

            i = h * N + k

            m.addConstr(
                T_ave[i] - eps_h[i] <= T_h_Max,
                name=f"Comfort_h{h}_k{k}"
            )   

    # =================================================================================
    # Optimization Problem - Model Diagnostics
    # =================================================================================

    if (Model_Diagnostics):

        Exp_GurobiPy_Model_Diagnostic(m, "SingleMultiHouse_OnGrid_Gurobi_MPC_Model.txt")

    # =================================================================================
    # Optimization Problem - Solve
    # =================================================================================

    # Solver Parameter Setup
    m = Exp_apply_gurobi_params(m, SolverOptions_Dict)

    # Solving Optimization Problem
    m.optimize()

    # =================================================================================
    # Creating Initial Decision Variables - For Warm Start
    # =================================================================================

    if ((m.status == GRB.OPTIMAL) or (m.status == GRB.TIME_LIMIT)):

        # =================================================================================
        # Optimization Problem - Get Solution
        # =================================================================================

        ## On-Grid
        Solution_Dict_np = Exp_Gurobi_unpack_mpc_solution_OnGrid(
            N,
            Nh_all,
            Nh_bat,
            Nh_pv,
            # Gurobi decision variables (MVar objects)
            T_wall,
            T_ave,
            T_att,
            T_im,
            U_ac,
            E_bat,
            Gamma,
            u_pv,
            eps_h,
            E_g
        )

        Solution_Dict_List = Exp_flatten_solution_dict(Solution_Dict_np)

        # On-Grid
        Initial_DecisionVariables_New = {
            "T_wall":    Solution_Dict_List["T_wall"],
            "T_ave":     Solution_Dict_List["T_ave"],
            "T_att":     Solution_Dict_List["T_att"],
            "T_im":      Solution_Dict_List["T_im"],
            "U_ac":      Solution_Dict_List["U_ac"],
            "E_bat":     Solution_Dict_List["E_bat"],
            "Gamma":     Solution_Dict_List["Gamma"],
            "u_pv":      Solution_Dict_List["u_pv"],
            "eps_h":     Solution_Dict_List["eps_h"],
            "E_g":       Solution_Dict_List["E_g"],
        }

    else:
        
        # Off-Grid
        # Solution_Dict_np = Exp_convert_OffGrid_solution_to_arrays(Initial_DecisionVariables,                                         N, Nh_all, Nh_bat, Nh_pv)

        # On-Grid
        Solution_Dict_np = Exp_convert_OnGrid_solution_to_arrays(Initial_DecisionVariables, 
                                        N, Nh_all, Nh_bat, Nh_pv)
        
        Solution_Dict_List = Initial_DecisionVariables

        Initial_DecisionVariables_New = Initial_DecisionVariables

    return Solution_Dict_np, Solution_Dict_List, Initial_DecisionVariables_New, N_House, N_PV_Bat, N_Bat, E_l_Array 

# =================================================================================
# Single-Multi House Off-Grid - No Fairness MPC Formulation - CasaDi
# =================================================================================
def Exp_SingleMultiHouse_OffGrid_NoFairness_Casadi_MPC_Formulation(ctx, RC_data, reshaped):

    # =================================================================================
    # Unpack context for local use
    # =================================================================================

    # ---- Community sizes ----
    N_House   = ctx["N_House"]
    N_PV_Bat  = ctx["N_PV_Bat"]
    N_Bat     = ctx["N_Bat"]
    N_PV      = ctx["N_PV"]
    N_None    = ctx["N_None"]

    # ---- Initial states (at current MPC call) ----
    T_h_Init     = ctx["T_h_Init"]       # shape (N_House,)
    T_wall_Init  = ctx["T_wall_Init"]
    T_attic_Init = ctx["T_attic_Init"]
    T_im_Init    = ctx["T_im_Init"]

    E_bat_Init   = ctx["E_bat_Init"]     # shape (N_PV_Bat + N_Bat,)
    U_ac_Init    = ctx["U_ac_Init"]      # shape (N_House,)

    # ---- MPC horizon disturbances (W_k_MPC equivalent) ----
    E_l          = ctx["E_l"]             # desired load, horizon window
    E_l_Array    = ctx["E_l_Array"]       # full load stack per house

    Ws           = ctx["Ws"]
    T_am         = ctx["T_am"]
    GHI          = ctx["GHI"]
    DNI          = ctx["DNI"]

    Energy_Price = ctx["Energy_Price"]    

    # ---- Plant & house parameters ----
    # Full dicts if we ever need them:
    plant = ctx["plant"]
    house = ctx["house"]

    # Convenience scalars:
    T_h_Max              = ctx["T_h_Max"]
    T_h_Min              = ctx["T_h_Min"]
    Q_AC                 = ctx["Q_AC"]
    E_AC                 = ctx["E_AC"]
    ACLoad_StartUp_Power = ctx["ACLoad_StartUp_Power"]
    Eff_Inv              = ctx["Eff_Inv"]

    E_bat_Max            = ctx["E_bat_Max"]
    E_bat_Min            = ctx["E_bat_Min"]
    Gamma_Charging       = ctx["Gamma_Charging"]
    Gamma_Discharging    = ctx["Gamma_Discharging"]
    P_bat                = ctx["P_bat"]

    Q_ac                 = ctx["Q_ac"]   # house-level AC thermal power coeff

    # ---- MPC tuning and geometry ----
    N_horizon                 = ctx["N_horizon"]
    MPC_StepLengthUsed        = ctx["MPC_StepLengthUsed"]
    MPC_DecisionVariables_Num = ctx["MPC_DecisionVariables_Num"]
    Initial_DecisionVariables = ctx["Initial_DecisionVariables"]

    Lambda_T = ctx["Lambda_T"]
    Lambda_Bat = ctx["Lambda_Bat"]
    Lambda_E_l = ctx["Lambda_E_l"]
    Lambda_Theta = ctx["Lambda_Theta"]
    Lambda_E_cri = ctx["Lambda_E_cri"]
    Lambda_G = ctx["Lambda_G"]
    Lambda_PV = ctx["Lambda_PV"]

    Epsilon                     = ctx["Epsilon"]
    OpenLoop_Plotting_Indicator = ctx["OpenLoop_Plotting_Indicator"]

    # ---- Simulation step ----
    Simulation_StepSize = ctx["Simulation_StepSize"]

    # ---- Solver options (directly from MPC_Parameters, not in ctx yet) ----
    SolverOptions_Dict = GUROBI_OPTIONS_func()

    # ---- MPC Planning Horizon ----
    N = ctx["N_horizon"]

    # =================================================================================
    # RC disturbances + discrete-time model
    # =================================================================================

    Q_venti_Const = RC_data["Q_venti_Const"]
    Q_infil_Const = RC_data["Q_infil_Const"]

    Q_ihl   = RC_data["Q_ihl"]
    T_sol_w = RC_data["T_sol_w"]
    T_sol_r = RC_data["T_sol_r"]
    Q_solar = RC_data["Q_solar"]

    A_T_h   = RC_data["A_T_h"]
    B_T_h   = RC_data["B_T_h"]

    A_1 = A_T_h[0,0]
    A_2 = A_T_h[0,1]
    A_3 = A_T_h[1,0]
    A_4 = A_T_h[1,1]
    A_5 = A_T_h[1,2]
    A_6 = A_T_h[1,3]
    A_7 = A_T_h[2,1]
    A_8 = A_T_h[2,2]
    A_9 = A_T_h[3,1]
    A_10 = A_T_h[3,3]

    B_1 = B_T_h[0,1]
    B_2 = B_T_h[1,0]
    B_3 = B_T_h[1,3]
    B_4 = B_T_h[1,4]
    B_5 = B_T_h[1,5]
    B_6 = B_T_h[1,6]
    B_7 = B_T_h[2,2]
    B_8 = B_T_h[3,7]


    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    # ---- Unpack reshaped data ----
    T_h_Init     = reshaped["T_h_Init"]
    T_wall_Init  = reshaped["T_wall_Init"]
    T_attic_Init = reshaped["T_attic_Init"]
    T_im_Init    = reshaped["T_im_Init"]

    E_bat_Init   = reshaped["E_bat_Init"]
    U_ac_Init    = reshaped["U_ac_Init"]

    T_am         = reshaped["T_am"]
    E_PV         = reshaped["E_PV"]          # now properly reshaped
    T_sol_w      = reshaped["T_sol_w"]
    T_sol_r      = reshaped["T_sol_r"]
    Q_solar      = reshaped["Q_solar"]
    Energy_Price = reshaped["Energy_Price"]

    E_Load_Critical_Reshaped = reshaped["E_Load_Critical_Reshaped"]
    E_l_Reshaped             = reshaped["E_l_Reshaped"]
    E_l_Array                = reshaped["E_l_Array_DC"]

    E_PV_Reshaped            = reshaped["E_PV_Reshaped"]

    Nh_all  = N_House
    Nh_bat  = N_PV_Bat + N_Bat
    Nh_pv   = N_PV_Bat + N_PV

    Continuous = False

    Model_Diagnostics = False

    # =================================================================================
    # Optimization Variables - Definitions
    # =================================================================================

    T_wall = ca.SX.sym("T_wall", Nh_all * N)
    T_ave  = ca.SX.sym("T_ave",  Nh_all * N)
    T_att  = ca.SX.sym("T_att",  Nh_all * N)
    T_im   = ca.SX.sym("T_im",   Nh_all * N)

    U_ac   = ca.SX.sym("U_ac",   Nh_all * N)

    E_bat     = ca.SX.sym("E_bat",     Nh_bat * N)
    Gamma     = ca.SX.sym("Gamma",     Nh_bat * N)
    theta_bat = ca.SX.sym("theta_bat", Nh_bat * N)
    f_on      = ca.SX.sym("f_on",      Nh_bat * N)
    f_off     = ca.SX.sym("f_off",     Nh_bat * N)
    g     = ca.SX.sym("g",      Nh_pv * N)

    E_load = ca.SX.sym("E_load", Nh_all * N)
    eps_h  = ca.SX.sym("eps_h",  Nh_all * N)
    eps_l  = ca.SX.sym("eps_l",  Nh_all * N)


    x = ca.vertcat(
        T_wall, T_ave, T_att, T_im,
        U_ac,
        E_bat, Gamma, theta_bat, f_on, f_off,
        g,
        E_load, eps_h, eps_l
    )
    n_x = x.numel()

    # =================================================================================
    # Optimization Variables - ub/lb
    # =================================================================================

    INF = np.inf

    lbx = []
    ubx = []

    # Convenience helpers:
    def _append_bounds(vec_len, lb, ub):
        lbx.extend([lb] * vec_len)
        ubx.extend([ub] * vec_len)

    # 1) T_wall: -inf..+inf
    _append_bounds(Nh_all * N, -INF, +INF)

    # 2) T_ave: [T_h_min, +inf)
    _append_bounds(Nh_all * N, T_h_Min, +INF)

    # 3) T_att: -inf..+inf
    _append_bounds(Nh_all * N, -INF, +INF)

    # 4) T_im: -inf..+inf
    _append_bounds(Nh_all * N, -INF, +INF)

    # 6) U_ac: 0..1  (continuous; swap if binary)
    _append_bounds(Nh_all * N, 0.0, 1.0)

    # 7) E_bat: [E_bat_cap_min, E_bat_cap_max]
    _append_bounds(Nh_bat * N, E_bat_Min, E_bat_Max)

    # 8) Gamma: [Gamma_min, Gamma_max]
    _append_bounds(Nh_bat * N, -1.52, 1.0)

    # 9) theta_bat: 0..1
    _append_bounds(Nh_bat * N, 0.0, 1.0)

    # 10) f_on: 0..1
    _append_bounds(Nh_all * N, 0.0, 1.0)

    # 11) f_off: 0..1
    _append_bounds(Nh_all * N, 0.0, 1.0)

    # 13) g: 0..Epv_bar(h_loc,k)  (time-varying bound)
    for i in range(Nh_pv*N):
        lbx.append(0.0)
        ubx.append(E_PV_Reshaped [i, 1])

    # 14) E_load: 0..E_l_bar(h_loc,k) (time-varying)
    for i in range(Nh_all*N):
        lbx.append(0.0)
        ubx.append(E_l_Reshaped[i, 1])

    # 15) eps_h: 0..+inf
    _append_bounds(Nh_all * N, 0.0, +INF)

    # 16) eps_l: lb = barE_cri(h,k), ub = +inf
    for i in range(Nh_all*N):
        lbx.append(0.0)
        ubx.append(E_Load_Critical_Reshaped[i,1])

    assert len(lbx) == n_x and len(ubx) == n_x
    lbx = ca.DM(lbx)
    ubx = ca.DM(ubx)

    # =================================================================================
    # Optimization Variables - Warm Start
    # =================================================================================

    import casadi as ca

    x_init_list = (
        Initial_DecisionVariables["T_wall"] +
        Initial_DecisionVariables["T_ave"]  +
        Initial_DecisionVariables["T_att"]  +
        Initial_DecisionVariables["T_im"]   +
        Initial_DecisionVariables["U_ac"]   +
        Initial_DecisionVariables["E_bat"]      +
        Initial_DecisionVariables["Gamma"]      +
        Initial_DecisionVariables["theta_bat"]  +
        Initial_DecisionVariables["f_on"]       +
        Initial_DecisionVariables["f_off"]      +
        Initial_DecisionVariables["g"]     +
        Initial_DecisionVariables["E_load"]+
        Initial_DecisionVariables["eps_h"] +
        Initial_DecisionVariables["eps_l"] 
    )

    # Convert to CasADi DM
    x_init = ca.DM(x_init_list)

    # =================================================================================
    # Optimization Problem - Objective
    # =================================================================================
    
    # -------------------------- Multi-House Off-Grid ---------------------------------- #

    J = 0

    # ---- 1. ALL HOUSES ----
    for h in range(Nh_all):
        for k in range(N):

            i = h*N + k
            weight = (N - k)

            J = J \
                + Lambda_T * weight * eps_h[i] \
                + Lambda_E_cri * weight * eps_l[i] \
                - Lambda_E_l * weight * E_load[i]

    # ---- 2. BATTERY HOUSES ----
    for b in range(Nh_bat):
        for k in range(N):

            j = b*N + k

            J = J \
                - Lambda_Bat * E_bat[j] \
                + Lambda_Theta * theta_bat[j]    

    # =================================================================================
    # Optimization Problem - Constraints and its Bounds
    # =================================================================================

    g_list = []  # Constraint List
    G_lb   = []  # Constraint lower bound list
    G_ub   = []  # Constraint upper bound list

    # -------------------------- T_wall - Dynamics ---------------------------------- #

    # ---- T1 dynamics ----
    for h in range(Nh_all):
        for k in range(N):

            i = N*h + k

            if (k == 0):

                g_list.append(
                    T_wall[i]
                    - (A_1 * T_wall_Init[h]
                    + A_2 * T_h_Init[h]
                    + B_1 * T_sol_w[k])
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

            else:

                g_list.append(
                    T_wall[i]
                    - (A_1 * T_wall[i-1]
                    + A_2 * T_ave [i-1]
                    + B_1 * T_sol_w[k])
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

    """ # ---- T1 dynamics ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = N*h + k

            g_list.append(
                T_wall[i+1]
                - (A_1 * T_wall[i]
                + A_2 * T_ave [i]
                + B_1 * T_sol_w[k])
            )
            G_lb.append(0.0)
            G_ub.append(0.0)

    # ---- Initial condition T_wall(h,0) ----
    for h in range(Nh_all):

        i = N*h

        g_list.append(
            T_wall[i] - T_wall_Init[h]
        )
        G_lb.append(0.0)
        G_ub.append(0.0) """

    # -------------------------- T_ave - Dynamics ---------------------------------- #

    # ---- T2 dynamics ----
    for h in range(Nh_all):
        for k in range(N):

            i = N*h + k

            if (k == 0):

                g_list.append(
                    T_ave[i] - (
                        A_3 * T_wall_Init[h] +
                        A_4 * T_h_Init[h]  +
                        A_5 * T_attic_Init[h]  +
                        A_6 * T_im_Init[h]   +
                        B_2 * T_am[k]   +
                        B_3 * Q_ihl     -
                        B_4 * Q_ac * U_ac[i] +
                        B_5 * Q_venti_Const * (T_am[k] - T_h_Init[h]) +
                        B_6 * Q_infil_Const * Ws[k] * (T_am[k] - T_h_Init[h])
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

            else:

                g_list.append(
                    T_ave[i] - (
                        A_3 * T_wall[i-1] +
                        A_4 * T_ave[i-1]  +
                        A_5 * T_att[i-1]  +
                        A_6 * T_im[i-1]   +
                        B_2 * T_am[k]   +
                        B_3 * Q_ihl     -
                        B_4 * Q_ac * U_ac[i] +
                        B_5 * Q_venti_Const * (T_am[k] - T_ave[i-1]) +
                        B_6 * Q_infil_Const * Ws[k] * (T_am[k] - T_ave[i-1])
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)


    """ # ---- T2 dynamics ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = N*h + k

            g_list.append(
                T_ave[i+1] - (
                    A_3 * T_wall[i] +
                    A_4 * T_ave[i]  +
                    A_5 * T_att[i]  +
                    A_6 * T_im[i]   +
                    B_2 * T_am[k]   +
                    B_3 * Q_ihl     -
                    B_4 * Q_ac * U_ac[i] +
                    B_5 * Q_venti_Const * (T_am[k] - T_ave[i]) +
                    B_6 * Q_infil_Const * Ws[k] * (T_am[k] - T_ave[i])
                )
            )
            G_lb.append(0.0)
            G_ub.append(0.0)

    # ---- Initial condition: T_ave(h,0) ----
    for h in range(Nh_all):

        i = N*h

        g_list.append(
            T_ave[i] - T_h_Init[h]
        )
        G_lb.append(0.0)
        G_ub.append(0.0) """

    # -------------------------- T_attic - Dynamics ---------------------------------- #

    # ---- T3 dynamics ----
    for h in range(Nh_all):
        for k in range(N):

            i = N*h + k

            if (k == 0):

                g_list.append(
                    T_att[i] - (
                        A_7 * T_h_Init[h] +
                        A_8 * T_attic_Init[h] +
                        B_7 * T_sol_r[k]
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

            else:

                g_list.append(
                    T_att[i] - (
                        A_7 * T_ave[i-1] +
                        A_8 * T_att[i-1] +
                        B_7 * T_sol_r[k]
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

    """ # ---- T3 dynamics ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = N*h + k

            g_list.append(
                T_att[i+1] - (
                    A_7 * T_ave[i] +
                    A_8 * T_att[i] +
                    B_7 * T_sol_r[k]
                )
            )
            G_lb.append(0.0)
            G_ub.append(0.0)

    # ---- Initial condition: T_att(h,0) ----
    for h in range(Nh_all):

        i = N*h

        g_list.append(
            T_att[i] - T_attic_Init[h]
        )
        G_lb.append(0.0)
        G_ub.append(0.0) """

    # -------------------------- T_im - Dynamics ---------------------------------- #

    # ---- T4 dynamics: indoor mass ----
    for h in range(Nh_all):
        for k in range(N):

            i = N*h + k

            if (k == 0):

                g_list.append(
                    T_im[i] - (
                        A_9  * T_h_Init[h] +
                        A_10 * T_im_Init[h]  +
                        B_8  * Q_solar[k]
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

            else:

                g_list.append(
                    T_im[i] - (
                        A_9  * T_ave[i-1] +
                        A_10 * T_im[i-1]  +
                        B_8  * Q_solar[k]
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

    """ # ---- T4 dynamics: indoor mass ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = N*h + k

            g_list.append(
                T_im[i+1] - (
                    A_9  * T_ave[i] +
                    A_10 * T_im[i]  +
                    B_8  * Q_solar[k]
                )
            )
            G_lb.append(0.0)
            G_ub.append(0.0)

    # ---- Initial condition: T_im(h,0) ----
    for h in range(Nh_all):

        i = N*h

        g_list.append(
            T_im[i] - T_im_Init[h]
        )
        G_lb.append(0.0)
        G_ub.append(0.0) """

    # -------------------------- E_Bat - Dynamics ---------------------------------- #

    # ---- 4) Battery energy dynamics ----
    for b in range(Nh_bat):
        for k in range(N):

            i = N*b + k

            if (k == 0):

                g_list.append(
                    E_bat[i] - (E_bat_Init[b] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize))
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

            else:

                g_list.append(
                    E_bat[i] - (E_bat[i-1] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize))
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

    """ # ---- 4) Battery energy dynamics ----
    for b in range(Nh_bat):
        for k in range(N - 1):

            i = N*b + k

            g_list.append(
                E_bat[i+1] - (E_bat[i] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize))
            )
            G_lb.append(0.0)
            G_ub.append(0.0)

    # ---- Battery initial condition: E_bat^h(0) ----
    for b in range(Nh_bat):

        i = N*b  # k=0

        g_list.append(
            E_bat[i] - E_bat_Init[b]
        )
        G_lb.append(0.0)
        G_ub.append(0.0) """

    # -------------------------- U_ac on-off - Dynamics ---------------------------------- #

    # (S1) Dynamics:
    for h in range(Nh_all):    

        # k = 1..N-1
        for k in range(N):

            i = N*h + k

            if (k == 0):

                g_list.append(
                    U_ac[i] - U_ac_Init[h] - f_on[i] + f_off[i]
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

            else:

                g_list.append(
                    U_ac[i] - U_ac[i-1] - f_on[i] + f_off[i]
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

    """ # (S1) Dynamics:
    for b in range(Nh_all):
        h = b  # or h = house_of_bat[b]

        # k = 0 case
        i_u_0 = h * N + 0
        i_f_0 = b * N + 0

        g_list.append(
            U_ac[i_u_0] - U_ac_Init[h] - f_on[i_f_0] + f_off[i_f_0]
        )
        G_lb.append(0.0)
        G_ub.append(0.0)

        # k = 1..N-1
        for k in range(1, N):
            i_u_k   = h * N + k
            i_u_km1 = h * N + (k - 1)
            i_f_k   = b * N + k

            g_list.append(
                U_ac[i_u_k] - U_ac[i_u_km1] - f_on[i_f_k] + f_off[i_f_k]
            )
            G_lb.append(0.0)
            G_ub.append(0.0) """

    # -------------------------- Energy Balance - OffGrid ---------------------------------- #

    # 5A) Off-grid community energy balance
    for k in range(N):

        expr = 0

        # + sum_h U_ac(h,k) * E_AC
        for h in range(Nh_all):
            i = h*N + k
            expr += U_ac[i] * E_AC/Eff_Inv

        # - sum_b Gamma(b,k) * E_bat_Step
        for b in range(Nh_bat):
            j = b*N + k
            expr -= Gamma[j] * (Gamma_Discharging*Simulation_StepSize)

        # + sum_h E_load(h,k)
        for h in range(Nh_all):
            i = h*N + k
            expr += E_load[i]

        # - sum_p g(p,k)
        for p in range(Nh_pv):
            l = p*N + k
            expr -= g[l]

        # Equality constraint: expr == 0
        g_list.append(expr)
        G_lb.append(0.0)
        G_ub.append(0.0)

    # -------------------------- AC Startup ---------------------------------- #

    for k in range(N):

        lhs = 0

        # Sum_b f_on(b,k) * P_AC_bar
        for b in range(Nh_bat):
            i = b*N + k
            lhs += f_on[i] * ACLoad_StartUp_Power

        # - Sum_b theta_bat(b,k) * P_bat_bar
        for b in range(Nh_bat):
            i = b*N + k
            lhs -= theta_bat[i] * P_bat

        PV_available_k = E_PV_Reshaped [k,1] * (N_PV + N_PV_Bat) * (1/Simulation_StepSize)

        # lhs <= PV_available_k  --> lhs - PV_available_k <= 0
        g_list.append(lhs - PV_available_k)
        G_lb.append(-ca.inf)   # <= 0
        G_ub.append(0.0)

    # -------------------------- AC on-off Complementarity ---------------------------------- #

    for b in range(Nh_all):
        for k in range(N):
            i_f = b * N + k

            g_list.append(
                f_on[i_f] + f_off[i_f] - 1.0
            )
            G_lb.append(-ca.inf)   # <= 0
            G_ub.append(0.0)

    # -------------------------- T_ave Slack ---------------------------------- #

    for h in range(Nh_all):
        for k in range(N):

            i = h * N + k

            g_list.append(
                T_ave[i] - eps_h[i] - T_h_Max
            )
            G_lb.append(-ca.inf)   # <= 0
            G_ub.append(0.0)

    # -------------------------- E_l Slack ---------------------------------- #

    for h in range(Nh_all):
        for k in range(N):

            i = h * N + k

            E_cri_i = E_Load_Critical_Reshaped[i, 1]

            g_list.append(
                -E_load[i] - eps_l[i] + E_cri_i
            )
            G_lb.append(-ca.inf)   # <= 0
            G_ub.append(0.0)

    # -------------------------- Bat Discharging Indicator ---------------------------------- #

    for b in range(Nh_bat):
        for k in range(N):
            i = b * N + k

            g_list.append(
                Gamma[i] - theta_bat[i] - Epsilon
            )
            G_lb.append(-ca.inf)   # <= 0
            G_ub.append(0.0)

    # =================================================================================
    # Optimization Problem - Create
    # =================================================================================

    # Creating NLP Problem
    NLP_Problem = {'f': J, 'x': x, 'g': g_list}

    ## Constructiong NLP Solver
    NLP_Solver = ca.nlpsol('nlp_solver', 'ipopt',  NLP_Problem, SolverOptions_Dict)

    # =================================================================================
    # Optimization Problem - Model Diagnostics
    # =================================================================================

    if (Model_Diagnostics):

        Exp_Casadi_Model_Diagnostic(NLP_Problem, NLP_Solver, "SingleMultiHouse_OffGrid_Gurobi_MPC_Model.txt")

    # =================================================================================
    # Optimization Problem - Solve
    # =================================================================================

    ## Solving the NLP Problem

    # Solving NLP Problem
    NLP_Solution = NLP_Solver(x0 = x_init_list, lbx = lbx, ubx = ubx, lbg = G_lb, ubg = G_ub)

    # =================================================================================
    # Optimization Problem - Get Solution
    # =================================================================================

    Solution_Dict_np = Exp_Casadi_unpack_mpc_solution_OffGrid(NLP_Solution, N, Nh_all, Nh_bat, Nh_pv)

    # Solution_Dict_np = Exp_Casadi_unpack_mpc_solution_OnGrid(NLP_Solution, N, Nh_all, Nh_bat, Nh_pv)

    Solution_Dict_List = Exp_flatten_solution_dict(Solution_Dict_np)

    # =================================================================================
    # Creating Initial Decision Variables - For Warm Start
    # =================================================================================

    # Off-Grid
    Initial_DecisionVariables_New = {
        "T_wall":    Solution_Dict_List["T_wall"],
        "T_ave":     Solution_Dict_List["T_ave"],
        "T_att":     Solution_Dict_List["T_att"],
        "T_im":      Solution_Dict_List["T_im"],
        "U_ac":      Solution_Dict_List["U_ac"],
        "E_bat":     Solution_Dict_List["E_bat"],
        "Gamma":     Solution_Dict_List["Gamma"],
        "theta_bat": Solution_Dict_List["theta_bat"],
        "f_on":      Solution_Dict_List["f_on"],
        "f_off":     Solution_Dict_List["f_off"],
        "g":         Solution_Dict_List["g"],
        "E_load":    Solution_Dict_List["E_load"],
        "eps_h":     Solution_Dict_List["eps_h"],
        "eps_l":     Solution_Dict_List["eps_l"]
    }

    return Solution_Dict_np, Solution_Dict_List, Initial_DecisionVariables_New, N_House, N_PV_Bat, N_Bat, E_l_Array 


# =================================================================================
# Single-Multi House On-Grid - No Fairness MPC Formulation - CasaDi
# =================================================================================

def Exp_SingleMultiHouse_OnGrid_NoFairness_Casadi_MPC_Formulation(ctx, RC_data, reshaped):

    # =================================================================================
    # Unpack context for local use
    # =================================================================================

    # ---- Community sizes ----
    N_House   = ctx["N_House"]
    N_PV_Bat  = ctx["N_PV_Bat"]
    N_Bat     = ctx["N_Bat"]
    N_PV      = ctx["N_PV"]
    N_None    = ctx["N_None"]

    # ---- Initial states (at current MPC call) ----
    T_h_Init     = ctx["T_h_Init"]       # shape (N_House,)
    T_wall_Init  = ctx["T_wall_Init"]
    T_attic_Init = ctx["T_attic_Init"]
    T_im_Init    = ctx["T_im_Init"]

    E_bat_Init   = ctx["E_bat_Init"]     # shape (N_PV_Bat + N_Bat,)
    U_ac_Init    = ctx["U_ac_Init"]      # shape (N_House,)

    # ---- MPC horizon disturbances (W_k_MPC equivalent) ----
    E_l          = ctx["E_l"]             # desired load, horizon window
    E_l_Array    = ctx["E_l_Array"]       # full load stack per house

    Ws           = ctx["Ws"]
    T_am         = ctx["T_am"]
    GHI          = ctx["GHI"]
    DNI          = ctx["DNI"]

    Energy_Price = ctx["Energy_Price"]    

    # ---- Plant & house parameters ----
    # Full dicts if we ever need them:
    plant = ctx["plant"]
    house = ctx["house"]

    # Convenience scalars:
    T_h_Max              = ctx["T_h_Max"]
    T_h_Min              = ctx["T_h_Min"]
    Q_AC                 = ctx["Q_AC"]
    E_AC                 = ctx["E_AC"]
    ACLoad_StartUp_Power = ctx["ACLoad_StartUp_Power"]
    Eff_Inv              = ctx["Eff_Inv"]

    E_bat_Max            = ctx["E_bat_Max"]
    E_bat_Min            = ctx["E_bat_Min"]
    Gamma_Charging       = ctx["Gamma_Charging"]
    Gamma_Discharging    = ctx["Gamma_Discharging"]
    P_bat                = ctx["P_bat"]

    Q_ac                 = ctx["Q_ac"]   # house-level AC thermal power coeff

    # ---- MPC tuning and geometry ----
    N_horizon                 = ctx["N_horizon"]
    MPC_StepLengthUsed        = ctx["MPC_StepLengthUsed"]
    MPC_DecisionVariables_Num = ctx["MPC_DecisionVariables_Num"]
    Initial_DecisionVariables = ctx["Initial_DecisionVariables"]

    Lambda_T = ctx["Lambda_T"]
    Lambda_Bat = ctx["Lambda_Bat"]
    Lambda_E_l = ctx["Lambda_E_l"]
    Lambda_Theta = ctx["Lambda_Theta"]
    Lambda_E_cri = ctx["Lambda_E_cri"]
    Lambda_G = ctx["Lambda_G"]
    Lambda_PV = ctx["Lambda_PV"]

    Epsilon                     = ctx["Epsilon"]
    OpenLoop_Plotting_Indicator = ctx["OpenLoop_Plotting_Indicator"]

    # ---- Simulation step ----
    Simulation_StepSize = ctx["Simulation_StepSize"]

    # ---- Solver options (directly from MPC_Parameters, not in ctx yet) ----
    SolverOptions_Dict = GUROBI_OPTIONS_func()

    # ---- MPC Planning Horizon ----
    N = ctx["N_horizon"]

    # =================================================================================
    # RC disturbances + discrete-time model
    # =================================================================================

    Q_venti_Const = RC_data["Q_venti_Const"]
    Q_infil_Const = RC_data["Q_infil_Const"]

    Q_ihl   = RC_data["Q_ihl"]
    T_sol_w = RC_data["T_sol_w"]
    T_sol_r = RC_data["T_sol_r"]
    Q_solar = RC_data["Q_solar"]

    A_T_h   = RC_data["A_T_h"]
    B_T_h   = RC_data["B_T_h"]

    A_1 = A_T_h[0,0]
    A_2 = A_T_h[0,1]
    A_3 = A_T_h[1,0]
    A_4 = A_T_h[1,1]
    A_5 = A_T_h[1,2]
    A_6 = A_T_h[1,3]
    A_7 = A_T_h[2,1]
    A_8 = A_T_h[2,2]
    A_9 = A_T_h[3,1]
    A_10 = A_T_h[3,3]

    B_1 = B_T_h[0,1]
    B_2 = B_T_h[1,0]
    B_3 = B_T_h[1,3]
    B_4 = B_T_h[1,4]
    B_5 = B_T_h[1,5]
    B_6 = B_T_h[1,6]
    B_7 = B_T_h[2,2]
    B_8 = B_T_h[3,7]


    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    # ---- Unpack reshaped data ----
    T_h_Init     = reshaped["T_h_Init"]
    T_wall_Init  = reshaped["T_wall_Init"]
    T_attic_Init = reshaped["T_attic_Init"]
    T_im_Init    = reshaped["T_im_Init"]

    E_bat_Init   = reshaped["E_bat_Init"]
    U_ac_Init    = reshaped["U_ac_Init"]

    T_am         = reshaped["T_am"]
    E_PV         = reshaped["E_PV"]          # now properly reshaped
    T_sol_w      = reshaped["T_sol_w"]
    T_sol_r      = reshaped["T_sol_r"]
    Q_solar      = reshaped["Q_solar"]
    Energy_Price = reshaped["Energy_Price"]

    E_Load_Critical_Reshaped = reshaped["E_Load_Critical_Reshaped"]
    E_l_Reshaped             = reshaped["E_l_Reshaped"]
    E_l_Array                = reshaped["E_l_Array_DC"]

    E_PV_Reshaped            = reshaped["E_PV_Reshaped"]

    Nh_all  = N_House
    Nh_bat  = N_PV_Bat + N_Bat
    Nh_pv   = N_PV_Bat + N_PV

    Continuous = False

    Model_Diagnostics = False

        # =================================================================================
    # Optimization Variables - Definitions
    # =================================================================================

    T_wall = ca.SX.sym("T_wall", Nh_all * N)
    T_ave  = ca.SX.sym("T_ave",  Nh_all * N)
    T_att  = ca.SX.sym("T_att",  Nh_all * N)
    T_im   = ca.SX.sym("T_im",   Nh_all * N)

    U_ac   = ca.SX.sym("U_ac",   Nh_all * N)

    E_bat     = ca.SX.sym("E_bat",     Nh_bat * N)
    Gamma     = ca.SX.sym("Gamma",     Nh_bat * N)

    u_pv  = ca.SX.sym("u_pv",   Nh_pv * N)

    eps_h  = ca.SX.sym("eps_h",  Nh_all * N)

    E_g    = ca.SX.sym("E_g",    N)


    x = ca.vertcat(
        T_wall, T_ave, T_att, T_im,
        U_ac,
        E_bat, Gamma, 
        u_pv, 
        eps_h, 
        E_g
    )
    n_x = x.numel()

    # =================================================================================
    # Optimization Variables - ub/lb
    # =================================================================================

    INF = np.inf

    lbx = []
    ubx = []

    # Convenience helpers:
    def _append_bounds(vec_len, lb, ub):
        lbx.extend([lb] * vec_len)
        ubx.extend([ub] * vec_len)

    # 1) T_wall: -inf..+inf
    _append_bounds(Nh_all * N, -INF, +INF)

    # 2) T_ave: [T_h_min, +inf)
    _append_bounds(Nh_all * N, T_h_Min, +INF)

    # 3) T_att: -inf..+inf
    _append_bounds(Nh_all * N, -INF, +INF)

    # 4) T_im: -inf..+inf
    _append_bounds(Nh_all * N, -INF, +INF)

    # 6) U_ac: 0..1  (continuous; swap if binary)
    _append_bounds(Nh_all * N, 0.0, 1.0)

    # 7) E_bat: [E_bat_cap_min, E_bat_cap_max]
    _append_bounds(Nh_bat * N, E_bat_Min, E_bat_Max)

    # 8) Gamma: [Gamma_min, Gamma_max]
    _append_bounds(Nh_bat * N, -1.52, 1.0)

    # 12) u_pv: 0..1
    _append_bounds(Nh_pv * N, 0.0, 1.0)

    # 15) eps_h: 0..+inf
    _append_bounds(Nh_all * N, 0.0, +INF)

    # 17) E_g: -inf..+inf
    _append_bounds(N, -INF, +INF)

    assert len(lbx) == n_x and len(ubx) == n_x
    lbx = ca.DM(lbx)
    ubx = ca.DM(ubx)

    # =================================================================================
    # Optimization Variables - Warm Start
    # =================================================================================

    import casadi as ca

    x_init_list = (
        Initial_DecisionVariables["T_wall"] +
        Initial_DecisionVariables["T_ave"]  +
        Initial_DecisionVariables["T_att"]  +
        Initial_DecisionVariables["T_im"]   +
        Initial_DecisionVariables["U_ac"]   +
        Initial_DecisionVariables["E_bat"]      +
        Initial_DecisionVariables["Gamma"]      +
        Initial_DecisionVariables["u_pv"]  +
        Initial_DecisionVariables["eps_h"] +
        Initial_DecisionVariables["E_g"]
    )

    # Convert to CasADi DM
    x_init = ca.DM(x_init_list)

    # =================================================================================
    # Optimization Problem - Objective
    # =================================================================================
    
    # -------------------------- Multi-House On-Grid ---------------------------------- #

    J = 0

    # ---- Grid cost term ----
    for k in range(N):
        J = J + Lambda_G * Energy_Price[k] * E_g[k]

    # ---- Comfort slack term ----
    for h in range(Nh_all):
        for k in range(N):
            i = h*N + k
            J = J + Lambda_T * eps_h[i]

    # ---- Battery SoC term ----
    for b in range(Nh_bat):
        for k in range(N):
            j = b*N + k
            J = J - Lambda_Bat * E_bat[j]

    # ---- PV utilization benefit term ----
    for p in range(Nh_pv):
        for k in range(N):
            l      = p*N + k
            E_pv_l = E_PV_Reshaped[l, 1]
            J = J - Lambda_PV * u_pv[l] * E_pv_l

    # =================================================================================
    # Optimization Problem - Constraints and its Bounds
    # =================================================================================

    g_list = []  # Constraint List
    G_lb   = []  # Constraint lower bound list
    G_ub   = []  # Constraint upper bound list

    # -------------------------- T_wall - Dynamics ---------------------------------- #

    # ---- T1 dynamics ----
    for h in range(Nh_all):
        for k in range(N):

            i = N*h + k

            if (k == 0):

                g_list.append(
                    T_wall[i]
                    - (A_1 * T_wall_Init[h]
                    + A_2 * T_h_Init[h]
                    + B_1 * T_sol_w[k])
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

            else:

                g_list.append(
                    T_wall[i]
                    - (A_1 * T_wall[i-1]
                    + A_2 * T_ave [i-1]
                    + B_1 * T_sol_w[k])
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

    """ # ---- T1 dynamics ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = N*h + k

            g_list.append(
                T_wall[i+1]
                - (A_1 * T_wall[i]
                + A_2 * T_ave [i]
                + B_1 * T_sol_w[k])
            )
            G_lb.append(0.0)
            G_ub.append(0.0)

    # ---- Initial condition T_wall(h,0) ----
    for h in range(Nh_all):

        i = N*h

        g_list.append(
            T_wall[i] - T_wall_Init[h]
        )
        G_lb.append(0.0)
        G_ub.append(0.0) """

    # -------------------------- T_ave - Dynamics ---------------------------------- #

    # ---- T2 dynamics ----
    for h in range(Nh_all):
        for k in range(N):

            i = N*h + k

            if (k == 0):

                g_list.append(
                    T_ave[i] - (
                        A_3 * T_wall_Init[h] +
                        A_4 * T_h_Init[h]  +
                        A_5 * T_attic_Init[h]  +
                        A_6 * T_im_Init[h]   +
                        B_2 * T_am[k]   +
                        B_3 * Q_ihl     -
                        B_4 * Q_ac * U_ac[i] +
                        B_5 * Q_venti_Const * (T_am[k] - T_h_Init[h]) +
                        B_6 * Q_infil_Const * Ws[k] * (T_am[k] - T_h_Init[h])
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

            else:

                g_list.append(
                    T_ave[i] - (
                        A_3 * T_wall[i-1] +
                        A_4 * T_ave[i-1]  +
                        A_5 * T_att[i-1]  +
                        A_6 * T_im[i-1]   +
                        B_2 * T_am[k]   +
                        B_3 * Q_ihl     -
                        B_4 * Q_ac * U_ac[i] +
                        B_5 * Q_venti_Const * (T_am[k] - T_ave[i-1]) +
                        B_6 * Q_infil_Const * Ws[k] * (T_am[k] - T_ave[i-1])
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)


    """ # ---- T2 dynamics ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = N*h + k

            g_list.append(
                T_ave[i+1] - (
                    A_3 * T_wall[i] +
                    A_4 * T_ave[i]  +
                    A_5 * T_att[i]  +
                    A_6 * T_im[i]   +
                    B_2 * T_am[k]   +
                    B_3 * Q_ihl     -
                    B_4 * Q_ac * U_ac[i] +
                    B_5 * Q_venti_Const * (T_am[k] - T_ave[i]) +
                    B_6 * Q_infil_Const * Ws[k] * (T_am[k] - T_ave[i])
                )
            )
            G_lb.append(0.0)
            G_ub.append(0.0)

    # ---- Initial condition: T_ave(h,0) ----
    for h in range(Nh_all):

        i = N*h

        g_list.append(
            T_ave[i] - T_h_Init[h]
        )
        G_lb.append(0.0)
        G_ub.append(0.0) """

    # -------------------------- T_attic - Dynamics ---------------------------------- #

    # ---- T3 dynamics ----
    for h in range(Nh_all):
        for k in range(N):

            i = N*h + k

            if (k == 0):

                g_list.append(
                    T_att[i] - (
                        A_7 * T_h_Init[h] +
                        A_8 * T_attic_Init[h] +
                        B_7 * T_sol_r[k]
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

            else:

                g_list.append(
                    T_att[i] - (
                        A_7 * T_ave[i-1] +
                        A_8 * T_att[i-1] +
                        B_7 * T_sol_r[k]
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

    """ # ---- T3 dynamics ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = N*h + k

            g_list.append(
                T_att[i+1] - (
                    A_7 * T_ave[i] +
                    A_8 * T_att[i] +
                    B_7 * T_sol_r[k]
                )
            )
            G_lb.append(0.0)
            G_ub.append(0.0)

    # ---- Initial condition: T_att(h,0) ----
    for h in range(Nh_all):

        i = N*h

        g_list.append(
            T_att[i] - T_attic_Init[h]
        )
        G_lb.append(0.0)
        G_ub.append(0.0) """

    # -------------------------- T_im - Dynamics ---------------------------------- #

    # ---- T4 dynamics: indoor mass ----
    for h in range(Nh_all):
        for k in range(N):

            i = N*h + k

            if (k == 0):

                g_list.append(
                    T_im[i] - (
                        A_9  * T_h_Init[h] +
                        A_10 * T_im_Init[h]  +
                        B_8  * Q_solar[k]
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

            else:

                g_list.append(
                    T_im[i] - (
                        A_9  * T_ave[i-1] +
                        A_10 * T_im[i-1]  +
                        B_8  * Q_solar[k]
                    )
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

    """ # ---- T4 dynamics: indoor mass ----
    for h in range(Nh_all):
        for k in range(N - 1):

            i = N*h + k

            g_list.append(
                T_im[i+1] - (
                    A_9  * T_ave[i] +
                    A_10 * T_im[i]  +
                    B_8  * Q_solar[k]
                )
            )
            G_lb.append(0.0)
            G_ub.append(0.0)

    # ---- Initial condition: T_im(h,0) ----
    for h in range(Nh_all):

        i = N*h

        g_list.append(
            T_im[i] - T_im_Init[h]
        )
        G_lb.append(0.0)
        G_ub.append(0.0) """

    # -------------------------- E_Bat - Dynamics ---------------------------------- #

    # ---- 4) Battery energy dynamics ----
    for b in range(Nh_bat):
        for k in range(N):

            i = N*b + k

            if (k == 0):

                g_list.append(
                    E_bat[i] - (E_bat_Init[b] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize))
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

            else:

                g_list.append(
                    E_bat[i] - (E_bat[i-1] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize))
                )
                G_lb.append(0.0)
                G_ub.append(0.0)

    """ # ---- 4) Battery energy dynamics ----
    for b in range(Nh_bat):
        for k in range(N - 1):

            i = N*b + k

            g_list.append(
                E_bat[i+1] - (E_bat[i] - Gamma[i] * (Gamma_Discharging*Simulation_StepSize))
            )
            G_lb.append(0.0)
            G_ub.append(0.0)

    # ---- Battery initial condition: E_bat^h(0) ----
    for b in range(Nh_bat):

        i = N*b  # k=0

        g_list.append(
            E_bat[i] - E_bat_Init[b]
        )
        G_lb.append(0.0)
        G_ub.append(0.0) """
    
    # -------------------------- Energy Balance - OnGrid ---------------------------------- #

    for k in range(N):

        expr = 0

        # + sum_h U_ac(h,k) * E_AC
        for h in range(Nh_all):
            i = h*N + k
            expr += U_ac[i] * E_AC/Eff_Inv

        # - sum_b Gamma(b,k) * E_bat_Step
        for b in range(Nh_bat):
            j = b*N + k
            expr -= Gamma[j] * (Gamma_Discharging*Simulation_StepSize)

        # + sum_h E_load(h,k)
        for h in range(Nh_all):
            i = h*N + k
            expr += E_l_Reshaped[i,1]

        # - sum_p u_pv(p,k) * \bar E_pv(p,k)
        for p in range(Nh_pv):
            l = p*N + k
            E_pv_l = E_PV_Reshaped[l, 1]
            expr -= u_pv[l] * E_pv_l

        # - E_g(k)
        expr -= E_g[k]

        # Equality: expr == 0
        g_list.append(expr)
        G_lb.append(0.0)
        G_ub.append(0.0)   

    # -------------------------- T_ave Slack ---------------------------------- #

    for h in range(Nh_all):
        for k in range(N):

            i = h * N + k

            g_list.append(
                T_ave[i] - eps_h[i] - T_h_Max
            )
            G_lb.append(-ca.inf)   # <= 0
            G_ub.append(0.0)

    # =================================================================================
    # Optimization Problem - Model Diagnostics
    # =================================================================================

    if (Model_Diagnostics):

        Exp_Casadi_Model_Diagnostic(NLP_Problem, NLP_Solver, "SingleMultiHouse_OffGrid_Gurobi_MPC_Model.txt")

    # =================================================================================
    # Optimization Problem - Create
    # =================================================================================

    # Creating NLP Problem
    NLP_Problem = {'f': J, 'x': x, 'g': g_list}

    ## Constructiong NLP Solver
    NLP_Solver = ca.nlpsol('nlp_solver', 'ipopt',  NLP_Problem, SolverOptions_Dict)

    # =================================================================================
    # Optimization Problem - Model Diagnostics
    # =================================================================================

    if (Model_Diagnostics):

        Exp_Casadi_Model_Diagnostic(NLP_Problem, NLP_Solver, "SingleMultiHouse_OnGrid_Casadi_MPC_Model.txt")

    # =================================================================================
    # Optimization Problem - Solve
    # =================================================================================

    ## Solving the NLP Problem

    # Solving NLP Problem
    NLP_Solution = NLP_Solver(x0 = x_init_list, lbx = lbx, ubx = ubx, lbg = G_lb, ubg = G_ub)

    # =================================================================================
    # Optimization Problem - Get Solution
    # =================================================================================

    # Solution_Dict_np = Exp_Casadi_unpack_mpc_solution_OffGrid(NLP_Solution, N, Nh_all, Nh_bat, Nh_pv)

    Solution_Dict_np = Exp_Casadi_unpack_mpc_solution_OnGrid(NLP_Solution, N, Nh_all, Nh_bat, Nh_pv)

    Solution_Dict_List = Exp_flatten_solution_dict(Solution_Dict_np)

    # =================================================================================
    # Creating Initial Decision Variables - For Warm Start
    # =================================================================================

    # On-Grid
    Initial_DecisionVariables_New = {
        "T_wall":    Solution_Dict_List["T_wall"],
        "T_ave":     Solution_Dict_List["T_ave"],
        "T_att":     Solution_Dict_List["T_att"],
        "T_im":      Solution_Dict_List["T_im"],
        "U_ac":      Solution_Dict_List["U_ac"],
        "E_bat":     Solution_Dict_List["E_bat"],
        "Gamma":     Solution_Dict_List["Gamma"],
        "u_pv":      Solution_Dict_List["u_pv"],
        "eps_h":     Solution_Dict_List["eps_h"],
        "E_g":       Solution_Dict_List["E_g"],
    }

    return Solution_Dict_np, Solution_Dict_List, Initial_DecisionVariables_New, N_House, N_PV_Bat, N_Bat, E_l_Array 