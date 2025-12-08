import casadi as ca
import numpy as np

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
Lambda_Bat = ctx["Lambda_Bat"]
Lambda_Theta = ctx["Lambda_Theta"]
Lambda_E_cri = ctx["Lambda_E_cri"]
Lambda_G = ctx["Lambda_G"]
Lambda_PV = ctx["Lambda_PV"]

Epsilon                     = ctx["Epsilon"]
OpenLoop_Plotting_Indicator = ctx["OpenLoop_Plotting_Indicator"]

# ---- Simulation step ----
Simulation_StepSize = ctx["Simulation_StepSize"]

# ---- Solver options (directly from MPC_Parameters, not in ctx yet) ----
SolverOptions_Dict = IPOPT_OPTIONS_func()

# ---- MPC Planning Horizon ----
N = ctx["N_horizon"]

# =================================================================================
# =================================================================================
# BASIC COMPUTATION
# =================================================================================
# =================================================================================

# =================================================================================
# Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
# =================================================================================

E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

# =================================================================================
# RC disturbances + discrete-time model
# =================================================================================

RC_data = compute_singlehouse_RC_data_from_ctx(ctx)

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

reshaped = reshape_and_sanitize_Community_inputs(
    ctx      = ctx,
    E_PV     = E_PV,
    T_sol_w  = T_sol_w,
    T_sol_r  = T_sol_r,
    Q_solar  = Q_solar,
)

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

u_pv  = ca.SX.sym("u_pv",   Nh_pv * N)
g     = ca.SX.sym("g",      Nh_pv * N)

E_load = ca.SX.sym("E_load", Nh_all * N)
eps_h  = ca.SX.sym("eps_h",  Nh_all * N)
eps_l  = ca.SX.sym("eps_l",  Nh_all * N)

E_g    = ca.SX.sym("E_g",    N)


x = ca.vertcat(
    T_wall, T_ave, T_att, T_im,
    U_ac,
    E_bat, Gamma, theta_bat, f_on, f_off,
    u_pv, g,
    E_load, eps_h, eps_l,
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

# 9) theta_bat: 0..1
_append_bounds(Nh_bat * N, 0.0, 1.0)

# 10) f_on: 0..1
_append_bounds(Nh_bat * N, 0.0, 1.0)

# 11) f_off: 0..1
_append_bounds(Nh_bat * N, 0.0, 1.0)

# 12) u_pv: 0..1
_append_bounds(Nh_pv * N, 0.0, 1.0)

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
    Initial_DecisionVariables["theta_bat"]  +
    Initial_DecisionVariables["f_on"]       +
    Initial_DecisionVariables["f_off"]      +
    Initial_DecisionVariables["u_pv"]  +
    Initial_DecisionVariables["g"]     +
    Initial_DecisionVariables["E_load"]+
    Initial_DecisionVariables["eps_h"] +
    Initial_DecisionVariables["eps_l"] +
    Initial_DecisionVariables["E_g"]
)

# Convert to CasADi DM
x_init = ca.DM(x_init_list)

# =================================================================================
# Optimization Problem - Objective
# =================================================================================

# -------------------------- Single-House Off-Grid ---------------------------------- #

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


# -------------------------- Single-House On-Grid ---------------------------------- #

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
        expr += U_ac[i] * E_AC

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

# -------------------------- Energy Balance - OnGrid ---------------------------------- #

for k in range(N):

    expr = 0

    # + sum_h U_ac(h,k) * E_AC
    for h in range(Nh_all):
        i = h*N + k
        expr += U_ac[i] * E_AC

    # - sum_b Gamma(b,k) * E_bat_Step
    for b in range(Nh_bat):
        j = b*N + k
        expr -= Gamma[j] * (Gamma_Discharging*Simulation_StepSize)

    # + sum_h E_load(h,k)
    for h in range(Nh_all):
        i = h*N + k
        expr += E_l[i,1]

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
# Optimization Problem - Solve
# =================================================================================

# Creating NLP Problem
NLP_Problem = {'f': J, 'x': x, 'g': g}

## Constructiong NLP Solver
NLP_Solver = ca.nlpsol('nlp_solver', 'ipopt',  NLP_Problem, SolverOptions_Dict)

## Solving the NLP Problem

# Solving NLP Problem
NLP_Solution = NLP_Solver(x0 = x_init_list, lbx = lbx, ubx = ubx, lbg = G_lb, ubg = G_ub)

# =================================================================================
# Optimization Problem - Get Solution
# =================================================================================

Solution_Dict_np = Exp_Casadi_unpack_mpc_solution_OffGrid(NLP_Solution, N, Nh_all, Nh_bat, Nh_pv)

Solution_Dict_np = Exp_Casadi_unpack_mpc_solution_OnGrid(NLP_Solution, N, Nh_all, Nh_bat, Nh_pv)

Solution_Dict_List = Exp_flatten_solution_dict(Solution_Dict_np)

# =================================================================================
# Creating Initial Decision Variables - For Warm Start
# =================================================================================

# Off-Grid
Initial_DecisionVariables = {
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

# On-Grid
Initial_DecisionVariables = {
    "T_wall":    Solution_Dict_List["T_wall"],
    "T_ave":     Solution_Dict_List["T_ave"],
    "T_att":     Solution_Dict_List["T_att"],
    "T_im":      Solution_Dict_List["T_im"],
    "U_ac":      Solution_Dict_List["U_ac"],
    "E_bat":     Solution_Dict_List["E_bat"],
    "Gamma":     Solution_Dict_List["Gamma"],
    "u_pv":      Solution_Dict_List["u_pv"],
    "E_load":    Solution_Dict_List["E_load"],
    "eps_h":     Solution_Dict_List["eps_h"],
    "E_g":       Solution_Dict_List["E_g"],
}

# =================================================================================
# Optimization Problem - Solution - Processing for MPC Control
# =================================================================================