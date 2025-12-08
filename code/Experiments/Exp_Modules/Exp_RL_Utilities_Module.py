###############################################################################################################
## Import Desired Packages
###############################################################################################################

import sys
import os

import numpy as np
from gymnasium import spaces

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

from Exp_Config_Module import *
from Exp_MPC_RL_Helpers import *

###############################################################################################################
## RL CONFIGURATION - CONSTANTS 
###############################################################################################################

# -------------------- RL Setup - Configured in Exp_Config_Module-------------------- #

RL_Parameters = Exp_RL_Configuration_Generator()

###############################################################################################################
## Experiment RL Utilities Module - Custom Functions
###############################################################################################################

#-------------------------------------------------------------------------------------------------------------#
# Single House Off-Grid RL
#-------------------------------------------------------------------------------------------------------------#

# -------------------- Observation Space -------------------- #

def SingleHouse_OffGrid_RL_ObservationSpace_Function(SmartComSim_Object):

    # Build Short Context from Env
    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House      = int(ctx["N_House"])
    N_PV_Bat     = int(ctx["N_PV_Bat"])
    N_Bat        = int(ctx["N_Bat"])
    N_PV         = int(ctx["N_PV"])
    N_None       = int(ctx["N_None"])

    # Get desired RL_Parameters
    RL_HORIZON_N = int(RL_Parameters["RL_HORIZON_N"])
    RL_HORIZON_AVG_N = int(RL_Parameters["RL_HORIZON_AVG_N"])

    # OFF-GRID State: [Th(N_House), E_Bat(N_PV_Bat+N_Bat), U_ac_prev(N_House), 
    # E_l_now(N_House), E_cri_now(N_House), 
    # E_PV_now(1), T_am_now(1), 
    # E_l_future((RL_HORIZON_N/RL_HORIZON_AVG_N)*N_House), E_cri_future((RL_HORIZON_N/RL_HORIZON_AVG_N)*N_House), 
    # E_PV_future(RL_HORIZON_N/RL_HORIZON_AVG_N), T_am_future(RL_HORIZON_N/RL_HORIZON_AVG_N) ]

    # On-GRID State: [Th(N_House), E_Bat(N_PV_Bat+N_Bat), 
    # E_l_now(N_House),  
    # E_PV_now(1), T_am_now(1), E_Price_now(1)
    # E_l_future((RL_HORIZON_N/RL_HORIZON_AVG_N)*N_House),
    # E_PV_future(RL_HORIZON_N/RL_HORIZON_AVG_N), T_am_future(RL_HORIZON_N/RL_HORIZON_AVG_N) E_price_future(RL_HORIZON_N/RL_HORIZON_AVG_N)]

    # For E_PV -> (N_PV + N_PV_BAT) * E_PV_add (in State Creation)
    # For E_l -> E_l_add (in State Creation)
    # For E_cri -> E_add_add (in State Creation)
    # For T_am -> T_am_avg (in State Creation)

    """
    OFF-GRID State:
        [ Th(N_House),
          E_Bat(N_PV_Bat + N_Bat),
          U_ac_prev(N_House),
          E_l_now(N_House),
          E_cri_now(N_House),
          E_PV_now(1),
          T_am_now(1),
          E_l_future(H_factor * N_House),
          E_cri_future(H_factor * N_House),
          E_PV_future(H_factor),
          T_am_future(H_factor) ]
    where H_factor = RL_HORIZON_N / RL_HORIZON_AVG_N
    """

    if RL_HORIZON_AVG_N <= 0:
        raise ValueError("RL_HORIZON_AVG_N must be > 0")

    H_factor = RL_HORIZON_N // RL_HORIZON_AVG_N

    dim = (
        N_House +                     # Th(N_House)
        (N_PV_Bat + N_Bat) +          # E_Bat(N_PV_Bat + N_Bat)
        N_House +                     # U_ac_prev(N_House)
        N_House +                     # E_l_now(N_House)
        N_House +                     # E_cri_now(N_House)
        1 +                           # E_PV_now(1)
        1 +                           # T_am_now(1)
        H_factor * N_House +          # E_l_future(H_factor * N_House)
        H_factor * N_House +          # E_cri_future(H_factor * N_House)
        H_factor +                    # E_PV_future(H_factor)
        H_factor                      # T_am_future(H_factor)
    )

    low = -np.inf * np.ones(dim, dtype=np.float32)
    high =  np.inf * np.ones(dim, dtype=np.float32)
    
    return spaces.Box(low=low, high=high, dtype=np.float32)    

# -------------------- Action Space -------------------- #

def SingleHouse_OffGrid_RL_ActionSpace_Function(SmartComSim_Object):

    # Build Short Context from Env
    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House      = int(ctx["N_House"])
    N_PV_Bat     = int(ctx["N_PV_Bat"])
    N_Bat        = int(ctx["N_Bat"])
    N_PV         = int(ctx["N_PV"])
    N_None       = int(ctx["N_None"])

    # OFF-GRID Action: [U_ac(N_House), Gamma(N_PV_Bat + N_Bat), E_Load(N_House)] 

    # On-GRID Action: [U_ac(N_House), Gamma(N_PV_Bat + N_Bat), u_pv(N_PV_Bat+N_PV)]

    # For U_ac -> [-1,1] {negative will mean cooling and non-negative will mean heating}
    # For Gamma -> [-1.52, 1]
    # For E_Load -> [0,1]
    # For u_pv -> [0,1]

    """
    OFF-GRID Action:
        [ U_ac(N_House),
          Gamma(N_PV_Bat + N_Bat),
          E_Load(N_House) ]

    Ranges:
        U_ac   ∈ [-1.0, 1.0]
        Gamma  ∈ [-1.52, 1.0]
        E_Load ∈ [0.0, 1.0]
    """
    n_u_ac   = N_House
    n_gamma  = N_PV_Bat + N_Bat
    n_eload  = N_House

    dim = n_u_ac + n_gamma + n_eload

    low = np.empty(dim, dtype=np.float32)
    high = np.empty(dim, dtype=np.float32)

    # U_ac: [-1, 1]
    low[0:n_u_ac] = -1.0
    high[0:n_u_ac] = 1.0

    # Gamma: [-1.52, 1]
    start = n_u_ac
    stop = start + n_gamma
    low[start:stop] = -1.52
    high[start:stop] = 1.0

    # E_Load: [0, 1]
    start = stop
    stop = start + n_eload
    low[start:stop] = 0.0
    high[start:stop] = 1.0

    return spaces.Box(low=low, high=high, dtype=np.float32)

# -------------------- Observation Generator -------------------- #

def SingleHouse_OffGrid_RL_Observation_Generator_Function(SmartComSim_Object):

    env = SmartComSim_Object
    
    # =================================================================================
    # =================================================================================
    # INTIIAL DATA GATHERING 
    # =================================================================================
    # =================================================================================

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)    

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_rl_inputs(
        ctx      = ctx,
        E_PV     = E_PV
    )    

    # =================================================================================
    # Use reshape to construct Observation for ON/OFF Grid
    # =================================================================================

    # Off-Grid
    Observation = Exp_SingleMultiHouse_OffGrid_observation_creator(ctx, reshaped, RL_Parameters)

    # On-Grid
    # Observation = Exp_SingleMultiHouse_OnGrid_observation_creator(ctx, reshaped, RL_Parameters)

    return Observation

# -------------------- Action Generator -------------------- #

def SingleHouse_OffGrid_RL_Action_Generator_Function(SmartComSim_Object, Action):

    env = SmartComSim_Object

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)    

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_rl_inputs(
        ctx      = ctx,
        E_PV     = E_PV
    )   

    # =================================================================================
    # Get Action_Dict from Action
    # ================================================================================= 

    Action_Dict = Exp_SingleMultiHouse_OffGrid_parse_action(Action, env)

    # Action_Dict = Exp_SingleMultiHouse_OnGrid_parse_action(Action, env)

    # =================================================================================
    # Use reshape/Action_Dict to construct Observation for ON/OFF Grid
    # =================================================================================

    # Off-Grid
    action = Exp_SingleMultiHouse_OffGrid_action_creator(Action_Dict, ctx, reshaped, RL_Parameters)

    # On-Grid
    # action = Exp_SingleMultiHouse_OnGrid_action_creator(Action_Dict, ctx, reshaped, RL_Parameters)


    return action

# -------------------- Reward -------------------- #

def SingleHouse_OffGrid_RL_Reward_Function(SmartComSim_Object, observation_k_1, action_k_0, observation_k_0):

    env = SmartComSim_Object

    # =================================================================================
    # Build unified RL context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters) 

    N_House                 = int(ctx["N_House"])
    N_PV_Bat                = int(ctx["N_PV_Bat"])
    N_Bat                   = int(ctx["N_Bat"])
    N_PV                    = int(ctx["N_PV"])
    N_None                  = int(ctx["N_None"])

    T_h_Max                 = ctx["T_h_Max"]
    T_h_Min                 = ctx["T_h_Min"]
    E_AC                    = ctx["E_AC"]
    P_ac_st                 = ctx["ACLoad_StartUp_Power"]
    Eff_Inv                 = ctx["Eff_Inv"]
    E_bat_Max               = ctx["E_bat_Max"]
    E_bat_Min               = ctx["E_bat_Min"]
    Gamma_Charging          = ctx["Gamma_Charging"]
    Gamma_Discharging       = ctx["Gamma_Discharging"]
    P_bat                   = ctx["P_bat"]

    # Additional variable requested
    E_l_max                 = ctx["E_l_max"]

    E_AC                    = E_AC / Eff_Inv 

    Simulation_StepSize = env.simulation_params["Simulation_StepSize"]

    # =============================================================================
    # Extract Reward Weights from RL_Parameters
    # =============================================================================

    # Off-grid weight dictionary (returns {} if missing)
    W_off = RL_Parameters.get("OFFGRID_WEIGHTS", {})    

    W_T_h     = W_off.get("W_T_h",     0.0)
    W_Ebat    = W_off.get("W_Ebat",    0.0)
    W_Ebal    = W_off.get("W_Ebal",    0.0)
    W_startup = W_off.get("W_startup", 0.0)
    W_surplus = W_off.get("W_surplus", 0.0)
    W_load    = W_off.get("W_load",    0.0)
    W_mode    = W_off.get("W_mode",    0.0)   

    # =================================================================================
    # Parse observation_k_1
    # =================================================================================

    o_k_1_Dict = Exp_SingleMultiHouse_OffGrid_parse_observation(observation_k_1, env, RL_Parameters)

    Th_now_1      = o_k_1_Dict["Th"]            # shape: (N_House,)
    E_Bat_now_1   = o_k_1_Dict["E_Bat"]         # shape: (N_PV_Bat+N_Bat,)
    U_ac_prev_1   = o_k_1_Dict["U_ac_prev"]     # shape: (N_House,)
    E_l_now_1     = o_k_1_Dict["E_l_now"]       # shape: (N_House,)
    E_cri_now_1   = o_k_1_Dict["E_cri_now"]     # shape: (N_House,)
    E_PV_now_1    = o_k_1_Dict["E_PV_now"]      # shape: (1,)
    T_am_now_1    = o_k_1_Dict["T_am_now"]      # shape: (1,)

    # =================================================================================
    # Parse action_k_0
    # =================================================================================

    a_k_0_Dict = Exp_SingleMultiHouse_OffGrid_parse_action(action_k_0, env)

    U_ac_0   = a_k_0_Dict["U_ac"]      # shape: (N_House,)
    Gamma_0  = a_k_0_Dict["Gamma"]     # shape: (N_PV_Bat + N_Bat,)
    E_Load_0 = a_k_0_Dict["E_Load"]    # shape: (N_House,)

    U_ac_0 = (np.abs(U_ac_0) > 0.5).astype(int)
    U_ac_h = (U_ac_0 >= 0).astype(int)
    E_Load_0 = E_Load_0 * E_l_max

    # =================================================================================
    # Parse observation_k_0
    # =================================================================================

    o_k_0_Dict = Exp_SingleMultiHouse_OffGrid_parse_observation(observation_k_0, env, RL_Parameters)

    Th_now_0      = o_k_0_Dict["Th"]            # shape: (N_House,)
    E_Bat_now_0   = o_k_0_Dict["E_Bat"]         # shape: (N_PV_Bat+N_Bat,)
    U_ac_prev_0   = o_k_0_Dict["U_ac_prev"]     # shape: (N_House,)
    E_l_now_0     = o_k_0_Dict["E_l_now"]       # shape: (N_House,)
    E_cri_now_0   = o_k_0_Dict["E_cri_now"]     # shape: (N_House,)
    E_PV_now_0    = o_k_0_Dict["E_PV_now"]      # shape: (1,)
    T_am_now_0    = o_k_0_Dict["T_am_now"]      # shape: (1,)

    # =================================================================================
    # Reward Computation
    # =================================================================================

    # =================================================================================
    # Reward Computation: Thermal Comfort (T_h_Reward) - CUMULATIVE over houses
    # =================================================================================

    # Th_now_1: shape (N_House,)
    # T_h_Min, T_h_Max: scalar or array-like (broadcastable to (N_House,))

    # 1) Temperature violations
    violation_cold = np.maximum(T_h_Min - Th_now_1, 0.0)   # too cold
    violation_hot  = np.maximum(Th_now_1 - T_h_Max, 0.0)   # too hot

    temp_violation = violation_cold + violation_hot        # shape: (N_House,)

    # 2) Per-house reward:
    #    - inside band: temp_violation = 0  → reward = +1
    #    - outside band: reward = 1 - (distance outside band)
    T_h_reward_per_house = 1.0 - temp_violation            # shape: (N_House,)

    # 3) Cumulative reward over all houses
    T_h_Reward = float(np.sum(T_h_reward_per_house))       # scalar

    # =================================================================================
    # Reward Computation: Battery SOC (E_bat_Reward) - CUMULATIVE over batteries
    # =================================================================================

    # E_Bat_now_1: shape (N_PV_Bat + N_Bat,)
    # E_bat_Min, E_bat_Max from ctx (broadcastable)

    # 1) Define safe region
    safe_min = 0.05 * (E_bat_Max)    # 5% above minimum SOC
    safe_max = E_bat_Max           # maximum SOC allowed

    # 2) Violations
    violation_low  = np.maximum(safe_min - E_Bat_now_1, 0.0)   # below safe min
    #violation_high = np.maximum(E_Bat_now_1 - safe_max, 0.0)   # above max

    total_violation = violation_low #+ violation_high           # shape: (Nbatt,)

    # 3) Per-battery reward
    #    inside band → violation = 0 → reward = +1
    #    outside band → reward = 1 - violation magnitude
    Ebat_reward_per_battery = 1.0 - total_violation

    # 4) Cumulative reward over all batteries
    Ebat_Reward = float(np.sum(Ebat_reward_per_battery))

    # ---------------------------------------------------------------------------------
    # Reward: Energy Balance
    # ---------------------------------------------------------------------------------

    # U_ac_0: (N_House,)   already binarized {0,1}
    # E_AC:   scalar or (N_House,)   per-house AC energy per step
    # E_Load_0: (N_House,)  already scaled by E_l_max

    E_ac_total   = float(np.sum(U_ac_0 * E_AC))   # total AC energy demand
    E_load_total = float(np.sum(E_Load_0))        # total flexible load demand

    Demand_total = E_ac_total + E_load_total      # scalar

    # E_PV_now_0: shape (1,) or scalar-like
    # Gamma_0:    shape (N_PV_Bat + N_Bat,)
    # P_bat:      scalar or (N_PV_Bat + N_Bat,)  -> per-step energy capacity

    E_pv_total = float(np.sum(E_PV_now_0)) * (N_PV_Bat + N_PV) 

    # Per-step battery energy term (c,dc) – using P_bat as the base magnitude
    E_bat_step = Gamma_Discharging * Simulation_StepSize                           # broadcasts as needed
    E_bat_contrib_total = float(np.sum(Gamma_0 * E_bat_step))

    Generation_total = E_pv_total + E_bat_contrib_total

    energy_deficit = max(Demand_total - Generation_total, 0.0)  # scalar ≥ 0

    Ebal_Reward = 1.0 - energy_deficit

    # ------------------------------------------------------------------------------
    # Reward: AC startup power feasibility (R_startup)
    # ------------------------------------------------------------------------------

    # U_ac_prev_0: shape (N_House,), previous AC command/state from o_k_0
    # U_ac_0:      shape (N_House,), current AC action after binarization {0,1}

    # f_on_0 = 1 where AC was OFF and now is ON (startup event)
    f_on_0 = ((U_ac_prev_0 <= 1) & (U_ac_0 >= 1)).astype(float)  # shape: (N_House,)

    # θ_bat = 1 if Gamma > 0 (discharging), else 0
    theta_bat_0 = (Gamma_0 > 0).astype(float)     # shape: (N_PV_Bat + N_Bat,)

    # P_ac_st: from ctx["ACLoad_StartUp_Power"] (scalar or (N_House,))
    # theta_bat_0: e.g.,
    # theta_bat_0 = a_k_0_Dict["theta_bat"]     # shape: (N_PV_Bat + N_Bat,)
    # P_bat: from ctx["P_bat"] (scalar or per-battery)
    # E_PV_now_0: shape (1,) or scalar-like
    # Delta_Ts: sampling period (from ctx or RL_Parameters)
    Delta_Ts = Simulation_StepSize   # make sure this exists in your ctx

    # Total startup power demand [kW]
    P_startup_total = float(np.sum(f_on_0 * P_ac_st))

    # Available battery discharge power [kW]
    P_bat_avail = float(np.sum(theta_bat_0 * P_bat))

    # PV power [kW] approximated from energy over step
    P_pv_avail = float(np.sum(E_PV_now_0)) * (N_PV_Bat + N_PV) / float(Delta_Ts)

    # Total available fast power
    P_avail_total = P_bat_avail + P_pv_avail

    # Power deficit (positive = not enough power, negative/zero = OK)
    P_deficit = P_startup_total - P_avail_total

    if np.sum(f_on_0) > 0:
        # There is at least one AC starting
        if P_deficit <= 0.0:
            R_startup = 1.0
        else:
            R_startup = 1.0 - P_deficit
    else:
        # No startup event: neutral contribution
        R_startup = 0.0

    # --------------------------------------------------------------
    # Surplus-waste penalty: separate reward term (scaled)
    # --------------------------------------------------------------

    raw_diff       = Demand_total - Generation_total    # +deficit, -surplus
    energy_surplus = max(-raw_diff, 0.0)                # surplus (>= 0)

    # Battery charging status
    is_charging_array = (Gamma_0 < 0.0)                 # True where charging
    num_charging      = int(np.sum(is_charging_array))
    num_batteries     = len(Gamma_0)
    num_not_charging  = num_batteries - num_charging

    # Condition:
    # Penalize if surplus exists AND at least one battery is NOT charging
    if energy_surplus > 0.0 and num_charging < num_batteries:
        # scaled penalty
        R_surplus = - energy_surplus * num_not_charging
    else:
        # Either no surplus, or ALL batteries are charging
        R_surplus = 0.0

    # --------------------------------------------------------------
    # Flexible load / critical load reward (IF–ELSE version)
    # --------------------------------------------------------------

    R_load_per_house = np.zeros(N_House, dtype=float)

    for i in range(N_House):

        Eload = float(E_Load_0[i])        # served (action)
        El    = float(E_l_now_0[i])       # requested
        Ecri  = float(E_cri_now_0[i])     # critical demand

        # Safety: no negative served load
        if Eload < 0:
            Eload = 0.0

        # ----------------------------------------------------------
        # CASE 0: No flexible load requested
        # ----------------------------------------------------------
        if El <= 0.0:

            if Eload > 0.0:
                # Penalty for serving load when none is asked for
                R_load_per_house[i] = - Eload
            else:
                # No load asked and none served -> neutral
                R_load_per_house[i] = 0.0

            continue  # Skip rest of cases for this house

        # ----------------------------------------------------------
        # CASE A: Fully served or overserved
        # ----------------------------------------------------------
        if Eload >= El:
            R_load_per_house[i] = 1.0

        # ----------------------------------------------------------
        # CASE B: Between critical and full demand
        #          reward = Eload / El
        # ----------------------------------------------------------
        elif (Eload >= Ecri) and (Eload < El):
            R_load_per_house[i] = Eload / El

        # ----------------------------------------------------------
        # CASE C: Below critical load
        #          heavy penalty = -100 * (Ecri - Eload)
        # ----------------------------------------------------------
        else:   # Eload < Ecri
            R_load_per_house[i] = -100.0 * (Ecri - Eload)

    # Sum across houses
    R_load = float(np.sum(R_load_per_house))

    # --------------------------------------------------------------
    # Heating/Cooling mode correctness reward (R_mode)
    # --------------------------------------------------------------

    R_mode_per_house = np.zeros(N_House, dtype=float)

    T_am = float(T_am_now_0)   # scalar from observation

    for i in range(N_House):

        Th   = float(Th_now_0[i])            # indoor temperature
        mode = int(U_ac_h[i])                # 1 = heating, 0 = cooling

        deltaT = abs(T_am - Th)

        # ----------------------------------------------------------
        # CASE 1: Ambient hotter than indoor (T_am > T_h)
        # ----------------------------------------------------------
        if T_am > Th:

            if mode == 1:
                # Heating when indoor < outdoor -> WRONG
                R_mode_per_house[i] = -deltaT
            else:
                # Cooling when indoor < outdoor -> CORRECT
                R_mode_per_house[i] = 1.0

        # ----------------------------------------------------------
        # CASE 2: Ambient colder than indoor (T_am < T_h)
        # ----------------------------------------------------------
        elif T_am < Th:

            if mode == 0:
                # Cooling when indoor > outdoor -> WRONG
                R_mode_per_house[i] = -deltaT
            else:
                # Heating when indoor > outdoor -> CORRECT
                R_mode_per_house[i] = 1.0

        # ----------------------------------------------------------
        # CASE 3: Ambient == indoor (rare) -> Neutral
        # ----------------------------------------------------------
        else:
            R_mode_per_house[i] = 0.0

    # Cumulative reward
    R_mode = float(np.sum(R_mode_per_house))

    Reward = (
        W_T_h       * T_h_Reward      +    # thermal comfort
        W_Ebat      * Ebat_Reward     +    # battery SOC
        W_Ebal      * Ebal_Reward     +    # energy balance
        W_startup   * R_startup       +    # AC startup feasibility
        W_surplus   * R_surplus       +    # surplus waste penalty
        W_load      * R_load          +    # flexible vs critical load performance
        W_mode      * R_mode               # heating/cooling correctness
    )  


    return Reward

# -------------------- Terminate -------------------- #

def SingleHouse_OffGrid_RL_Terminate_Function(SmartComSim_Object):
    """
    Natural (MDP) termination for smart community RL.
    Uses ONLY ctx (no external inputs).

    Episode TERMINATES if:
      1) ALL house temperatures fall outside the allowed band:
            T_set ± 5°C
         (either all too cold or all too hot)
      OR
      2) ALL batteries (if present) have energy in the low band:
            [E_bat_min, E_bat_min + 0.05*(E_bat_max - E_bat_min)]
    """

    env = SmartComSim_Object

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)      

    # ------------------------------------------------------------
    # 1. TEMPERATURE-BASED TERMINATION
    # ------------------------------------------------------------

    # Current temps (stored inside ctx)
    T_h = np.array(ctx["T_h_Init"])   # shape (N_House,)

    # Setpoint = midpoint of min & max
    T_set = 0.5 * (ctx["T_h_Min"] + ctx["T_h_Max"])

    # Band = setpoint ± 5°C
    band = 5.0
    T_low_band = T_set - band
    T_high_band = T_set + band

    # Check:
    too_cold_all = np.all(T_h < T_low_band)
    too_hot_all  = np.all(T_h > T_high_band)

    thermal_failure = bool(too_cold_all or too_hot_all)

    # ------------------------------------------------------------
    # 2. BATTERY-BASED TERMINATION
    # ------------------------------------------------------------

    N_total_bats = ctx["N_PV_Bat"] + ctx["N_Bat"]

    if N_total_bats > 0:
        # Current E_bat from ctx
        E_bat = np.array(ctx["E_bat_Init"])  # shape (N_total_bats,)

        # Band width = 5% of usable range
        E_min = ctx["E_bat_Min"]
        E_max = ctx["E_bat_Max"]
        low_band_width = 0.0005 * (E_max - E_min)

        low_band_lower = E_min
        low_band_upper = E_min + low_band_width

        bat_low_all = np.all(
            (E_bat >= low_band_lower) & (E_bat <= low_band_upper)
        )

        battery_failure = bool(bat_low_all)

    else:
        battery_failure = False

    # ------------------------------------------------------------
    # 3. COMBINE CONDITIONS
    # ------------------------------------------------------------
    Terminate = thermal_failure or battery_failure

    return Terminate

# -------------------- Truncate -------------------- #

def SingleHouse_OffGrid_RL_Truncate_Function(SmartComSim_Object):

    """
    Determine whether the episode should end because we are too close 
    to the end of the dataset to provide the required future horizon.
    
    NOTE:
    -----
    This is an ARTIFICIAL end (dataset boundary), so in Gymnasium/SB3
    this must be mapped to:
        terminated = False
        truncated  = True
    even though internally we return `Terminate = True` here.
    
    Parameters
    ----------
    env : SmartComSim_Object
        The active simulation environment instance.
    
    RL_Parameters : dict
        Contains RL settings, specifically:
            RL_HORIZON_N : int
                Number of future steps required to construct the state.
    
    Returns
    -------
    bool
        True  -> We must end this episode (dataset boundary reached).
        False -> Episode can continue normally.
    """

    env = SmartComSim_Object

    # Total number of steps available in the full dataset (e.g., 1 year)
    total_steps = env.Simulation_Steps_Total

    # To construct a future-horizon state at time t, we need:
    #     t + RL_HORIZON_N < total_steps
    # This means the RL agent can only operate safely until:
    max_safe_step = total_steps - RL_Parameters["RL_HORIZON_N"]

    # Current timestep in the environment
    current_step = env.time_iter

    # If we exceed or reach the data boundary threshold,
    # we cannot supply future horizon data -> must end episode.
    if current_step >= max_safe_step - 1:
        Terminate = True   # Artificial termination → will map to truncated
    else:
        Terminate = False

    return Terminate

#-------------------------------------------------------------------------------------------------------------#
# Single House On-Grid RL
#-------------------------------------------------------------------------------------------------------------#

# -------------------- Observation Space -------------------- #

def SingleHouse_OnGrid_RL_ObservationSpace_Function(SmartComSim_Object):

    # Build Short Context from Env
    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House      = int(ctx["N_House"])
    N_PV_Bat     = int(ctx["N_PV_Bat"])
    N_Bat        = int(ctx["N_Bat"])
    N_PV         = int(ctx["N_PV"])
    N_None       = int(ctx["N_None"])

    # Get desired RL_Parameters
    RL_HORIZON_N = int(RL_Parameters["RL_HORIZON_N"])
    RL_HORIZON_AVG_N = int(RL_Parameters["RL_HORIZON_AVG_N"])

    """
    ON-GRID State:
        [ Th(N_House),
          E_Bat(N_PV_Bat + N_Bat),
          E_l_now(N_House),
          E_PV_now(1),
          T_am_now(1),
          E_Price_now(1),
          E_l_future(H_factor * N_House),
          E_PV_future(H_factor),
          T_am_future(H_factor),
          E_price_future(H_factor) ]
    where H_factor = RL_HORIZON_N / RL_HORIZON_AVG_N
    """

    if RL_HORIZON_AVG_N <= 0:
        raise ValueError("RL_HORIZON_AVG_N must be > 0")

    H_factor = RL_HORIZON_N // RL_HORIZON_AVG_N

    dim = (
        N_House +                     # Th(N_House)
        (N_PV_Bat + N_Bat) +          # E_Bat(N_PV_Bat + N_Bat)
        N_House +                     # E_l_now(N_House)
        1 +                           # E_PV_now(1)
        1 +                           # T_am_now(1)
        1 +                           # E_Price_now(1)
        H_factor * N_House +          # E_l_future(H_factor * N_House)
        H_factor +                    # E_PV_future(H_factor)
        H_factor +                    # T_am_future(H_factor)
        H_factor                      # E_price_future(H_factor)
    )

    low = -np.inf * np.ones(dim, dtype=np.float32)
    high =  np.inf * np.ones(dim, dtype=np.float32)

    return spaces.Box(low=low, high=high, dtype=np.float32)

# -------------------- Action Space -------------------- #

def SingleHouse_OnGrid_RL_ActionSpace_Function(SmartComSim_Object):

    # Build Short Context from Env
    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House      = int(ctx["N_House"])
    N_PV_Bat     = int(ctx["N_PV_Bat"])
    N_Bat        = int(ctx["N_Bat"])
    N_PV         = int(ctx["N_PV"])
    N_None       = int(ctx["N_None"])

    # OFF-GRID Action: [U_ac(N_House), Gamma(N_PV_Bat + N_Bat), E_Load(N_House)] 

    # On-GRID Action: [U_ac(N_House), Gamma(N_PV_Bat + N_Bat), u_pv(N_PV_Bat+N_PV)]

    # For U_ac -> [-1,1] {negative will mean cooling and non-negative will mean heating}
    # For Gamma -> [-1.52, 1]
    # For E_Load -> [0,1]
    # For u_pv -> [0,1]

    """
    ON-GRID Action:
        [ U_ac(N_House),
          Gamma(N_PV_Bat + N_Bat),
          u_pv(N_PV_Bat + N_PV) ]

    Ranges:
        U_ac ∈ [-1.0, 1.0]
        Gamma ∈ [-1.52, 1.0]
        u_pv ∈ [0.0, 1.0]
    """
    n_u_ac  = N_House
    n_gamma = N_PV_Bat + N_Bat
    n_upv   = N_PV_Bat + N_PV

    dim = n_u_ac + n_gamma + n_upv

    low = np.empty(dim, dtype=np.float32)
    high = np.empty(dim, dtype=np.float32)

    # U_ac: [-1, 1]
    low[0:n_u_ac] = -1.0
    high[0:n_u_ac] = 1.0

    # Gamma: [-1.52, 1]
    start = n_u_ac
    stop = start + n_gamma
    low[start:stop] = -1.52
    high[start:stop] = 1.0

    # u_pv: [0, 1]
    start = stop
    stop = start + n_upv
    low[start:stop] = 0.0
    high[start:stop] = 1.0

    return spaces.Box(low=low, high=high, dtype=np.float32)

# -------------------- Observation Generator -------------------- #

def SingleHouse_OnGrid_RL_Observation_Generator_Function(SmartComSim_Object):

    env = SmartComSim_Object
    
    # =================================================================================
    # =================================================================================
    # INTIIAL DATA GATHERING 
    # =================================================================================
    # =================================================================================

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)    

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_rl_inputs(
        ctx      = ctx,
        E_PV     = E_PV
    )    

    # =================================================================================
    # Use reshape to construct Observation for ON/OFF Grid
    # =================================================================================

    # Off-Grid
    # Observation = Exp_SingleMultiHouse_OffGrid_observation_creator(ctx, reshaped, RL_Parameters)

    # On-Grid
    Observation = Exp_SingleMultiHouse_OnGrid_observation_creator(ctx, reshaped, RL_Parameters)

    return Observation

# -------------------- Action Generator -------------------- #

def SingleHouse_OnGrid_RL_Action_Generator_Function(SmartComSim_Object, Action):

    env = SmartComSim_Object

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)    

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_rl_inputs(
        ctx      = ctx,
        E_PV     = E_PV
    )   

    # =================================================================================
    # Get Action_Dict from Action
    # ================================================================================= 

    #Action_Dict = Exp_SingleMultiHouse_OffGrid_parse_action(Action, env)

    Action_Dict = Exp_SingleMultiHouse_OnGrid_parse_action(Action, env)

    # =================================================================================
    # Use reshape/Action_Dict to construct Observation for ON/OFF Grid
    # =================================================================================

    # Off-Grid
    # action = Exp_SingleMultiHouse_OffGrid_action_creator(Action_Dict, ctx, reshaped, RL_Parameters)

    # On-Grid
    action = Exp_SingleMultiHouse_OnGrid_action_creator(Action_Dict, ctx, reshaped, RL_Parameters)


    return action

# -------------------- Reward -------------------- #

def SingleHouse_OnGrid_RL_Reward_Function(SmartComSim_Object, observation_k_1, action_k_0, observation_k_0):

    env = SmartComSim_Object

    # =================================================================================
    # Build unified RL context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters) 

    N_House                 = int(ctx["N_House"])
    N_PV_Bat                = int(ctx["N_PV_Bat"])
    N_Bat                   = int(ctx["N_Bat"])
    N_PV                    = int(ctx["N_PV"])
    N_None                  = int(ctx["N_None"])

    T_h_Max                 = ctx["T_h_Max"]
    T_h_Min                 = ctx["T_h_Min"]
    E_AC                    = ctx["E_AC"]
    P_ac_st                 = ctx["ACLoad_StartUp_Power"]
    Eff_Inv                 = ctx["Eff_Inv"]
    E_bat_Max               = ctx["E_bat_Max"]
    E_bat_Min               = ctx["E_bat_Min"]
    Gamma_Charging          = ctx["Gamma_Charging"]
    Gamma_Discharging       = ctx["Gamma_Discharging"]
    P_bat                   = ctx["P_bat"]

    # Additional variable requested
    E_l_max                 = ctx["E_l_max"]

    E_AC                    = E_AC / Eff_Inv 

    Simulation_StepSize = env.simulation_params["Simulation_StepSize"]

    # =============================================================================
    # Extract Reward Weights from RL_Parameters
    # =============================================================================

    # On-grid weight dictionary (returns {} if missing)
    W_on  = RL_Parameters.get("ONGRID_WEIGHTS", {})
    
    W_T_h     = W_on.get("W_T_h",     0.0)
    W_Ebat    = W_on.get("W_Ebat",    0.0)
    W_cost    = W_on.get("W_cost",    0.0)
    W_PV      = W_on.get("W_PV",      0.0)
    W_u_pv    = W_on.get("W_u_pv",    0.0)
    W_mode    = W_on.get("W_mode",    0.0)

    # =================================================================================
    # Parse observation_k_1
    # =================================================================================

    o_k_1_Dict = Exp_SingleMultiHouse_OffGrid_parse_observation(observation_k_1, env, RL_Parameters)

    Th_now_1      = o_k_1_Dict["Th"]            # shape: (N_House,)
    E_Bat_now_1   = o_k_1_Dict["E_Bat"]         # shape: (N_PV_Bat+N_Bat,)
    E_l_now_1     = o_k_1_Dict["E_l_now"]       # shape: (N_House,)
    E_Price_now_1 = o_k_1_Dict["E_Price_now"]   # shape: (1,)
    E_PV_now_1    = o_k_1_Dict["E_PV_now"]      # shape: (1,)
    T_am_now_1    = o_k_1_Dict["T_am_now"]      # shape: (1,)

    # =================================================================================
    # Parse action_k_0
    # =================================================================================

    a_k_0_Dict = Exp_SingleMultiHouse_OffGrid_parse_action(action_k_0, env)

    U_ac_0   = a_k_0_Dict["U_ac"]      # shape: (N_House,)
    Gamma_0  = a_k_0_Dict["Gamma"]     # shape: (N_PV_Bat + N_Bat,)
    U_pv_0   = a_k_0_Dict["u_pv"]      # shape: (N_PV_Bat + N_PV,)

    U_ac_0 = (np.abs(U_ac_0) > 0.5).astype(int)
    U_ac_h = (U_ac_0 >= 0).astype(int)

    # =================================================================================
    # Parse observation_k_0
    # =================================================================================

    o_k_0_Dict = Exp_SingleMultiHouse_OffGrid_parse_observation(observation_k_0, env, RL_Parameters)

    Th_now_0      = o_k_0_Dict["Th"]            # shape: (N_House,)
    E_Bat_now_0   = o_k_0_Dict["E_Bat"]         # shape: (N_PV_Bat+N_Bat,)
    E_l_now_0     = o_k_0_Dict["E_l_now"]       # shape: (N_House,)
    E_Price_now_0 = o_k_0_Dict["E_Price_now"]   # shape: (1,)
    E_PV_now_0    = o_k_0_Dict["E_PV_now"]      # shape: (1,)
    T_am_now_0    = o_k_0_Dict["T_am_now"]      # shape: (1,)

    # =================================================================================
    # Reward Computation
    # =================================================================================

    # =================================================================================
    # Reward Computation: Thermal Comfort (T_h_Reward) - CUMULATIVE over houses
    # =================================================================================

    # Th_now_1: shape (N_House,)
    # T_h_Min, T_h_Max: scalar or array-like (broadcastable to (N_House,))

    # 1) Temperature violations
    violation_cold = np.maximum(T_h_Min - Th_now_1, 0.0)   # too cold
    violation_hot  = np.maximum(Th_now_1 - T_h_Max, 0.0)   # too hot

    temp_violation = violation_cold + violation_hot        # shape: (N_House,)

    # 2) Per-house reward:
    #    - inside band: temp_violation = 0  → reward = +1
    #    - outside band: reward = 1 - (distance outside band)
    T_h_reward_per_house = 1.0 - temp_violation            # shape: (N_House,)

    # 3) Cumulative reward over all houses
    T_h_Reward = float(np.sum(T_h_reward_per_house))       # scalar

    # =================================================================================
    # Reward Computation: Battery SOC (E_bat_Reward) - CUMULATIVE over batteries
    # =================================================================================

    # E_Bat_now_1: shape (N_PV_Bat + N_Bat,)
    # E_bat_Min, E_bat_Max from ctx (broadcastable)

    # 1) Define safe region
    safe_min = 0.05 * (E_bat_Max)    # 5% above minimum SOC
    safe_max = E_bat_Max           # maximum SOC allowed

    # 2) Violations
    violation_low  = np.maximum(safe_min - E_Bat_now_1, 0.0)   # below safe min
    #violation_high = np.maximum(E_Bat_now_1 - safe_max, 0.0)   # above max

    total_violation = violation_low #+ violation_high           # shape: (Nbatt,)

    # 3) Per-battery reward
    #    inside band → violation = 0 → reward = +1
    #    outside band → reward = 1 - violation magnitude
    Ebat_reward_per_battery = 1.0 - total_violation

    # 4) Cumulative reward over all batteries
    Ebat_Reward = float(np.sum(Ebat_reward_per_battery))     

    # --------------------------------------------------------------
    # Heating/Cooling mode correctness reward (R_mode)
    # --------------------------------------------------------------

    R_mode_per_house = np.zeros(N_House, dtype=float)

    T_am = float(T_am_now_0)   # scalar from observation

    for i in range(N_House):

        Th   = float(Th_now_0[i])            # indoor temperature
        mode = int(U_ac_h[i])                # 1 = heating, 0 = cooling

        deltaT = abs(T_am - Th)

        # ----------------------------------------------------------
        # CASE 1: Ambient hotter than indoor (T_am > T_h)
        # ----------------------------------------------------------
        if T_am > Th:

            if mode == 1:
                # Heating when indoor < outdoor -> WRONG
                R_mode_per_house[i] = -deltaT
            else:
                # Cooling when indoor < outdoor -> CORRECT
                R_mode_per_house[i] = 1.0

        # ----------------------------------------------------------
        # CASE 2: Ambient colder than indoor (T_am < T_h)
        # ----------------------------------------------------------
        elif T_am < Th:

            if mode == 0:
                # Cooling when indoor > outdoor -> WRONG
                R_mode_per_house[i] = -deltaT
            else:
                # Heating when indoor > outdoor -> CORRECT
                R_mode_per_house[i] = 1.0

        # ----------------------------------------------------------
        # CASE 3: Ambient == indoor (rare) -> Neutral
        # ----------------------------------------------------------
        else:
            R_mode_per_house[i] = 0.0

    # Cumulative reward
    R_mode = float(np.sum(R_mode_per_house))

    # =================================================================================
    # 1) Common energy terms (On-Grid)
    # =================================================================================

    # Total AC energy demand (kWh in this step)
    E_ac_total = float(np.sum(U_ac_0 * E_AC))

    # Total inflexible load demand (kWh) from observation
    E_load_total = float(np.sum(E_l_now_0))

    # Battery discharge energy (kWh) this step
    Gamma_discharge = np.maximum(Gamma_0, 0.0)   # only discharging contributes
    E_bat_dis_total = float(np.sum(Gamma_discharge * Gamma_Discharging * Simulation_StepSize ))

    # PV energy available this step (kWh)
    E_pv_avail = float(np.sum(E_PV_now_0)) * (N_PV_Bat + N_PV)

    # Effective PV utilization factor from u_pv (clip to [0,1])
    if E_pv_avail > 0.0:
        # assume U_pv_0 in [-1,1] or [0,1], we only care about "using" PV (>=0)
        u_pv_eff = float(np.clip(np.mean(np.maximum(U_pv_0, 0.0)), 0.0, 1.0))
    else:
        u_pv_eff = 0.0

    # PV actually used (kWh)
    E_pv_used = u_pv_eff * E_pv_avail

    # Grid import (kWh): what’s left after PV + battery discharge
    Demand_total     = E_ac_total + E_load_total
    Supply_local     = E_pv_used + E_bat_dis_total
    E_grid_import    = Demand_total - Supply_local

    # =================================================================================
    # 2) R_cost  – minimize grid energy cost
    # =================================================================================

    price = float(E_Price_now_0)   # scalar price for this step

    Step_Cost = price * E_grid_import    # [$/step] or arbitrary unit
    R_cost = -Step_Cost                  # reward is negative cost

    # =================================================================================
    # 3) R_PV – penalize PV curtailment (maximize utilization)
    # =================================================================================

    E_pv_curt = max(E_pv_avail - E_pv_used, 0.0)   # kWh curtailed

    # Simple choice: linear penalty with curtailment
    R_PV = -E_pv_curt

    # =================================================================================
    # 4) R_u_pv – penalize u_pv > 0 when E_pv == 0
    # =================================================================================

    if E_pv_avail <= 0.0:
        # Any positive PV utilization command when there is no PV?
        u_pv_pos = np.maximum(U_pv_0, 0.0)
        if np.any(u_pv_pos > 0.0):
            # penalty proportional to "how much" PV is being commanded
            R_u_pv = -np.sum(u_pv_pos)
        else:
            R_u_pv = 0.0
    else:
        # PV available, no penalty here
        R_u_pv = 0.0

    Reward = (
        W_T_h  * T_h_Reward   +   # from off-grid design
        W_Ebat * Ebat_Reward  +   # from off-grid design
        W_mode * R_mode       +   # from off-grid design
        W_cost * R_cost       +   # new on-grid term
        W_PV   * R_PV         +   # new on-grid term
        W_u_pv * R_u_pv           # new on-grid term
    )  

    return Reward

# -------------------- Terminate -------------------- #

def SingleHouse_OnGrid_RL_Terminate_Function(SmartComSim_Object):

    """
    Natural (MDP) termination for smart community RL.
    Uses ONLY ctx (no external inputs).

    Episode TERMINATES if:
      1) ALL house temperatures fall outside the allowed band:
            T_set ± 5°C
         (either all too cold or all too hot)
      OR
      2) ALL batteries (if present) have energy in the low band:
            [E_bat_min, E_bat_min + 0.05*(E_bat_max - E_bat_min)]
    """

    env = SmartComSim_Object

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)      

    # ------------------------------------------------------------
    # 1. TEMPERATURE-BASED TERMINATION
    # ------------------------------------------------------------

    # Current temps (stored inside ctx)
    T_h = np.array(ctx["T_h_Init"])   # shape (N_House,)

    # Setpoint = midpoint of min & max
    T_set = 0.5 * (ctx["T_h_Min"] + ctx["T_h_Max"])

    # Band = setpoint ± 5°C
    band = 5.0
    T_low_band = T_set - band
    T_high_band = T_set + band

    # Check:
    too_cold_all = np.all(T_h < T_low_band)
    too_hot_all  = np.all(T_h > T_high_band)

    thermal_failure = bool(too_cold_all or too_hot_all)

    # ------------------------------------------------------------
    # 2. BATTERY-BASED TERMINATION
    # ------------------------------------------------------------

    N_total_bats = ctx["N_PV_Bat"] + ctx["N_Bat"]

    if N_total_bats > 0:
        # Current E_bat from ctx
        E_bat = np.array(ctx["E_bat_Init"])  # shape (N_total_bats,)

        # Band width = 5% of usable range
        E_min = ctx["E_bat_Min"]
        E_max = ctx["E_bat_Max"]
        low_band_width = 0.0005 * (E_max - E_min)

        low_band_lower = E_min
        low_band_upper = E_min + low_band_width

        bat_low_all = np.all(
            (E_bat >= low_band_lower) & (E_bat <= low_band_upper)
        )

        battery_failure = bool(bat_low_all)

    else:
        battery_failure = False

    # ------------------------------------------------------------
    # 3. COMBINE CONDITIONS
    # ------------------------------------------------------------
    Terminate = thermal_failure or battery_failure

    return Terminate

# -------------------- Truncate -------------------- #

def SingleHouse_OnGrid_RL_Truncate_Function(SmartComSim_Object):

    """
    Determine whether the episode should end because we are too close 
    to the end of the dataset to provide the required future horizon.
    
    NOTE:
    -----
    This is an ARTIFICIAL end (dataset boundary), so in Gymnasium/SB3
    this must be mapped to:
        terminated = False
        truncated  = True
    even though internally we return `Terminate = True` here.
    
    Parameters
    ----------
    env : SmartComSim_Object
        The active simulation environment instance.
    
    RL_Parameters : dict
        Contains RL settings, specifically:
            RL_HORIZON_N : int
                Number of future steps required to construct the state.
    
    Returns
    -------
    bool
        True  -> We must end this episode (dataset boundary reached).
        False -> Episode can continue normally.
    """

    env = SmartComSim_Object

    # Total number of steps available in the full dataset (e.g., 1 year)
    total_steps = env.Simulation_Steps_Total

    # To construct a future-horizon state at time t, we need:
    #     t + RL_HORIZON_N < total_steps
    # This means the RL agent can only operate safely until:
    max_safe_step = total_steps - RL_Parameters["RL_HORIZON_N"]

    # Current timestep in the environment
    current_step = env.time_iter

    # If we exceed or reach the data boundary threshold,
    # we cannot supply future horizon data -> must end episode.
    if current_step >= max_safe_step - 1:
        Terminate = True   # Artificial termination → will map to truncated
    else:
        Terminate = False

    return Terminate

#-------------------------------------------------------------------------------------------------------------#
# Multi House Off-Grid RL
#-------------------------------------------------------------------------------------------------------------#

# -------------------- Observation Space -------------------- #

def MultiHouse_OffGrid_RL_ObservationSpace_Function(SmartComSim_Object):

    # Build Short Context from Env
    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House      = int(ctx["N_House"])
    N_PV_Bat     = int(ctx["N_PV_Bat"])
    N_Bat        = int(ctx["N_Bat"])
    N_PV         = int(ctx["N_PV"])
    N_None       = int(ctx["N_None"])

    # Get desired RL_Parameters
    RL_HORIZON_N = int(RL_Parameters["RL_HORIZON_N"])
    RL_HORIZON_AVG_N = int(RL_Parameters["RL_HORIZON_AVG_N"])

    # OFF-GRID State: [Th(N_House), E_Bat(N_PV_Bat+N_Bat), U_ac_prev(N_House), 
    # E_l_now(N_House), E_cri_now(N_House), 
    # E_PV_now(1), T_am_now(1), 
    # E_l_future((RL_HORIZON_N/RL_HORIZON_AVG_N)*N_House), E_cri_future((RL_HORIZON_N/RL_HORIZON_AVG_N)*N_House), 
    # E_PV_future(RL_HORIZON_N/RL_HORIZON_AVG_N), T_am_future(RL_HORIZON_N/RL_HORIZON_AVG_N) ]

    # On-GRID State: [Th(N_House), E_Bat(N_PV_Bat+N_Bat), 
    # E_l_now(N_House),  
    # E_PV_now(1), T_am_now(1), E_Price_now(1)
    # E_l_future((RL_HORIZON_N/RL_HORIZON_AVG_N)*N_House),
    # E_PV_future(RL_HORIZON_N/RL_HORIZON_AVG_N), T_am_future(RL_HORIZON_N/RL_HORIZON_AVG_N) E_price_future(RL_HORIZON_N/RL_HORIZON_AVG_N)]

    # For E_PV -> (N_PV + N_PV_BAT) * E_PV_add (in State Creation)
    # For E_l -> E_l_add (in State Creation)
    # For E_cri -> E_add_add (in State Creation)
    # For T_am -> T_am_avg (in State Creation)

    """
    OFF-GRID State:
        [ Th(N_House),
          E_Bat(N_PV_Bat + N_Bat),
          U_ac_prev(N_House),
          E_l_now(N_House),
          E_cri_now(N_House),
          E_PV_now(1),
          T_am_now(1),
          E_l_future(H_factor * N_House),
          E_cri_future(H_factor * N_House),
          E_PV_future(H_factor),
          T_am_future(H_factor) ]
    where H_factor = RL_HORIZON_N / RL_HORIZON_AVG_N
    """

    if RL_HORIZON_AVG_N <= 0:
        raise ValueError("RL_HORIZON_AVG_N must be > 0")

    H_factor = RL_HORIZON_N // RL_HORIZON_AVG_N

    dim = (
        N_House +                     # Th(N_House)
        (N_PV_Bat + N_Bat) +          # E_Bat(N_PV_Bat + N_Bat)
        N_House +                     # U_ac_prev(N_House)
        N_House +                     # E_l_now(N_House)
        N_House +                     # E_cri_now(N_House)
        1 +                           # E_PV_now(1)
        1 +                           # T_am_now(1)
        H_factor * N_House +          # E_l_future(H_factor * N_House)
        H_factor * N_House +          # E_cri_future(H_factor * N_House)
        H_factor +                    # E_PV_future(H_factor)
        H_factor                      # T_am_future(H_factor)
    )

    low = -np.inf * np.ones(dim, dtype=np.float32)
    high =  np.inf * np.ones(dim, dtype=np.float32)
    
    return spaces.Box(low=low, high=high, dtype=np.float32) 

# -------------------- Action Space -------------------- #

def MultiHouse_OffGrid_RL_ActionSpace_Function(SmartComSim_Object):

    # Build Short Context from Env
    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House      = int(ctx["N_House"])
    N_PV_Bat     = int(ctx["N_PV_Bat"])
    N_Bat        = int(ctx["N_Bat"])
    N_PV         = int(ctx["N_PV"])
    N_None       = int(ctx["N_None"])

    # OFF-GRID Action: [U_ac(N_House), Gamma(N_PV_Bat + N_Bat), E_Load(N_House)] 

    # On-GRID Action: [U_ac(N_House), Gamma(N_PV_Bat + N_Bat), u_pv(N_PV_Bat+N_PV)]

    # For U_ac -> [-1,1] {negative will mean cooling and non-negative will mean heating}
    # For Gamma -> [-1.52, 1]
    # For E_Load -> [0,1]
    # For u_pv -> [0,1]

    """
    OFF-GRID Action:
        [ U_ac(N_House),
          Gamma(N_PV_Bat + N_Bat),
          E_Load(N_House) ]

    Ranges:
        U_ac   ∈ [-1.0, 1.0]
        Gamma  ∈ [-1.52, 1.0]
        E_Load ∈ [0.0, 1.0]
    """
    n_u_ac   = N_House
    n_gamma  = N_PV_Bat + N_Bat
    n_eload  = N_House

    dim = n_u_ac + n_gamma + n_eload

    low = np.empty(dim, dtype=np.float32)
    high = np.empty(dim, dtype=np.float32)

    # U_ac: [-1, 1]
    low[0:n_u_ac] = -1.0
    high[0:n_u_ac] = 1.0

    # Gamma: [-1.52, 1]
    start = n_u_ac
    stop = start + n_gamma
    low[start:stop] = -1.52
    high[start:stop] = 1.0

    # E_Load: [0, 1]
    start = stop
    stop = start + n_eload
    low[start:stop] = 0.0
    high[start:stop] = 1.0

    return spaces.Box(low=low, high=high, dtype=np.float32)

# -------------------- Observation Generator -------------------- #

def MultiHouse_OffGrid_RL_Observation_Generator_Function(SmartComSim_Object):

    env = SmartComSim_Object
    
    # =================================================================================
    # =================================================================================
    # INTIIAL DATA GATHERING 
    # =================================================================================
    # =================================================================================

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)    

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_rl_inputs(
        ctx      = ctx,
        E_PV     = E_PV
    )    

    # =================================================================================
    # Use reshape to construct Observation for ON/OFF Grid
    # =================================================================================

    # Off-Grid
    Observation = Exp_SingleMultiHouse_OffGrid_observation_creator(ctx, reshaped, RL_Parameters)

    # On-Grid
    # Observation = Exp_SingleMultiHouse_OnGrid_observation_creator(ctx, reshaped, RL_Parameters)

    return Observation

# -------------------- Action Generator -------------------- #

def MultiHouse_OffGrid_RL_Action_Generator_Function(SmartComSim_Object, Action):

    env = SmartComSim_Object

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)    

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_rl_inputs(
        ctx      = ctx,
        E_PV     = E_PV
    )   

    # =================================================================================
    # Get Action_Dict from Action
    # ================================================================================= 

    Action_Dict = Exp_SingleMultiHouse_OffGrid_parse_action(Action, env)

    # Action_Dict = Exp_SingleMultiHouse_OnGrid_parse_action(Action, env)

    # =================================================================================
    # Use reshape/Action_Dict to construct Observation for ON/OFF Grid
    # =================================================================================

    # Off-Grid
    action = Exp_SingleMultiHouse_OffGrid_action_creator(Action_Dict, ctx, reshaped, RL_Parameters)

    # On-Grid
    # action = Exp_SingleMultiHouse_OnGrid_action_creator(Action_Dict, ctx, reshaped, RL_Parameters)


    return action

# -------------------- Reward -------------------- #

def MultiHouse_OffGrid_RL_Reward_Function(SmartComSim_Object, observation_k_1, action_k_0, observation_k_0):

    env = SmartComSim_Object

    # =================================================================================
    # Build unified RL context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters) 

    N_House                 = int(ctx["N_House"])
    N_PV_Bat                = int(ctx["N_PV_Bat"])
    N_Bat                   = int(ctx["N_Bat"])
    N_PV                    = int(ctx["N_PV"])
    N_None                  = int(ctx["N_None"])

    T_h_Max                 = ctx["T_h_Max"]
    T_h_Min                 = ctx["T_h_Min"]
    E_AC                    = ctx["E_AC"]
    P_ac_st                 = ctx["ACLoad_StartUp_Power"]
    Eff_Inv                 = ctx["Eff_Inv"]
    E_bat_Max               = ctx["E_bat_Max"]
    E_bat_Min               = ctx["E_bat_Min"]
    Gamma_Charging          = ctx["Gamma_Charging"]
    Gamma_Discharging       = ctx["Gamma_Discharging"]
    P_bat                   = ctx["P_bat"]

    # Additional variable requested
    E_l_max                 = ctx["E_l_max"]

    E_AC                    = E_AC / Eff_Inv 

    Simulation_StepSize = env.simulation_params["Simulation_StepSize"]

    # =============================================================================
    # Extract Reward Weights from RL_Parameters
    # =============================================================================

    # Off-grid weight dictionary (returns {} if missing)
    W_off = RL_Parameters.get("OFFGRID_WEIGHTS", {})    

    W_T_h     = W_off.get("W_T_h",     0.0)
    W_Ebat    = W_off.get("W_Ebat",    0.0)
    W_Ebal    = W_off.get("W_Ebal",    0.0)
    W_startup = W_off.get("W_startup", 0.0)
    W_surplus = W_off.get("W_surplus", 0.0)
    W_load    = W_off.get("W_load",    0.0)
    W_mode    = W_off.get("W_mode",    0.0)

    # =================================================================================
    # Parse observation_k_1
    # =================================================================================

    o_k_1_Dict = Exp_SingleMultiHouse_OffGrid_parse_observation(observation_k_1, env, RL_Parameters)

    Th_now_1      = o_k_1_Dict["Th"]            # shape: (N_House,)
    E_Bat_now_1   = o_k_1_Dict["E_Bat"]         # shape: (N_PV_Bat+N_Bat,)
    U_ac_prev_1   = o_k_1_Dict["U_ac_prev"]     # shape: (N_House,)
    E_l_now_1     = o_k_1_Dict["E_l_now"]       # shape: (N_House,)
    E_cri_now_1   = o_k_1_Dict["E_cri_now"]     # shape: (N_House,)
    E_PV_now_1    = o_k_1_Dict["E_PV_now"]      # shape: (1,)
    T_am_now_1    = o_k_1_Dict["T_am_now"]      # shape: (1,)

    # =================================================================================
    # Parse action_k_0
    # =================================================================================

    a_k_0_Dict = Exp_SingleMultiHouse_OffGrid_parse_action(action_k_0, env)

    U_ac_0   = a_k_0_Dict["U_ac"]      # shape: (N_House,)
    Gamma_0  = a_k_0_Dict["Gamma"]     # shape: (N_PV_Bat + N_Bat,)
    E_Load_0 = a_k_0_Dict["E_Load"]    # shape: (N_House,)

    U_ac_0 = (np.abs(U_ac_0) > 0.5).astype(int)
    U_ac_h = (U_ac_0 >= 0).astype(int)
    E_Load_0 = E_Load_0 * E_l_max

    # =================================================================================
    # Parse observation_k_0
    # =================================================================================

    o_k_0_Dict = Exp_SingleMultiHouse_OffGrid_parse_observation(observation_k_0, env, RL_Parameters)

    Th_now_0      = o_k_0_Dict["Th"]            # shape: (N_House,)
    E_Bat_now_0   = o_k_0_Dict["E_Bat"]         # shape: (N_PV_Bat+N_Bat,)
    U_ac_prev_0   = o_k_0_Dict["U_ac_prev"]     # shape: (N_House,)
    E_l_now_0     = o_k_0_Dict["E_l_now"]       # shape: (N_House,)
    E_cri_now_0   = o_k_0_Dict["E_cri_now"]     # shape: (N_House,)
    E_PV_now_0    = o_k_0_Dict["E_PV_now"]      # shape: (1,)
    T_am_now_0    = o_k_0_Dict["T_am_now"]      # shape: (1,)

    # =================================================================================
    # Reward Computation
    # =================================================================================

    # =================================================================================
    # Reward Computation: Thermal Comfort (T_h_Reward) - CUMULATIVE over houses
    # =================================================================================

    # Th_now_1: shape (N_House,)
    # T_h_Min, T_h_Max: scalar or array-like (broadcastable to (N_House,))

    # 1) Temperature violations
    violation_cold = np.maximum(T_h_Min - Th_now_1, 0.0)   # too cold
    violation_hot  = np.maximum(Th_now_1 - T_h_Max, 0.0)   # too hot

    temp_violation = violation_cold + violation_hot        # shape: (N_House,)

    # 2) Per-house reward:
    #    - inside band: temp_violation = 0  → reward = +1
    #    - outside band: reward = 1 - (distance outside band)
    T_h_reward_per_house = 1.0 - temp_violation            # shape: (N_House,)

    # 3) Cumulative reward over all houses
    T_h_Reward = float(np.sum(T_h_reward_per_house))       # scalar

    # =================================================================================
    # Reward Computation: Battery SOC (E_bat_Reward) - CUMULATIVE over batteries
    # =================================================================================

    # E_Bat_now_1: shape (N_PV_Bat + N_Bat,)
    # E_bat_Min, E_bat_Max from ctx (broadcastable)

    # 1) Define safe region
    safe_min = 0.05 * (E_bat_Max)    # 5% above minimum SOC
    safe_max = E_bat_Max           # maximum SOC allowed

    # 2) Violations
    violation_low  = np.maximum(safe_min - E_Bat_now_1, 0.0)   # below safe min
    #violation_high = np.maximum(E_Bat_now_1 - safe_max, 0.0)   # above max

    total_violation = violation_low #+ violation_high           # shape: (Nbatt,)

    # 3) Per-battery reward
    #    inside band → violation = 0 → reward = +1
    #    outside band → reward = 1 - violation magnitude
    Ebat_reward_per_battery = 1.0 - total_violation

    # 4) Cumulative reward over all batteries
    Ebat_Reward = float(np.sum(Ebat_reward_per_battery))

    # ---------------------------------------------------------------------------------
    # Reward: Energy Balance
    # ---------------------------------------------------------------------------------

    # U_ac_0: (N_House,)   already binarized {0,1}
    # E_AC:   scalar or (N_House,)   per-house AC energy per step
    # E_Load_0: (N_House,)  already scaled by E_l_max

    E_ac_total   = float(np.sum(U_ac_0 * E_AC))   # total AC energy demand
    E_load_total = float(np.sum(E_Load_0))        # total flexible load demand

    Demand_total = E_ac_total + E_load_total      # scalar

    # E_PV_now_0: shape (1,) or scalar-like
    # Gamma_0:    shape (N_PV_Bat + N_Bat,)
    # P_bat:      scalar or (N_PV_Bat + N_Bat,)  -> per-step energy capacity

    E_pv_total = float(np.sum(E_PV_now_0)) * (N_PV_Bat + N_PV)

    # Per-step battery energy term (c,dc) – using P_bat as the base magnitude
    E_bat_step = Gamma_Discharging * Simulation_StepSize                           # broadcasts as needed
    E_bat_contrib_total = float(np.sum(Gamma_0 * E_bat_step))

    Generation_total = E_pv_total + E_bat_contrib_total

    energy_deficit = max(Demand_total - Generation_total, 0.0)  # scalar ≥ 0

    Ebal_Reward = 1.0 - energy_deficit

    # ------------------------------------------------------------------------------
    # Reward: AC startup power feasibility (R_startup)
    # ------------------------------------------------------------------------------

    # U_ac_prev_0: shape (N_House,), previous AC command/state from o_k_0
    # U_ac_0:      shape (N_House,), current AC action after binarization {0,1}

    # f_on_0 = 1 where AC was OFF and now is ON (startup event)
    f_on_0 = ((U_ac_prev_0 <= 1) & (U_ac_0 >= 1)).astype(float)  # shape: (N_House,)

    # θ_bat = 1 if Gamma > 0 (discharging), else 0
    theta_bat_0 = (Gamma_0 > 0).astype(float)     # shape: (N_PV_Bat + N_Bat,)

    # P_ac_st: from ctx["ACLoad_StartUp_Power"] (scalar or (N_House,))
    # theta_bat_0: e.g.,
    # theta_bat_0 = a_k_0_Dict["theta_bat"]     # shape: (N_PV_Bat + N_Bat,)
    # P_bat: from ctx["P_bat"] (scalar or per-battery)
    # E_PV_now_0: shape (1,) or scalar-like
    # Delta_Ts: sampling period (from ctx or RL_Parameters)
    Delta_Ts = Simulation_StepSize   # make sure this exists in your ctx

    # Total startup power demand [kW]
    P_startup_total = float(np.sum(f_on_0 * P_ac_st))

    # Available battery discharge power [kW]
    P_bat_avail = float(np.sum(theta_bat_0 * P_bat))

    # PV power [kW] approximated from energy over step
    P_pv_avail = float(np.sum(E_PV_now_0)) * (N_PV_Bat + N_PV) / float(Delta_Ts)

    # Total available fast power
    P_avail_total = P_bat_avail + P_pv_avail

    # Power deficit (positive = not enough power, negative/zero = OK)
    P_deficit = P_startup_total - P_avail_total

    if np.sum(f_on_0) > 0:
        # There is at least one AC starting
        if P_deficit <= 0.0:
            R_startup = 1.0
        else:
            R_startup = 1.0 - P_deficit
    else:
        # No startup event: neutral contribution
        R_startup = 0.0

    # --------------------------------------------------------------
    # Surplus-waste penalty: separate reward term (scaled)
    # --------------------------------------------------------------

    raw_diff       = Demand_total - Generation_total    # +deficit, -surplus
    energy_surplus = max(-raw_diff, 0.0)                # surplus (>= 0)

    # Battery charging status
    is_charging_array = (Gamma_0 < 0.0)                 # True where charging
    num_charging      = int(np.sum(is_charging_array))
    num_batteries     = len(Gamma_0)
    num_not_charging  = num_batteries - num_charging

    # Condition:
    # Penalize if surplus exists AND at least one battery is NOT charging
    if energy_surplus > 0.0 and num_charging < num_batteries:
        # scaled penalty
        R_surplus = - energy_surplus * num_not_charging
    else:
        # Either no surplus, or ALL batteries are charging
        R_surplus = 0.0

    # --------------------------------------------------------------
    # Flexible load / critical load reward (IF–ELSE version)
    # --------------------------------------------------------------

    R_load_per_house = np.zeros(N_House, dtype=float)

    for i in range(N_House):

        Eload = float(E_Load_0[i])        # served (action)
        El    = float(E_l_now_0[i])       # requested
        Ecri  = float(E_cri_now_0[i])     # critical demand

        # Safety: no negative served load
        if Eload < 0:
            Eload = 0.0

        # ----------------------------------------------------------
        # CASE 0: No flexible load requested
        # ----------------------------------------------------------
        if El <= 0.0:

            if Eload > 0.0:
                # Penalty for serving load when none is asked for
                R_load_per_house[i] = - Eload
            else:
                # No load asked and none served -> neutral
                R_load_per_house[i] = 0.0

            continue  # Skip rest of cases for this house

        # ----------------------------------------------------------
        # CASE A: Fully served or overserved
        # ----------------------------------------------------------
        if Eload >= El:
            R_load_per_house[i] = 1.0

        # ----------------------------------------------------------
        # CASE B: Between critical and full demand
        #          reward = Eload / El
        # ----------------------------------------------------------
        elif (Eload >= Ecri) and (Eload < El):
            R_load_per_house[i] = Eload / El

        # ----------------------------------------------------------
        # CASE C: Below critical load
        #          heavy penalty = -100 * (Ecri - Eload)
        # ----------------------------------------------------------
        else:   # Eload < Ecri
            R_load_per_house[i] = -100.0 * (Ecri - Eload)

    # Sum across houses
    R_load = float(np.sum(R_load_per_house))

    # --------------------------------------------------------------
    # Heating/Cooling mode correctness reward (R_mode)
    # --------------------------------------------------------------

    R_mode_per_house = np.zeros(N_House, dtype=float)

    T_am = float(T_am_now_0)   # scalar from observation

    for i in range(N_House):

        Th   = float(Th_now_0[i])            # indoor temperature
        mode = int(U_ac_h[i])                # 1 = heating, 0 = cooling

        deltaT = abs(T_am - Th)

        # ----------------------------------------------------------
        # CASE 1: Ambient hotter than indoor (T_am > T_h)
        # ----------------------------------------------------------
        if T_am > Th:

            if mode == 1:
                # Heating when indoor < outdoor -> WRONG
                R_mode_per_house[i] = -deltaT
            else:
                # Cooling when indoor < outdoor -> CORRECT
                R_mode_per_house[i] = 1.0

        # ----------------------------------------------------------
        # CASE 2: Ambient colder than indoor (T_am < T_h)
        # ----------------------------------------------------------
        elif T_am < Th:

            if mode == 0:
                # Cooling when indoor > outdoor -> WRONG
                R_mode_per_house[i] = -deltaT
            else:
                # Heating when indoor > outdoor -> CORRECT
                R_mode_per_house[i] = 1.0

        # ----------------------------------------------------------
        # CASE 3: Ambient == indoor (rare) -> Neutral
        # ----------------------------------------------------------
        else:
            R_mode_per_house[i] = 0.0

    # Cumulative reward
    R_mode = float(np.sum(R_mode_per_house))

    Reward = (
        T_h_Reward      +    # thermal comfort
        Ebat_Reward     +    # battery SOC
        Ebal_Reward     +    # energy balance
        R_startup       +    # AC startup feasibility
        R_surplus       +    # surplus waste penalty
        R_load          +    # flexible vs critical load performance
        R_mode               # heating/cooling correctness
    )  


    return Reward

# -------------------- Terminate -------------------- #

def MultiHouse_OffGrid_RL_Terminate_Function(SmartComSim_Object):

    """
    Natural (MDP) termination for smart community RL.
    Uses ONLY ctx (no external inputs).

    Episode TERMINATES if:
      1) ALL house temperatures fall outside the allowed band:
            T_set ± 5°C
         (either all too cold or all too hot)
      OR
      2) ALL batteries (if present) have energy in the low band:
            [E_bat_min, E_bat_min + 0.05*(E_bat_max - E_bat_min)]
    """

    env = SmartComSim_Object

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)      

    # ------------------------------------------------------------
    # 1. TEMPERATURE-BASED TERMINATION
    # ------------------------------------------------------------

    # Current temps (stored inside ctx)
    T_h = np.array(ctx["T_h_Init"])   # shape (N_House,)

    # Setpoint = midpoint of min & max
    T_set = 0.5 * (ctx["T_h_Min"] + ctx["T_h_Max"])

    # Band = setpoint ± 5°C
    band = 5.0
    T_low_band = T_set - band
    T_high_band = T_set + band

    # Check:
    too_cold_all = np.all(T_h < T_low_band)
    too_hot_all  = np.all(T_h > T_high_band)

    thermal_failure = bool(too_cold_all or too_hot_all)

    # ------------------------------------------------------------
    # 2. BATTERY-BASED TERMINATION
    # ------------------------------------------------------------

    N_total_bats = ctx["N_PV_Bat"] + ctx["N_Bat"]

    if N_total_bats > 0:
        # Current E_bat from ctx
        E_bat = np.array(ctx["E_bat_Init"])  # shape (N_total_bats,)

        # Band width = 5% of usable range
        E_min = ctx["E_bat_Min"]
        E_max = ctx["E_bat_Max"]
        low_band_width = 0.0005 * (E_max - E_min)

        low_band_lower = E_min
        low_band_upper = E_min + low_band_width

        bat_low_all = np.all(
            (E_bat >= low_band_lower) & (E_bat <= low_band_upper)
        )

        battery_failure = bool(bat_low_all)

    else:
        battery_failure = False

    # ------------------------------------------------------------
    # 3. COMBINE CONDITIONS
    # ------------------------------------------------------------
    Terminate = thermal_failure or battery_failure

    return Terminate

# -------------------- Truncate -------------------- #

def MultiHouse_OffGrid_RL_Truncate_Function(SmartComSim_Object):

    """
    Determine whether the episode should end because we are too close 
    to the end of the dataset to provide the required future horizon.
    
    NOTE:
    -----
    This is an ARTIFICIAL end (dataset boundary), so in Gymnasium/SB3
    this must be mapped to:
        terminated = False
        truncated  = True
    even though internally we return `Terminate = True` here.
    
    Parameters
    ----------
    env : SmartComSim_Object
        The active simulation environment instance.
    
    RL_Parameters : dict
        Contains RL settings, specifically:
            RL_HORIZON_N : int
                Number of future steps required to construct the state.
    
    Returns
    -------
    bool
        True  -> We must end this episode (dataset boundary reached).
        False -> Episode can continue normally.
    """

    env = SmartComSim_Object

    # Total number of steps available in the full dataset (e.g., 1 year)
    total_steps = env.Simulation_Steps_Total

    # To construct a future-horizon state at time t, we need:
    #     t + RL_HORIZON_N < total_steps
    # This means the RL agent can only operate safely until:
    max_safe_step = total_steps - RL_Parameters["RL_HORIZON_N"]

    # Current timestep in the environment
    current_step = env.time_iter

    # If we exceed or reach the data boundary threshold,
    # we cannot supply future horizon data -> must end episode.
    if current_step >= max_safe_step - 1:
        Terminate = True   # Artificial termination → will map to truncated
    else:
        Terminate = False

    return Terminate

#-------------------------------------------------------------------------------------------------------------#
# Multi House On-Grid RL
#-------------------------------------------------------------------------------------------------------------#

# -------------------- Observation Space -------------------- #

def MultiHouse_OnGrid_RL_ObservationSpace_Function(SmartComSim_Object):
    # Build Short Context from Env
    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House      = int(ctx["N_House"])
    N_PV_Bat     = int(ctx["N_PV_Bat"])
    N_Bat        = int(ctx["N_Bat"])
    N_PV         = int(ctx["N_PV"])
    N_None       = int(ctx["N_None"])

    # Get desired RL_Parameters
    RL_HORIZON_N = int(RL_Parameters["RL_HORIZON_N"])
    RL_HORIZON_AVG_N = int(RL_Parameters["RL_HORIZON_AVG_N"])

    """
    ON-GRID State:
        [ Th(N_House),
          E_Bat(N_PV_Bat + N_Bat),
          E_l_now(N_House),
          E_PV_now(1),
          T_am_now(1),
          E_Price_now(1),
          E_l_future(H_factor * N_House),
          E_PV_future(H_factor),
          T_am_future(H_factor),
          E_price_future(H_factor) ]
    where H_factor = RL_HORIZON_N / RL_HORIZON_AVG_N
    """

    if RL_HORIZON_AVG_N <= 0:
        raise ValueError("RL_HORIZON_AVG_N must be > 0")

    H_factor = RL_HORIZON_N // RL_HORIZON_AVG_N

    dim = (
        N_House +                     # Th(N_House)
        (N_PV_Bat + N_Bat) +          # E_Bat(N_PV_Bat + N_Bat)
        N_House +                     # E_l_now(N_House)
        1 +                           # E_PV_now(1)
        1 +                           # T_am_now(1)
        1 +                           # E_Price_now(1)
        H_factor * N_House +          # E_l_future(H_factor * N_House)
        H_factor +                    # E_PV_future(H_factor)
        H_factor +                    # T_am_future(H_factor)
        H_factor                      # E_price_future(H_factor)
    )

    low = -np.inf * np.ones(dim, dtype=np.float32)
    high =  np.inf * np.ones(dim, dtype=np.float32)
    
    return spaces.Box(low=low, high=high, dtype=np.float32)

# -------------------- Action Space -------------------- #

def MultiHouse_OnGrid_RL_ActionSpace_Function(SmartComSim_Object):

    # Build Short Context from Env
    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House      = int(ctx["N_House"])
    N_PV_Bat     = int(ctx["N_PV_Bat"])
    N_Bat        = int(ctx["N_Bat"])
    N_PV         = int(ctx["N_PV"])
    N_None       = int(ctx["N_None"])

    # OFF-GRID Action: [U_ac(N_House), Gamma(N_PV_Bat + N_Bat), E_Load(N_House)] 

    # On-GRID Action: [U_ac(N_House), Gamma(N_PV_Bat + N_Bat), u_pv(N_PV_Bat+N_PV)]

    # For U_ac -> [-1,1] {negative will mean cooling and non-negative will mean heating}
    # For Gamma -> [-1.52, 1]
    # For E_Load -> [0,1]
    # For u_pv -> [0,1]

    """
    ON-GRID Action:
        [ U_ac(N_House),
          Gamma(N_PV_Bat + N_Bat),
          u_pv(N_PV_Bat + N_PV) ]

    Ranges:
        U_ac ∈ [-1.0, 1.0]
        Gamma ∈ [-1.52, 1.0]
        u_pv ∈ [0.0, 1.0]
    """
    n_u_ac  = N_House
    n_gamma = N_PV_Bat + N_Bat
    n_upv   = N_PV_Bat + N_PV

    dim = n_u_ac + n_gamma + n_upv

    low = np.empty(dim, dtype=np.float32)
    high = np.empty(dim, dtype=np.float32)

    # U_ac: [-1, 1]
    low[0:n_u_ac] = -1.0
    high[0:n_u_ac] = 1.0

    # Gamma: [-1.52, 1]
    start = n_u_ac
    stop = start + n_gamma
    low[start:stop] = -1.52
    high[start:stop] = 1.0

    # u_pv: [0, 1]
    start = stop
    stop = start + n_upv
    low[start:stop] = 0.0
    high[start:stop] = 1.0

    return spaces.Box(low=low, high=high, dtype=np.float32)

# -------------------- Observation Generator -------------------- #

def MultiHouse_OnGrid_RL_Observation_Generator_Function(SmartComSim_Object):

    env = SmartComSim_Object
    
    # =================================================================================
    # =================================================================================
    # INTIIAL DATA GATHERING 
    # =================================================================================
    # =================================================================================

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)    

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_rl_inputs(
        ctx      = ctx,
        E_PV     = E_PV
    )    

    # =================================================================================
    # Use reshape to construct Observation for ON/OFF Grid
    # =================================================================================

    # Off-Grid
    # Observation = Exp_SingleMultiHouse_OffGrid_observation_creator(ctx, reshaped, RL_Parameters)

    # On-Grid
    Observation = Exp_SingleMultiHouse_OnGrid_observation_creator(ctx, reshaped, RL_Parameters)

    return Observation

# -------------------- Action Generator -------------------- #

def MultiHouse_OnGrid_RL_Action_Generator_Function(SmartComSim_Object, Action):

    env = SmartComSim_Object

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)    

    # =================================================================================
    # Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
    # =================================================================================

    E_PV = compute_singlehouse_E_PV_from_ctx(ctx)

    # =================================================================================
    # Reshape & sanitize all disturbances and initial conditions (MATLAB block)
    # =================================================================================

    reshaped = reshape_and_sanitize_Community_rl_inputs(
        ctx      = ctx,
        E_PV     = E_PV
    )   

    # =================================================================================
    # Get Action_Dict from Action
    # ================================================================================= 

    # Action_Dict = Exp_SingleMultiHouse_OffGrid_parse_action(Action, env)

    Action_Dict = Exp_SingleMultiHouse_OnGrid_parse_action(Action, env)

    # =================================================================================
    # Use reshape/Action_Dict to construct Observation for ON/OFF Grid
    # =================================================================================

    # Off-Grid
    # action = Exp_SingleMultiHouse_OffGrid_action_creator(Action_Dict, ctx, reshaped, RL_Parameters)

    # On-Grid
    action = Exp_SingleMultiHouse_OnGrid_action_creator(Action_Dict, ctx, reshaped, RL_Parameters)


    return action

# -------------------- Reward -------------------- #

def MultiHouse_OnGrid_RL_Reward_Function(SmartComSim_Object, observation_k_1, action_k_0, observation_k_0):

    env = SmartComSim_Object

    # =================================================================================
    # Build unified RL context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters) 

    N_House                 = int(ctx["N_House"])
    N_PV_Bat                = int(ctx["N_PV_Bat"])
    N_Bat                   = int(ctx["N_Bat"])
    N_PV                    = int(ctx["N_PV"])
    N_None                  = int(ctx["N_None"])

    T_h_Max                 = ctx["T_h_Max"]
    T_h_Min                 = ctx["T_h_Min"]
    E_AC                    = ctx["E_AC"]
    P_ac_st                 = ctx["ACLoad_StartUp_Power"]
    Eff_Inv                 = ctx["Eff_Inv"]
    E_bat_Max               = ctx["E_bat_Max"]
    E_bat_Min               = ctx["E_bat_Min"]
    Gamma_Charging          = ctx["Gamma_Charging"]
    Gamma_Discharging       = ctx["Gamma_Discharging"]
    P_bat                   = ctx["P_bat"]

    # Additional variable requested
    E_l_max                 = ctx["E_l_max"]

    E_AC                    = E_AC / Eff_Inv 

    Simulation_StepSize = env.simulation_params["Simulation_StepSize"]

    # =============================================================================
    # Extract Reward Weights from RL_Parameters
    # =============================================================================

    # On-grid weight dictionary (returns {} if missing)
    W_on  = RL_Parameters.get("ONGRID_WEIGHTS", {})
    
    W_T_h     = W_on.get("W_T_h",     0.0)
    W_Ebat    = W_on.get("W_Ebat",    0.0)
    W_cost    = W_on.get("W_cost",    0.0)
    W_PV      = W_on.get("W_PV",      0.0)
    W_u_pv    = W_on.get("W_u_pv",    0.0)
    W_mode    = W_on.get("W_mode",    0.0)

    # =================================================================================
    # Parse observation_k_1
    # =================================================================================

    o_k_1_Dict = Exp_SingleMultiHouse_OffGrid_parse_observation(observation_k_1, env, RL_Parameters)

    Th_now_1      = o_k_1_Dict["Th"]            # shape: (N_House,)
    E_Bat_now_1   = o_k_1_Dict["E_Bat"]         # shape: (N_PV_Bat+N_Bat,)
    E_l_now_1     = o_k_1_Dict["E_l_now"]       # shape: (N_House,)
    E_Price_now_1   = o_k_1_Dict["E_Price_now"] # shape: (1,)
    E_PV_now_1    = o_k_1_Dict["E_PV_now"]      # shape: (1,)
    T_am_now_1    = o_k_1_Dict["T_am_now"]      # shape: (1,)

    # =================================================================================
    # Parse action_k_0
    # =================================================================================

    a_k_0_Dict = Exp_SingleMultiHouse_OffGrid_parse_action(action_k_0, env)

    U_ac_0   = a_k_0_Dict["U_ac"]      # shape: (N_House,)
    Gamma_0  = a_k_0_Dict["Gamma"]     # shape: (N_PV_Bat + N_Bat,)
    U_pv_0   = a_k_0_Dict["u_pv"]      # shape: (N_PV_Bat + N_PV,)

    U_ac_0 = (np.abs(U_ac_0) > 0.5).astype(int)
    U_ac_h = (U_ac_0 >= 0).astype(int)

    # =================================================================================
    # Parse observation_k_0
    # =================================================================================

    o_k_0_Dict = Exp_SingleMultiHouse_OffGrid_parse_observation(observation_k_0, env, RL_Parameters)

    Th_now_0      = o_k_0_Dict["Th"]            # shape: (N_House,)
    E_Bat_now_0   = o_k_0_Dict["E_Bat"]         # shape: (N_PV_Bat+N_Bat,)
    E_l_now_0     = o_k_0_Dict["E_l_now"]       # shape: (N_House,)
    E_Price_now_0 = o_k_0_Dict["E_Price_now"]   # shape: (1,)
    E_PV_now_0    = o_k_0_Dict["E_PV_now"]      # shape: (1,)
    T_am_now_0    = o_k_0_Dict["T_am_now"]      # shape: (1,)

    # =================================================================================
    # Reward Computation
    # =================================================================================

    # =================================================================================
    # Reward Computation: Thermal Comfort (T_h_Reward) - CUMULATIVE over houses
    # =================================================================================

    # Th_now_1: shape (N_House,)
    # T_h_Min, T_h_Max: scalar or array-like (broadcastable to (N_House,))

    # 1) Temperature violations
    violation_cold = np.maximum(T_h_Min - Th_now_1, 0.0)   # too cold
    violation_hot  = np.maximum(Th_now_1 - T_h_Max, 0.0)   # too hot

    temp_violation = violation_cold + violation_hot        # shape: (N_House,)

    # 2) Per-house reward:
    #    - inside band: temp_violation = 0  → reward = +1
    #    - outside band: reward = 1 - (distance outside band)
    T_h_reward_per_house = 1.0 - temp_violation            # shape: (N_House,)

    # 3) Cumulative reward over all houses
    T_h_Reward = float(np.sum(T_h_reward_per_house))       # scalar

    # =================================================================================
    # Reward Computation: Battery SOC (E_bat_Reward) - CUMULATIVE over batteries
    # =================================================================================

    # E_Bat_now_1: shape (N_PV_Bat + N_Bat,)
    # E_bat_Min, E_bat_Max from ctx (broadcastable)

    # 1) Define safe region
    safe_min = 0.05 * (E_bat_Max)    # 5% above minimum SOC
    safe_max = E_bat_Max           # maximum SOC allowed

    # 2) Violations
    violation_low  = np.maximum(safe_min - E_Bat_now_1, 0.0)   # below safe min
    #violation_high = np.maximum(E_Bat_now_1 - safe_max, 0.0)   # above max

    total_violation = violation_low #+ violation_high           # shape: (Nbatt,)

    # 3) Per-battery reward
    #    inside band → violation = 0 → reward = +1
    #    outside band → reward = 1 - violation magnitude
    Ebat_reward_per_battery = 1.0 - total_violation

    # 4) Cumulative reward over all batteries
    Ebat_Reward = float(np.sum(Ebat_reward_per_battery))     

    # --------------------------------------------------------------
    # Heating/Cooling mode correctness reward (R_mode)
    # --------------------------------------------------------------

    R_mode_per_house = np.zeros(N_House, dtype=float)

    T_am = float(T_am_now_0)   # scalar from observation

    for i in range(N_House):

        Th   = float(Th_now_0[i])            # indoor temperature
        mode = int(U_ac_h[i])                # 1 = heating, 0 = cooling

        deltaT = abs(T_am - Th)

        # ----------------------------------------------------------
        # CASE 1: Ambient hotter than indoor (T_am > T_h)
        # ----------------------------------------------------------
        if T_am > Th:

            if mode == 1:
                # Heating when indoor < outdoor -> WRONG
                R_mode_per_house[i] = -deltaT
            else:
                # Cooling when indoor < outdoor -> CORRECT
                R_mode_per_house[i] = 1.0

        # ----------------------------------------------------------
        # CASE 2: Ambient colder than indoor (T_am < T_h)
        # ----------------------------------------------------------
        elif T_am < Th:

            if mode == 0:
                # Cooling when indoor > outdoor -> WRONG
                R_mode_per_house[i] = -deltaT
            else:
                # Heating when indoor > outdoor -> CORRECT
                R_mode_per_house[i] = 1.0

        # ----------------------------------------------------------
        # CASE 3: Ambient == indoor (rare) -> Neutral
        # ----------------------------------------------------------
        else:
            R_mode_per_house[i] = 0.0

    # Cumulative reward
    R_mode = float(np.sum(R_mode_per_house))

    # =================================================================================
    # 1) Common energy terms (On-Grid)
    # =================================================================================

    # Total AC energy demand (kWh in this step)
    E_ac_total = float(np.sum(U_ac_0 * E_AC))

    # Total inflexible load demand (kWh) from observation
    E_load_total = float(np.sum(E_l_now_0))

    # Battery discharge energy (kWh) this step
    Gamma_discharge = np.maximum(Gamma_0, 0.0)   # only discharging contributes
    E_bat_dis_total = float(np.sum(Gamma_discharge * Gamma_Discharging * Simulation_StepSize ))

    # PV energy available this step (kWh)
    E_pv_avail = float(np.sum(E_PV_now_0)) * (N_PV_Bat + N_PV)

    # Effective PV utilization factor from u_pv (clip to [0,1])
    if E_pv_avail > 0.0:
        # assume U_pv_0 in [-1,1] or [0,1], we only care about "using" PV (>=0)
        u_pv_eff = float(np.clip(np.mean(np.maximum(U_pv_0, 0.0)), 0.0, 1.0))
    else:
        u_pv_eff = 0.0

    # PV actually used (kWh)
    E_pv_used = u_pv_eff * E_pv_avail

    # Grid import (kWh): what’s left after PV + battery discharge
    Demand_total     = E_ac_total + E_load_total
    Supply_local     = E_pv_used + E_bat_dis_total
    E_grid_import    = Demand_total - Supply_local

    # =================================================================================
    # 2) R_cost  – minimize grid energy cost
    # =================================================================================

    price = float(E_Price_now_0)   # scalar price for this step

    Step_Cost = price * E_grid_import    # [$/step] or arbitrary unit
    R_cost = -Step_Cost                  # reward is negative cost

    # =================================================================================
    # 3) R_PV – penalize PV curtailment (maximize utilization)
    # =================================================================================

    E_pv_curt = max(E_pv_avail - E_pv_used, 0.0)   # kWh curtailed

    # Simple choice: linear penalty with curtailment
    R_PV = -E_pv_curt

    # =================================================================================
    # 4) R_u_pv – penalize u_pv > 0 when E_pv == 0
    # =================================================================================

    if E_pv_avail <= 0.0:
        # Any positive PV utilization command when there is no PV?
        u_pv_pos = np.maximum(U_pv_0, 0.0)
        if np.any(u_pv_pos > 0.0):
            # penalty proportional to "how much" PV is being commanded
            R_u_pv = -np.sum(u_pv_pos)
        else:
            R_u_pv = 0.0
    else:
        # PV available, no penalty here
        R_u_pv = 0.0

    Reward = (
        W_T_h  * T_h_Reward   +   # from off-grid design
        W_Ebat * Ebat_Reward  +   # from off-grid design
        W_mode * R_mode       +   # from off-grid design
        W_cost * R_cost       +   # new on-grid term
        W_PV   * R_PV         +   # new on-grid term
        W_u_pv * R_u_pv           # new on-grid term
    )  


    return Reward

# -------------------- Terminate -------------------- #

def MultiHouse_OnGrid_RL_Terminate_Function(SmartComSim_Object):

    """
    Natural (MDP) termination for smart community RL.
    Uses ONLY ctx (no external inputs).

    Episode TERMINATES if:
      1) ALL house temperatures fall outside the allowed band:
            T_set ± 5°C
         (either all too cold or all too hot)
      OR
      2) ALL batteries (if present) have energy in the low band:
            [E_bat_min, E_bat_min + 0.05*(E_bat_max - E_bat_min)]
    """

    env = SmartComSim_Object

    # =================================================================================
    # Build unified MPC context (equivalent to MATLAB "From ... Params" block)
    # =================================================================================

    ctx = build_Community_rl_context(env, RL_Parameters)      

    # ------------------------------------------------------------
    # 1. TEMPERATURE-BASED TERMINATION
    # ------------------------------------------------------------

    # Current temps (stored inside ctx)
    T_h = np.array(ctx["T_h_Init"])   # shape (N_House,)

    # Setpoint = midpoint of min & max
    T_set = 0.5 * (ctx["T_h_Min"] + ctx["T_h_Max"])

    # Band = setpoint ± 5°C
    band = 5.0
    T_low_band = T_set - band
    T_high_band = T_set + band

    # Check:
    too_cold_all = np.all(T_h < T_low_band)
    too_hot_all  = np.all(T_h > T_high_band)

    thermal_failure = bool(too_cold_all or too_hot_all)

    # ------------------------------------------------------------
    # 2. BATTERY-BASED TERMINATION
    # ------------------------------------------------------------

    N_total_bats = ctx["N_PV_Bat"] + ctx["N_Bat"]

    if N_total_bats > 0:
        # Current E_bat from ctx
        E_bat = np.array(ctx["E_bat_Init"])  # shape (N_total_bats,)

        # Band width = 5% of usable range
        E_min = ctx["E_bat_Min"]
        E_max = ctx["E_bat_Max"]
        low_band_width = 0.0005 * (E_max - E_min)

        low_band_lower = E_min
        low_band_upper = E_min + low_band_width

        bat_low_all = np.all(
            (E_bat >= low_band_lower) & (E_bat <= low_band_upper)
        )

        battery_failure = bool(bat_low_all)

    else:
        battery_failure = False

    # ------------------------------------------------------------
    # 3. COMBINE CONDITIONS
    # ------------------------------------------------------------
    Terminate = thermal_failure or battery_failure

    return Terminate

# -------------------- Truncate -------------------- #

def MultiHouse_OnGrid_RL_Truncate_Function(SmartComSim_Object):

    """
    Determine whether the episode should end because we are too close 
    to the end of the dataset to provide the required future horizon.
    
    NOTE:
    -----
    This is an ARTIFICIAL end (dataset boundary), so in Gymnasium/SB3
    this must be mapped to:
        terminated = False
        truncated  = True
    even though internally we return `Terminate = True` here.
    
    Parameters
    ----------
    env : SmartComSim_Object
        The active simulation environment instance.
    
    RL_Parameters : dict
        Contains RL settings, specifically:
            RL_HORIZON_N : int
                Number of future steps required to construct the state.
    
    Returns
    -------
    bool
        True  -> We must end this episode (dataset boundary reached).
        False -> Episode can continue normally.
    """

    env = SmartComSim_Object

    # Total number of steps available in the full dataset (e.g., 1 year)
    total_steps = env.Simulation_Steps_Total

    # To construct a future-horizon state at time t, we need:
    #     t + RL_HORIZON_N < total_steps
    # This means the RL agent can only operate safely until:
    max_safe_step = total_steps - RL_Parameters["RL_HORIZON_N"]

    # Current timestep in the environment
    current_step = env.time_iter

    # If we exceed or reach the data boundary threshold,
    # we cannot supply future horizon data -> must end episode.
    if current_step >= max_safe_step - 1:
        Terminate = True   # Artificial termination → will map to truncated
    else:
        Terminate = False

    return Terminate