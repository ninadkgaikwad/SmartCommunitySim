###############################################################################################################
## Import Desired Packages
###############################################################################################################

import sys
import os

import time
import numpy as np
import pandas as pd

from math import exp
from scipy.linalg import expm

import torch
import torch.nn as nn

from stable_baselines3 import SAC
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.utils import set_random_seed

###############################################################################################################
## Import Custom Packages
###############################################################################################################

# Adding paths to find local modules
paths_to_add = [
    r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Modules",
    r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code",
]

for p in paths_to_add:
    if p not in sys.path and os.path.isdir(p):
        sys.path.append(p)

from Exp_Config_Module import *

from SmartComSim import SmartCommunity_Simulator as SC_Plant

###############################################################################################################
## Experiment MPC RL Controllers Helper Module - Common Custom Functions
###############################################################################################################

###############################################################################################################
## RL CONFIGURATION - CONSTANTS 
###############################################################################################################

# -------------------- RL Setup - Configured in Exp_Config_Module-------------------- #

# RL_Parameters = Exp_RL_Configuration_Generator()

# =====================================================================================
# Helper 1: Community sizes from env.Community_Params
# =====================================================================================

def _get_community_sizes(env):
    cp = env.Community_Params
    N_House  = int(cp["N_House"])
    N_PV_Bat = int(cp["N_PV_Bat"])
    N_Bat    = int(cp["N_Bat"])
    N_PV     = int(cp["N_PV"])
    N_None   = int(cp["N_None"])
    return N_House, N_PV_Bat, N_Bat, N_PV, N_None


# =====================================================================================
# Helper 2: Initial states from env.X_k_Plant
# =====================================================================================

def _get_initial_states(env, N_PV_Bat, N_Bat):
    """
    Extracts initial temperatures, battery SOCs, and previous AC commands
    from env.X_k_Plant (matlab.double -> numpy array).
    Mirrors the MATLAB indices:
        T_h_Init     = X_k_Plant(1,7,:)
        T_wall_Init  = X_k_Plant(1,8,:)
        T_attic_Init = X_k_Plant(1,9,:)
        T_im_Init    = X_k_Plant(1,10,:)
        E_bat_Init   = X_k_Plant(1,4,1:N_PV_Bat+N_Bat)
        U_ac_Init    = X_k_Plant(1,30,:)
    """
    X_k_Plant_np = np.array(env.X_k_Plant)  # shape approx (1, 39, N_House)

    # Reshape for single house for consistency
    if (len(X_k_Plant_np.shape) == 2):

        X_k_Plant_np = np.reshape(X_k_Plant_np, (X_k_Plant_np.shape[0], X_k_Plant_np.shape[1], 1))

    T_h_Init     = X_k_Plant_np[0, 6, :]    # (1,7,:) -> [0,6,:]
    T_wall_Init  = X_k_Plant_np[0, 7, :]
    T_attic_Init = X_k_Plant_np[0, 8, :]
    T_im_Init    = X_k_Plant_np[0, 9, :]

    # Battery states only for houses with battery
    E_bat_Init = X_k_Plant_np[0, 3, : (N_PV_Bat + N_Bat)]

    # Previous AC action
    U_ac_Init = X_k_Plant_np[0, 29, :]      # (1,30,:) -> [0,29,:]

    return {
        "T_h_Init": T_h_Init,
        "T_wall_Init": T_wall_Init,
        "T_attic_Init": T_attic_Init,
        "T_im_Init": T_im_Init,
        "E_bat_Init": E_bat_Init,
        "U_ac_Init": U_ac_Init,
    }


# =====================================================================================
# Helper 3: Build MPC horizon disturbances (W_k_MPC equivalent)
# =====================================================================================

def _build_mpc_horizon_slices(env, MPC_Parameters):
    """
    Builds the MPC horizon window for weather + load disturbances, mimicking W_k_MPC:
        E_l, E_l_Array, Ws, T_am, GHI, DNI
    plus Initial_DecisionVariables from MPC_Parameters.
    """
    N_horizon = int(MPC_Parameters["N_horizon"])
    t0 = int(env.time_iter)
    t1 = t0 + N_horizon

    # Full-series weather arrays
    Ws_full   = np.array(env.Ws)
    T_am_full = np.array(env.T_am)
    GHI_full  = np.array(env.GHI)
    DNI_full  = np.array(env.DNI)
    DateTime_Matrix_full = np.array(env.DateTime_Matrix)

    # Full-series load arrays
    E_LoadData_full      = np.array(env.E_LoadData)
    E_Load_Desired_Array = np.array(env.E_Load_Desired)

    # Reshape for single house for consistency
    if (len(E_LoadData_full.shape) == 2):

        E_LoadData_full = np.reshape(E_LoadData_full, (E_LoadData_full.shape[0], E_LoadData_full.shape[1], 1))

    # Slice along time: [t0, t1)
    Ws   = Ws_full[t0:t1, 0]
    T_am = T_am_full[t0:t1, 0]
    GHI  = GHI_full[t0:t1, 0]
    DNI  = DNI_full[t0:t1, 0]
    DateTime_Matrix = DateTime_Matrix_full[t0:t1, :]

    # For loads: E_l = desired, E_l_Array = full data
    E_l       = E_Load_Desired_Array[t0:t1, :]   # (N, N_House)
    E_l_Array = E_LoadData_full[t0:t1, :, :]     # (N, load_types(3:11), N_House)

    # Get E_l_Max for RL Action Normalization
    # E_l_Max = E_Load_Desired_Array.max()

    # For Energy_Price
    Energy_Price_full   = np.array(env.Energy_Price)
    Energy_Price = Energy_Price_full[t0:t1, 4]

    

    return {
        "E_l": E_l,
        # "E_l_Max": E_l_Max,
        "E_l_Array": E_l_Array,
        "Ws": Ws,
        "T_am": T_am,
        "GHI": GHI,
        "DNI": DNI,
        "DateTime_Matrix": DateTime_Matrix,
        "Energy_Price": Energy_Price,
    }


# =====================================================================================
# Helper 4: Plant and house parameters from env
# =====================================================================================

def _get_plant_and_house_params(env):
    HEMSPlant_Params = env.HEMSPlant_Params
    HEMSHouse_Params = env.HEMSHouse_Params

    plant = {
        "T_h_Max": HEMSPlant_Params["T_AC_max"],
        "T_h_Min": HEMSPlant_Params["T_AC_min"],
        "Q_AC": HEMSPlant_Params["ACLoad_Power"],
        "E_AC": HEMSPlant_Params["E_AC"],
        "ACLoad_StartUp_Power": HEMSPlant_Params["ACLoad_StartUp_Power"],
        "Eff_Inv": HEMSPlant_Params["Eff_Inv"],
        "E_bat_Max": HEMSPlant_Params["Battery_Energy_Max"],
        "E_bat_Min": HEMSPlant_Params["Battery_Energy_Min"],
        "Gamma_Charging": HEMSPlant_Params["MaxRate_Charging"],
        "Gamma_Discharging": HEMSPlant_Params["MaxRate_Discharging"],
        "P_bat": HEMSPlant_Params["MaxRate_Discharging_StartUp"],
    }

    house = {
        "Q_ac": HEMSHouse_Params["Q_ac"],
    }

    return plant, house

# =====================================================================================
# Helper 6: Simulation step
# =====================================================================================

def _get_sim_step(env):
    return env.simulation_params["Simulation_StepSize"]

# =====================================================================================
# Generate PV energy profile over MPC horizon (Python version of HEMS_PVEnergy_Available_Generator)
# =====================================================================================

def compute_singlehouse_E_PV_from_ctx(ctx):
    """
    Compute E_PV over the MPC horizon using already-sliced
    Ws, T_am, GHI from the MPC context `ctx`.

    This is the Python equivalent of:

        [E_PV] = HEMS_PVEnergy_Available_Generator(PVEnergy_Generator_Input);
        E_PV   = E_PV';  % column vector

    Returns
    -------
    E_PV : np.ndarray
        1D array of PV energy [kWh] over the MPC horizon.
    """

    ############################# Helpers ##############################
    
    def _to_1d_np(x):
        """Ensure x is a 1D numpy array (handles matlab.double, lists, etc.)."""
        return np.array(x).flatten()

    def _s(val):
        # unwrap matlab.double([[x]]) etc. to scalar
        arr = np.array(val).flatten()
        return float(arr[0])
    
    # ------------------------------------------------------------------
    # 1) Weather series over the MPC horizon (already sliced in ctx)
    # ------------------------------------------------------------------
    Ws  = _to_1d_np(ctx["Ws"])
    T_am = _to_1d_np(ctx["T_am"])
    GHI  = _to_1d_np(ctx["GHI"])
    # DNI is in ctx["DNI"] if needed later, but not used in this model

    # All of these should have the same length = horizon length
    assert len(Ws) == len(T_am) == len(GHI), "Weather arrays must match in length"

    # Simulation step (hours)
    dt = float(ctx["Simulation_StepSize"])   # Simulation_StepSize in hours

    # ------------------------------------------------------------------
    # 2) PV parameters: you can either
    #    (a) store them directly in ctx, or
    #    (b) pull them from ctx["HEMSPlant_Params"] (MATLAB struct)
    # ------------------------------------------------------------------
    H = ctx["HEMSPlant_Params"]  # MATLAB-style struct proxied into Python

    

    PV_TotalModules_Num = _s(H["PV_TotlaModules_Num"])
    PV_RatedPower       = _s(H["PV_RatedPower"])
    PV_TempCoeff        = _s(H["PV_TempCoeff"])

    Uo       = _s(H["Uo"])
    U1       = _s(H["U1"])
    Temp_Std = _s(H["Temp_Std"])
    GHI_Std  = _s(H["GHI_Std"])

    # ------------------------------------------------------------------
    # 3) Faiman module temperature model
    #
    #   Tm(k) = T_am(k) + GHI(k) / (Uo + U1 * Ws(k))
    # ------------------------------------------------------------------
    Tm = T_am + (GHI / (Uo + U1 * Ws))

    # ------------------------------------------------------------------
    # 4) PV energy per step (vectorized) – same formula as MATLAB
    #
    #   PV_Total_Power = PV_TotalModules_Num * PV_RatedPower;
    #
    #   PVEnergy_Available(ii) =
    #       PV_Total_Power *
    #       (1 + (PV_TempCoeff/100) * (Tm(ii) - Temp_Std)) *
    #       (GHI(ii) / GHI_Std) *
    #       Simulation_StepSize / 1000;
    #
    # Units: if PV_Total_Power is W and dt is hours, /1000 gives kWh.
    # ------------------------------------------------------------------
    PV_Total_Power = PV_TotalModules_Num * PV_RatedPower

    E_PV = (
        PV_Total_Power
        * (1.0 + (PV_TempCoeff / 100.0) * (Tm - Temp_Std))
        * (GHI / GHI_Std)
        * dt
        / 1000.0
    )  # shape: (N_horizon,)

    # store in ctx for the CasADi model if useful
    # ctx["E_PV"] = E_PV
    # ctx["N_Horizon"] = len(E_PV)

    return E_PV

###############################################################################################################
## Experiment MPC RL Controllers Helper Module - MPC Specific Custom Functions
###############################################################################################################

# =====================================================================================
# Helper 5: MPC tuning (Lambda’s etc.) from MPC_Parameters
# =====================================================================================

def _get_mpc_tuning(MPC_Parameters):
    tuning = {
        "N_horizon": int(MPC_Parameters["N_horizon"]),
        "MPC_StepLengthUsed": int(MPC_Parameters["MPC_StepLengthUsed"]),
        "MPC_DecisionVariables_Num": int(MPC_Parameters["DecisionVariables_PerHouse"]),
        "Initial_DecisionVariables": MPC_Parameters.get("Initial_DecisionVariables", None),
        "Lambda_T": MPC_Parameters["Lambda_T"],
        "Lambda_Bat": MPC_Parameters["Lambda_Bat"],
        "Lambda_Theta": MPC_Parameters["Lambda_Theta"],
        "Lambda_E_l": MPC_Parameters["Lambda_E_l"],
        "Lambda_E_cri": MPC_Parameters["Lambda_E_cri"],
        "Lambda_G": MPC_Parameters["Lambda_G"],
        "Lambda_PV": MPC_Parameters["Lambda_PV"],
        "Epsilon": MPC_Parameters["Epsilon"],
        "OpenLoop_Plotting_Indicator": MPC_Parameters["OpenLoop_Plotting_Indicator"],
    }
    return tuning


# =====================================================================================
# High-level context builder: bundles all of the above into one dict
# =====================================================================================

def build_Community_mpc_context(env, MPC_Parameters):
    """
    Builds a context dict containing everything the controller needs for
    the MPC formulation, mirroring the MATLAB 'parameter unpacking' block.
    """
    # Community
    N_House, N_PV_Bat, N_Bat, N_PV, N_None = _get_community_sizes(env)

    # Initial states
    init = _get_initial_states(env, N_PV_Bat, N_Bat)

    # Horizon disturbances
    wmpc = _build_mpc_horizon_slices(env, MPC_Parameters)

    # Plant & house params
    plant, house = _get_plant_and_house_params(env)

    # MPC tuning
    tuning = _get_mpc_tuning(MPC_Parameters)

    # Simulation step
    sim_step = _get_sim_step(env)

    

    # Bundle everything into a single context dict
    ctx = {
        "N_House": N_House,
        "N_PV_Bat": N_PV_Bat,
        "N_Bat": N_Bat,
        "N_PV": N_PV,
        "N_None": N_None,

        # Initial states
        **init,

        # Disturbances / W_k_MPC-like
        **wmpc,

        # Plant / house params
        "plant": plant,
        "house": house,

        # Individual plant scalars (for convenience)
        "T_h_Max": plant["T_h_Max"],
        "T_h_Min": plant["T_h_Min"],
        "Q_AC": plant["Q_AC"],
        "E_AC": plant["E_AC"],
        "ACLoad_StartUp_Power": plant["ACLoad_StartUp_Power"],
        "Eff_Inv": plant["Eff_Inv"],
        "E_bat_Max": plant["E_bat_Max"],
        "E_bat_Min": plant["E_bat_Min"],
        "Gamma_Charging": plant["Gamma_Charging"],
        "Gamma_Discharging": plant["Gamma_Discharging"],
        "P_bat": plant["P_bat"],

        "Q_ac": house["Q_ac"],

        # MPC tuning
        **tuning,

        # Simulation dt
        "Simulation_StepSize": sim_step,
    }

    # ---------------------------------------------------------------
    # Plant-level parameters (include these now!)
    # ---------------------------------------------------------------
    ctx["HEMSPlant_Params"] = env.HEMSPlant_Params
    ctx["HEMSHouse_Params"] = env.HEMSHouse_Params
    ctx["Simulation_Params"] = env.simulation_params

    return ctx



# =====================================================================================
# Generate House RC Data and Disturbances - Helpers
# =====================================================================================

def _ViewFactor(beta, phi, tilt, phic):
    """
    Python translation of MATLAB:
        CosInciAngle =
            cos(beta)*cos(phi - phic)*sin(tilt)
          + sin(beta)*cos(tilt)

    All angles are in **degrees**, matching the MATLAB implementation.

    Parameters
    ----------
    beta : float
        Solar elevation angle (deg)
    phi : float
        Solar azimuth angle (deg)
    tilt : float
        Surface tilt angle (deg)
    phic : float
        Surface azimuth orientation angle (deg)

    Returns
    -------
    CosInciAngle : float
        Value of cos(incidence angle)
    """

    beta_rad = np.deg2rad(beta)
    phi_rad = np.deg2rad(phi)
    tilt_rad = np.deg2rad(tilt)
    phic_rad = np.deg2rad(phic)

    CosInciAngle = (
        np.cos(beta_rad) * np.cos(phi_rad - phic_rad) * np.sin(tilt_rad)
        + np.sin(beta_rad) * np.cos(tilt_rad)
    )

    return CosInciAngle

def _LeapYearFinder(year):
    """
    Python equivalent of MATLAB LeapYearFinder.
    
    Returns
    -------
    1 if leap year
    0 if not leap year
    """
    year = int(year)

    # Gregorian leap year rule
    if (year % 4) != 0:
        return 0
    elif (year % 100) != 0:
        return 1
    elif (year % 400) != 0:
        return 0
    else:
        return 1


def _JulianDay(day, month, year):
    """
    Python translation of MATLAB function:
        [n] = JulianDay(Day, Month, Year)

    Computes day-of-year index (1–365 or 1–366).
    Matches your exact month-start tables for leap / non-leap.

    Parameters
    ----------
    day   : int
    month : int
    year  : int

    Returns
    -------
    n : int
        Julian day number (1–365/366)
    """

    leap = _LeapYearFinder(year)

    # Month start tables match EXACT MATLAB logic
    if leap == 0:
        # Non-leap year
        month_start = {
            1:   1,
            2:   32,
            3:   60,
            4:   91,
            5:   121,
            6:   152,
            7:   182,
            8:   213,
            9:   244,
            10:  274,
            11:  305,
            12:  335,
        }
    else:
        # Leap year
        month_start = {
            1:   1,
            2:   32,
            3:   61,
            4:   92,
            5:   122,
            6:   153,
            7:   183,
            8:   214,
            9:   245,
            10:  275,
            11:  306,
            12:  336,
        }

    # MATLAB: n = StartMonthStartDay + Day - 1
    n = month_start[int(month)] + int(day) - 1

    return n

def _HourAngle(Hp):
    """
    Python translation of MATLAB:
        H(i,j) = 15 * (12 - Hp(1,j))

    Parameters
    ----------
    Hp : float or array_like
        Solar time(s) in decimal hours. 
        Can be scalar or array.

    Returns
    -------
    H : np.ndarray
        Hour angle(s) in degrees.
    """

    Hp = np.asarray(Hp, dtype=float)

    # MATLAB formula: H = 15 * (12 - Hp)
    H = 15.0 * (12.0 - Hp)

    return H

def _Declination(n):
    """
    Python translation of MATLAB:
        dec = 23.45 * sin((360/365)*(n - 81)*(pi/180))

    Parameters
    ----------
    n : float, int, or array_like
        Julian day (1–365). Scalar or array.

    Returns
    -------
    dec : np.ndarray
        Solar declination angle in degrees.
    """

    n = np.asarray(n, dtype=float)

    dec = 23.45 * np.sin(np.deg2rad((360.0 / 365.0) * (n - 81.0)))

    return dec

def _ClockToSolarTime(n, hem, Ltm, L, CT_array):
    """
    Python translation of:
        [ST, B, E] = ClockToSolarTime(n, hem, Ltm, L, CT)

    Parameters
    ----------
    n : float or int
        Julian day (scalar). In your usage this is typically a single value.
    hem : float or int
        Hemisphere sign: -1 for West (e.g., Long < 0), +1 for East.
    Ltm : float
        Local time meridian (deg).
    L : float
        Longitude (deg, positive).
    CT_array : array_like
        Clock time(s) in decimal hours. Can be a 1D list/array.

    Returns
    -------
    ST_array : np.ndarray
        Solar time(s) in decimal hours, same shape as CT_array.
    B : float
        Intermediate angle B in degrees.
    E : float
        Equation of Time in minutes (same units as MATLAB).
    """

    # Ensure CT is a numpy array
    CT_array = np.asarray(CT_array, dtype=float)

    # ---- Equation of time pieces (match MATLAB) ----
    # B = (360/364)*(n - 81)   [deg]
    B = (360.0 / 364.0) * (float(n) - 81.0)

    # E in minutes
    B_rad = np.deg2rad(B)
    E = (
        9.87 * np.sin(2.0 * B_rad)
        - 7.53 * np.cos(B_rad)
        - 1.5 * np.sin(B_rad)
    )

    # ---- Solar time ST ----
    # ST = CT - (hem*(Ltm - L)*4)/60 + E/60
    #   (4 minutes per degree; divide by 60 to convert to hours)
    ST_array = (
        CT_array
        - (hem * (Ltm - L) * 4.0) / 60.0
        + E / 60.0
    )

    return ST_array, B, E

def _AltiAzi(dec_deg, L_deg, H_deg_array):
    """
    Python translation of the MATLAB AltiAzi(dec, L, H) function.

    Parameters
    ----------
    dec_deg : float
        Solar declination in degrees.
    L_deg : float
        Latitude in degrees.
    H_deg_array : array_like
        Hour angle(s) in degrees. Can be 1D array/list.

    Returns
    -------
    beta_deg : np.ndarray
        Solar elevation angle(s) in degrees. Shape = (len(H_deg_array),).
    phi_deg : np.ndarray
        Solar azimuth angle(s) in degrees. Shape = (len(H_deg_array),).

    Notes
    -----
    This follows the exact logic of the MATLAB code:

        beta(j) = asin( cos(L)*cos(dec)*cos(H_j) + sin(L)*sin(dec) )
        azi1(j) = asin( cos(dec)*sin(H_j) / cos(beta(j)) )

        if cos(H_j) >= tan(dec)/tan(L):
            phi(j) = azi1(j)
        else
            if azi1(j) >= 0
                phi(j) = azi2(j) = 180 - |azi1(j)|
            else
                phi(j) = -azi2(j) = -(180 - |azi1(j)|)
    """

    # Ensure numpy array
    H_deg_array = np.asarray(H_deg_array, dtype=float)

    # Convert constants to radians
    dec_rad = np.deg2rad(dec_deg)
    L_rad   = np.deg2rad(L_deg)

    # Prepare outputs
    beta_deg = np.zeros_like(H_deg_array, dtype=float)
    phi_deg  = np.zeros_like(H_deg_array, dtype=float)

    """ for j in range(len(H_deg_array)):
        H_deg = H_deg_array[j]
        H_rad = np.deg2rad(H_deg)

        # --- Elevation angle beta ---
        # beta = asin( cos(L)*cos(dec)*cos(H) + sin(L)*sin(dec) )
        arg_beta = (
            np.cos(L_rad) * np.cos(dec_rad) * np.cos(H_rad)
            + np.sin(L_rad) * np.sin(dec_rad)
        )
        # numerical safety
        arg_beta = np.clip(arg_beta, -1.0, 1.0)
        beta_rad = np.arcsin(arg_beta)
        beta_deg[j] = np.rad2deg(beta_rad)

        # --- Intermediate azimuth azi1 ---
        # azi1 = asin( cos(dec)*sin(H) / cos(beta) )
        cos_beta = np.cos(beta_rad)
        if np.isclose(cos_beta, 0.0):
            # Degenerate case, just set azi1 = 0
            azi1_rad = 0.0
        else:
            arg_azi1 = (np.cos(dec_rad) * np.sin(H_rad)) / cos_beta
            arg_azi1 = np.clip(arg_azi1, -1.0, 1.0)
            azi1_rad = np.arcsin(arg_azi1)

        azi1_deg = np.rad2deg(azi1_rad)

        # MATLAB creates azi2 = 180 - |azi1|
        azi2_deg = 180.0 - abs(azi1_deg)

        # --- Quadrant corrections ---
        x = np.cos(H_rad)
        # y = tan(dec)/tan(L)
        if np.isclose(np.cos(L_rad), 0.0):
            # pathological latitude; just avoid division by zero
            y = np.inf
        else:
            y = np.tan(dec_rad) / np.tan(L_rad)

        if x >= y:
            # Region 1
            phi_deg[j] = azi1_deg
        else:
            # Region 2/3 depending on sign of azi1
            if azi1_deg >= 0:
                phi_deg[j] = azi2_deg
            else:
                phi_deg[j] = -azi2_deg """    
    
    H_deg = H_deg_array
    H_rad = np.deg2rad(H_deg)

    # --- Elevation angle beta ---
    # beta = asin( cos(L)*cos(dec)*cos(H) + sin(L)*sin(dec) )
    arg_beta = (
        np.cos(L_rad) * np.cos(dec_rad) * np.cos(H_rad)
        + np.sin(L_rad) * np.sin(dec_rad)
    )
    # numerical safety
    arg_beta = np.clip(arg_beta, -1.0, 1.0)
    beta_rad = np.arcsin(arg_beta)
    beta_deg = np.rad2deg(beta_rad)

    # --- Intermediate azimuth azi1 ---
    # azi1 = asin( cos(dec)*sin(H) / cos(beta) )
    cos_beta = np.cos(beta_rad)
    if np.isclose(cos_beta, 0.0):
        # Degenerate case, just set azi1 = 0
        azi1_rad = 0.0
    else:
        arg_azi1 = (np.cos(dec_rad) * np.sin(H_rad)) / cos_beta
        arg_azi1 = np.clip(arg_azi1, -1.0, 1.0)
        azi1_rad = np.arcsin(arg_azi1)

    azi1_deg = np.rad2deg(azi1_rad)

    # MATLAB creates azi2 = 180 - |azi1|
    azi2_deg = 180.0 - abs(azi1_deg)

    # --- Quadrant corrections ---
    x = np.cos(H_rad)
    # y = tan(dec)/tan(L)
    if np.isclose(np.cos(L_rad), 0.0):
        # pathological latitude; just avoid division by zero
        y = np.inf
    else:
        y = np.tan(dec_rad) / np.tan(L_rad)

    if x >= y:
        # Region 1
        phi_deg = azi1_deg
    else:
        # Region 2/3 depending on sign of azi1
        if azi1_deg >= 0:
            phi_deg = azi2_deg
        else:
            phi_deg = -azi2_deg

    return beta_deg, phi_deg

# =====================================================================================
# Generate House RC Data and Disturbances - Main
# =====================================================================================

def compute_singlehouse_RC_data_from_ctx(ctx):
    """
    Python analogue of HEMS_HouseRCModel_MPC_Data_Generator.

    Uses:
      - HEMSHouse_Input      = ctx["HEMSHouse_Params"]
      - HEMSPlant_Params     = ctx["HEMSPlant_Params"]
      - Simulation_Params    = ctx["Simulation_Params"]
      - Weather over horizon = ctx["Ws"], ctx["T_am"], ctx["DNI"], ctx["DateTime_Matrix"]

    Returns:
      dict with keys:
        Q_venti_Const, Q_infil_Const, Q_ihl,
        T_sol_w, T_sol_r, Q_solar,  # length = N_horizon
        A_T_h, B_T_h                # 4x4, 4x8 matrices (discrete time)
    """

    # -------------------------------------------------------------------------
    # 0) Small helpers for matlab.double / list conversion
    # -------------------------------------------------------------------------
    def _to_scalar(x):
        # Handles matlab.double([[val]]), [ [val] ], plain float
        if isinstance(x, (list, tuple)):
            # peel nested lists until scalar-ish
            while isinstance(x, (list, tuple)) and len(x) == 1:
                x = x[0]
        return float(x)

    def _to_array(x):
        # matlab.double -> nested lists; just np.array
        return np.asarray(x, dtype=float)

    # -------------------------------------------------------------------------
    # 1) Extract from ctx
    # -------------------------------------------------------------------------
    HEMSHouse_Input   = ctx["HEMSHouse_Params"]
    HEMSPlant_Params  = ctx["HEMSPlant_Params"]
    Simulation_Params = ctx["Simulation_Params"]

    Ws              = _to_array(ctx["Ws"])
    T_am            = _to_array(ctx["T_am"])
    DNI             = _to_array(ctx["DNI"])
    DateTime_Matrix = _to_array(ctx["DateTime_Matrix"])

    # We only care about as many steps as in the horizon (N_horizon)
    N_horizon = len(Ws)

    # -------------------------------------------------------------------------
    # 2) Extract HEMSHouse_Input fields (as in MATLAB)
    # -------------------------------------------------------------------------
    R_w     = _to_scalar(HEMSHouse_Input["R_w"])
    R_attic = _to_scalar(HEMSHouse_Input["R_attic"])
    R_roof  = _to_scalar(HEMSHouse_Input["R_roof"])
    R_im    = _to_scalar(HEMSHouse_Input["R_im"])
    R_win   = _to_scalar(HEMSHouse_Input["R_win"])

    C_w     = _to_scalar(HEMSHouse_Input["C_w"])
    C_attic = _to_scalar(HEMSHouse_Input["C_attic"])
    C_im    = _to_scalar(HEMSHouse_Input["C_im"])
    C_in    = _to_scalar(HEMSHouse_Input["C_in"])

    C1      = _to_scalar(HEMSHouse_Input["C1"])
    C2      = _to_scalar(HEMSHouse_Input["C2"])
    C3      = _to_scalar(HEMSHouse_Input["C3"])

    Human_Num      = _to_scalar(HEMSHouse_Input["Human_Num"])
    Human_Heat     = _to_scalar(HEMSHouse_Input["Human_Heat"])
    Appliance_Heat = _to_scalar(HEMSHouse_Input["Appliance_Heat"])

    Cp      = _to_scalar(HEMSHouse_Input["Cp"])
    V       = _to_scalar(HEMSHouse_Input["V"])
    Den_Air = _to_scalar(HEMSHouse_Input["Den_Air"])
    C_oew   = _to_scalar(HEMSHouse_Input["C_oew"])

    SHGC    = _to_scalar(HEMSHouse_Input["SHGC"])
    Alpha_w = _to_scalar(HEMSHouse_Input["Alpha_w"])
    Alpha_r = _to_scalar(HEMSHouse_Input["Alpha_r"])

    Area_w   = _to_array(HEMSHouse_Input["Area_w"])
    Tilt_w   = _to_array(HEMSHouse_Input["Tilt_w"])
    Azi_w    = _to_array(HEMSHouse_Input["Azi_w"])

    Area_r   = _to_array(HEMSHouse_Input["Area_r"])
    Tilt_r   = _to_array(HEMSHouse_Input["Tilt_r"])
    Azi_r    = _to_array(HEMSHouse_Input["Azi_r"])

    Area_win = _to_array(HEMSHouse_Input["Area_win"])
    Tilt_win = _to_array(HEMSHouse_Input["Tilt_win"])
    Azi_win  = _to_array(HEMSHouse_Input["Azi_win"])

    # -------------------------------------------------------------------------
    # 3) Extract Simulation and Plant params
    # -------------------------------------------------------------------------
    # StepSize is in seconds in your MATLAB code
    StepSize = _to_scalar(Simulation_Params["StepSize"])

    hem  = _to_scalar(HEMSPlant_Params["hem"])
    Lat  = _to_scalar(HEMSPlant_Params["Lat"])
    Long = _to_scalar(HEMSPlant_Params["Long"])
    Ltm  = _to_scalar(HEMSPlant_Params["Ltm"])

    # -------------------------------------------------------------------------
    # 4) Basic computations
    # -------------------------------------------------------------------------
    WeatherData_Length = len(Ws)

    # Internal gains
    Q_ihl = Human_Num * Human_Heat + Appliance_Heat

    # Ventilation / infiltration constants
    Q_venti_Const = Cp * V * Den_Air
    Q_infil_Const = Cp * C_oew

    # Allocate arrays
    F_w   = np.zeros(WeatherData_Length)
    F_r   = np.zeros(WeatherData_Length)
    F_win = np.zeros(WeatherData_Length)
    h_c   = np.zeros(WeatherData_Length)
    Q_solar = np.zeros(WeatherData_Length)
    T_sol_w = np.zeros(WeatherData_Length)
    T_sol_r = np.zeros(WeatherData_Length)

    # -------------------------------------------------------------------------
    # 5) Solar geometry & gains (structure matches MATLAB)
    #    The helper functions called here (JulianDay, Declination, etc.)
    #    are assumed to be defined elsewhere in Python.
    # -------------------------------------------------------------------------
    for ii in range(WeatherData_Length):

        Day   = DateTime_Matrix[ii, 0]
        Month = DateTime_Matrix[ii, 1]
        Year  = DateTime_Matrix[ii, 2]
        Time  = DateTime_Matrix[ii, 3]

        # --- Solar geometry ---
        n   = _JulianDay(Day, Month, Year)              # TODO: provide Python implementation
        dec = _Declination(n)                           # TODO
        ST, _, _  = _ClockToSolarTime(n, hem, Ltm, Long, Time)  # TODO

        # Correction for ST
        if ST < 0:
            ST = ST + 24.0
        elif ST >= 24.0:
            ST = ST - 24.0

        Ha      = _HourAngle(ST)                        # TODO
        beta, phi = _AltiAzi(dec, Lat, Ha)              # TODO

        # --- View factors: Wall ---
        Fw_sum = 0.0
        for jj in range(Area_w.size):
            VF = _ViewFactor(beta, phi, Tilt_w[0,jj], Azi_w[0,jj])  # TODO
            if (VF < 0.0) or (beta < 0.0):
                VF = 0.0
            Fw_sum += Area_w[0,jj] * VF
        if np.sum(Area_w) > 0:
            F_w[ii] = Fw_sum / np.sum(Area_w)
        else:
            F_w[ii] = 0.0

        # --- View factors: Roof ---
        Fr_sum = 0.0
        for jj in range(Area_r.size):
            VF = _ViewFactor(beta, phi, Tilt_r, Azi_r)  # TODO
            if (VF < 0.0) or (beta < 0.0):
                VF = 0.0
            Fr_sum += Area_r * VF
        if np.sum(Area_r) > 0:
            F_r[ii] = Fr_sum / np.sum(Area_r)
        else:
            F_r[ii] = 0.0

        # --- View factors: Window ---
        Fwin_sum = 0.0
        for jj in range(Area_win.size):
            VF = _ViewFactor(beta, phi, Tilt_win[0,jj], Azi_win[0,jj])  # TODO
            if (VF < 0.0) or (beta < 0.0):
                VF = 0.0
            Fwin_sum += Area_win[0,jj] * VF
        if np.sum(Area_win) > 0:
            F_win[ii] = Fwin_sum / np.sum(Area_win)
        else:
            F_win[ii] = 0.0

        # Convective heat transfer coefficient
        h_c[ii] = 11.4 + 5.7 * Ws[ii]

        # Solar gains through windows
        Q_solar[ii] = F_win[ii] * DNI[ii] * np.sum(Area_win) * SHGC

        # Effective solar temperatures for wall/roof
        if h_c[ii] != 0.0:
            T_sol_w[ii] = (Alpha_w / h_c[ii]) * F_w[ii] * DNI[ii] + T_am[ii]
            T_sol_r[ii] = (Alpha_r / h_c[ii]) * F_r[ii] * DNI[ii] + T_am[ii]
        else:
            # Degenerate case; fall back to ambient
            T_sol_w[ii] = T_am[ii]
            T_sol_r[ii] = T_am[ii]

    # Trim to horizon if WeatherData_Length > N_horizon
    T_sol_w = T_sol_w[:N_horizon]
    T_sol_r = T_sol_r[:N_horizon]
    Q_solar = Q_solar[:N_horizon]

    # -------------------------------------------------------------------------
    # 6) Continuous-time state-space (Ac, Bc)
    # -------------------------------------------------------------------------
    R_2 = -(R_attic * R_im * R_win) \
          - ((R_w / 2.0) * R_im * R_win) \
          - ((R_w / 2.0) * R_attic * R_win) \
          - ((R_w / 2.0) * R_attic * R_im)

    R_1 = R_attic * R_im * R_win * (R_w / 2.0)

    Ac = np.array([
        [(-4.0 / (C_w * R_w)),        (2.0 / (C_w * R_w)),                                0.0,                                   0.0],
        [(2.0 / (C_in * R_w)),        (R_2 / (C_in * R_1)),                     (1.0 / (C_in * R_attic)),            (1.0 / (C_in * R_im))],
        [0.0,                         (1.0 / (C_attic * R_attic)), ((-R_attic - R_roof) / (C_attic * R_roof * R_attic)),      0.0],
        [0.0,                         (1.0 / (C_im * R_im)),                                0.0,                         (-1.0 / (C_im * R_im))]
    ], dtype=float)

    Bc = np.array([
        [0.0,                      (1.0 / (C_w * (R_w / 2.0))),          0.0,                      0.0,          0.0,          0.0,          0.0,       0.0],
        [(1.0 / (C_in * R_win)),   0.0,                                   0.0,                     C1 / C_in,    C2 / C_in,    (1.0 / C_in), (1.0 / C_in), 0.0],
        [0.0,                      0.0,                                   (1.0 / (C_attic * R_roof)), 0.0,        0.0,          0.0,          0.0,       0.0],
        [0.0,                      0.0,                                   0.0,                      0.0,          0.0,          0.0,          0.0,       C3 / C_im]
    ], dtype=float)

    # -------------------------------------------------------------------------
    # 7) Discretization: A = expm(Ac*StepSize), B = Ac^{-1}(expm(Ac*StepSize)-I)Bc
    # -------------------------------------------------------------------------
    if expm is not None:
        A_disc = expm(Ac * StepSize)
        try:
            A_minus_I = A_disc - np.eye(4)
            B_disc = np.linalg.solve(Ac, A_minus_I).dot(Bc)
        except np.linalg.LinAlgError:
            # fallback: simple Euler in pathological cases
            A_disc = np.eye(4) + Ac * StepSize
            B_disc = Bc * StepSize
    else:
        # No SciPy: forward Euler
        A_disc = np.eye(4) + Ac * StepSize
        B_disc = Bc * StepSize

    A_T_h = A_disc
    B_T_h = B_disc

    # -------------------------------------------------------------------------
    # 8) Pack output (MPC data struct)
    # -------------------------------------------------------------------------
    RC_Data = {
        "Q_venti_Const": Q_venti_Const,
        "Q_infil_Const": Q_infil_Const,
        "Q_ihl": Q_ihl,
        "T_sol_w": T_sol_w,
        "T_sol_r": T_sol_r,
        "Q_solar": Q_solar,
        "A_T_h": A_T_h,
        "B_T_h": B_T_h,
    }

    return RC_Data

# =====================================================================================
# Reshaping MPC Data for Arbitrary Community MPC - Main
# =====================================================================================

def reshape_and_sanitize_Community_mpc_inputs(
    ctx,
    E_PV,
    T_sol_w,
    T_sol_r,
    Q_solar,
):
    """
    Reshape initial states & disturbances and correct boundary violations
    for the Single-House Off-Grid MPC, mirroring the MATLAB block:

        - Reshapes:
            T_h_Init, T_wall_Init, T_attic_Init, T_im_Init
            E_bat_Init, U_ac_Init
            T_am, E_PV, T_sol_w, T_sol_r, Q_solar
        - Corrects:
            T_h_Init wrt [T_h_Min, T_h_Max]
            E_bat_Init wrt [E_bat_Min, E_bat_Max]
        - Processes:
            E_l, E_l_Array → DC side (via Eff_Inv)
            Builds E_PV_Reshaped stacked for all PV/PV+Bat houses

    Parameters
    ----------
    ctx : dict
        MPC context built from environment and MPC_Parameters.
    E_PV : array-like, shape (N,)
        PV energy over the MPC horizon (AC-side).
    T_sol_w, T_sol_r, Q_solar : array-like, shape (N,)
        Solar-related disturbances from RC generator.

    Returns
    -------
    reshaped : dict
        Dictionary containing:
            T_h_Init, T_wall_Init, T_attic_Init, T_im_Init
            E_bat_Init, U_ac_Init
            T_am, E_PV, T_sol_w, T_sol_r, Q_solar
            E_Load_Critical_Reshaped, E_l_Reshaped, E_l_Array_DC
            E_PV_Reshaped
    """

    # -------------------------------------------------------------------------
    # Unpack geometry & bounds from ctx
    # -------------------------------------------------------------------------
    N_House   = int(ctx["N_House"])
    N_PV_Bat  = int(ctx["N_PV_Bat"])
    N_Bat     = int(ctx["N_Bat"])
    N_PV      = int(ctx["N_PV"])
    N         = int(ctx["N_horizon"])

    T_h_Min   = float(ctx["T_h_Min"])
    T_h_Max   = float(ctx["T_h_Max"])
    E_bat_Min = float(ctx["E_bat_Min"])
    E_bat_Max = float(ctx["E_bat_Max"])
    Eff_Inv   = float(ctx["Eff_Inv"])

    # Initial conditions from ctx
    T_h_Init     = np.array(ctx["T_h_Init"],     dtype=float)
    T_wall_Init  = np.array(ctx["T_wall_Init"],  dtype=float)
    T_attic_Init = np.array(ctx["T_attic_Init"], dtype=float)
    T_im_Init    = np.array(ctx["T_im_Init"],    dtype=float)
    E_bat_Init   = np.array(ctx["E_bat_Init"],   dtype=float)
    U_ac_Init    = np.array(ctx["U_ac_Init"],    dtype=float)

    # Weather & load from ctx
    T_am       = np.array(ctx["T_am"],      dtype=float)
    Ws         = np.array(ctx["Ws"],      dtype=float)
    E_l        = np.array(ctx["E_l"],       dtype=float)
    E_l_Array  = np.array(ctx["E_l_Array"], dtype=float)
    Energy_Price  = np.array(ctx["Energy_Price"], dtype=float)

    # -------------------------------------------------------------------------
    # 1) Reshape initial conditions to column-like vectors
    # -------------------------------------------------------------------------
    T_h_Init     = T_h_Init.reshape(N_House, 1)
    T_wall_Init  = T_wall_Init.reshape(N_House, 1)
    T_attic_Init = T_attic_Init.reshape(N_House, 1)
    T_im_Init    = T_im_Init.reshape(N_House, 1)

    E_bat_Init   = E_bat_Init.reshape(N_PV_Bat + N_Bat, 1)
    U_ac_Init    = U_ac_Init.reshape(N_House, 1)

    # -------------------------------------------------------------------------
    # 2) Reshape disturbances: weather, PV, RC outputs
    # -------------------------------------------------------------------------
    T_am   = T_am.reshape(N, 1)
    Ws     = Ws.reshape(N, 1)
    E_PV   = np.array(E_PV,   dtype=float).reshape(N, 1)
    T_sol_w = np.array(T_sol_w, dtype=float).reshape(N, 1)
    T_sol_r = np.array(T_sol_r, dtype=float).reshape(N, 1)
    Q_solar = np.array(Q_solar, dtype=float).reshape(N, 1)
    Energy_Price = np.array(Energy_Price, dtype=float).reshape(N, 1)

    # -------------------------------------------------------------------------
    # 3) Correct initial states for boundary violations
    # -------------------------------------------------------------------------
    eps_T = (T_h_Max - T_h_Min) / 10000.0 if T_h_Max > T_h_Min else 1e-6
    eps_E = (E_bat_Max - E_bat_Min) / 10000.0 if E_bat_Max > E_bat_Min else 1e-6

    for ii in range(N_House):
        # House temperature correction
        if T_h_Init[ii, 0] < T_h_Min:
            T_h_Init[ii, 0] = T_h_Min + eps_T

        # House battery SOC correction (only for houses with batteries)
        if ii < (N_PV_Bat + N_Bat):
            if E_bat_Init[ii, 0] > E_bat_Max:
                E_bat_Init[ii, 0] = E_bat_Max - eps_E
            elif E_bat_Init[ii, 0] < E_bat_Min:
                E_bat_Init[ii, 0] = E_bat_Min + eps_E

    # -------------------------------------------------------------------------
    # 4) Extract E_Load_Critical, reshape & convert loads to DC
    # -------------------------------------------------------------------------
    # E_l_Array assumed shape: (N, n_load_channels, N_House)
    # MATLAB: E_Load_Critical = E_l_Array(:,10,:);
    # Python index 9
    E_Load_Critical = E_l_Array[:, 9, :]                    # (N, N_House)
    E_Load_Critical_Reshaped = E_Load_Critical.reshape(N * N_House, 1)

    # Same flattening for total desired load
    E_l_Reshaped = E_l.reshape(N * N_House, 1)

    # Convert to DC side
    E_Load_Critical_Reshaped = E_Load_Critical_Reshaped / Eff_Inv
    E_l_Reshaped             = E_l_Reshaped / Eff_Inv

    # For per-channel loads: first 9 channels AC, channels >=10 converted
    if E_l_Array.shape[1] > 9:
        E_l_Array_DC = np.concatenate(
            [
                E_l_Array[:, :9, :],          # unchanged
                E_l_Array[:, 9:, :] / Eff_Inv # converted to DC
            ],
            axis=1
        )
    else:
        E_l_Array_DC = E_l_Array.copy()

    # -------------------------------------------------------------------------
    # 5) Build PV energy stacked for all PV-bearing houses
    # -------------------------------------------------------------------------
    n_pv_total = N_PV_Bat + N_PV
    if n_pv_total > 0:
        # MATLAB:
        #  E_PV_Reshaped = [];
        #  for ii=1:N_PV_Bat+N_PV
        #      E_PV_Reshaped=[E_PV_Reshaped;E_PV];
        #  end
        E_PV_Reshaped = np.tile(E_PV, (n_pv_total, 1))  # (N * n_pv_total, 1)
    else:
        E_PV_Reshaped = np.zeros((0, 1))

    # -------------------------------------------------------------------------
    # Return everything in a single dictionary
    # -------------------------------------------------------------------------
    reshaped = {
        "T_h_Init": T_h_Init,
        "T_wall_Init": T_wall_Init,
        "T_attic_Init": T_attic_Init,
        "T_im_Init": T_im_Init,
        "E_bat_Init": E_bat_Init,
        "U_ac_Init": U_ac_Init,
        "T_am": T_am,
        "Ws": Ws,
        "E_PV": E_PV,
        "T_sol_w": T_sol_w,
        "T_sol_r": T_sol_r,
        "Q_solar": Q_solar,
        "Energy_Price": Energy_Price,
        "E_Load_Critical_Reshaped": E_Load_Critical_Reshaped,
        "E_l_Reshaped": E_l_Reshaped,
        "E_l_Array_DC": E_l_Array_DC,
        "E_PV_Reshaped": E_PV_Reshaped,
    }

    return reshaped

def Exp_apply_gurobi_params(model, param_dict):
    """
    Apply user-specified Gurobi parameters to a gurobipy.Model.

    Parameters
    ----------
    model : gurobipy.Model
        Gurobi model instance to configure.

    param_dict : dict
        Dictionary of parameters, typically something like:
        {
            'Threads': 8,
            'MIPFocus': 2,
            'TimeLimit': 500.0,
            'MIPGap': 0.01,
            'Cuts': 2,
            'Presolve': 2,
            'OutputFlag': 1,
            'DisplayInterval': 25,
            ...
        }
        Any key with value None is skipped.
        Unknown keys raise a warning (not a crash).
    """

    for key, value in param_dict['gurobi'].items():
        if value is None:
            # Skip entries that remain commented-out / unused
            continue

        try:
            model.setParam(key, value)
            # Optional: print confirmation
            # print(f"Gurobi Param set: {key} = {value}")
        except Exception as e:
            print(f"[WARNING] Could not set Gurobi parameter '{key}' → {value}")
            print(f"          Gurobi error: {e}")

    return model

def Exp_Casadi_unpack_mpc_solution_OffGrid(NLP_Solution, N, Nh_all, Nh_bat, Nh_pv):
    """
    Unpack the optimal decision vector 'x' from a CasADi NLP solution
    into named numpy arrays corresponding to the original SX.sym blocks.

    Variables and sizes (in the same order as in ca.vertcat):

        T_wall     : Nh_all * N
        T_ave      : Nh_all * N
        T_att      : Nh_all * N
        T_im       : Nh_all * N

        U_ac       : Nh_all * N

        E_bat      : Nh_bat * N
        Gamma      : Nh_bat * N
        theta_bat  : Nh_bat * N
        f_on       : Nh_bat * N
        f_off      : Nh_bat * N

        u_pv       : Nh_pv * N
        g          : Nh_pv * N

        E_load     : Nh_all * N
        eps_h      : Nh_all * N
        eps_l      : Nh_all * N

        E_g        : N
    """

    # Get optimal x as a flat numpy vector
    x_opt = np.array(NLP_Solution["x"]).flatten()
    # or: x_opt = NLP_Solution["x"].full().flatten()  if using DM

    idx = 0

    def _take(block_size):
        nonlocal idx
        block = x_opt[idx:idx + block_size]
        idx += block_size
        return block

    # ---- sizes ----
    n_T      = Nh_all * N
    n_U_ac   = Nh_all * N
    n_bat    = Nh_bat * N
    n_pv     = Nh_pv * N
    n_load   = Nh_all * N
    n_eps    = Nh_all * N
    n_Eg     = N

    # ---- unpack in the SAME ORDER as vertcat ----
    T_wall   = _take(n_T).reshape(Nh_all, N)
    T_ave    = _take(n_T).reshape(Nh_all, N)
    T_att    = _take(n_T).reshape(Nh_all, N)
    T_im     = _take(n_T).reshape(Nh_all, N)

    U_ac     = _take(n_U_ac).reshape(Nh_all, N)

    E_bat    = _take(n_bat).reshape(Nh_bat, N)
    Gamma    = _take(n_bat).reshape(Nh_bat, N)
    theta_bat= _take(n_bat).reshape(Nh_bat, N)
    f_on     = _take(n_bat).reshape(Nh_bat, N)
    f_off    = _take(n_bat).reshape(Nh_bat, N)
    g        = _take(n_pv).reshape(Nh_pv, N)

    E_load   = _take(n_load).reshape(Nh_all, N)
    eps_h    = _take(n_eps).reshape(Nh_all, N)
    eps_l    = _take(n_eps).reshape(Nh_all, N)

    # Sanity check: we should have consumed all of x_opt
    if idx != len(x_opt):
        raise ValueError(f"Unpacking error: used {idx} of {len(x_opt)} entries in x_opt")

    return {
        "T_wall": T_wall,
        "T_ave": T_ave,
        "T_att": T_att,
        "T_im": T_im,
        "U_ac": U_ac,
        "E_bat": E_bat,
        "Gamma": Gamma,
        "theta_bat": theta_bat,
        "f_on": f_on,
        "f_off": f_off,
        "g": g,
        "E_load": E_load,
        "eps_h": eps_h,
        "eps_l": eps_l
    }

def Exp_Casadi_unpack_mpc_solution_OnGrid(NLP_Solution, N, Nh_all, Nh_bat, Nh_pv):
    """
    Unpack the optimal decision vector 'x' from a CasADi NLP solution
    into named numpy arrays corresponding to the original SX.sym blocks.

    Variables and sizes (in the same order as in ca.vertcat):

        T_wall     : Nh_all * N
        T_ave      : Nh_all * N
        T_att      : Nh_all * N
        T_im       : Nh_all * N

        U_ac       : Nh_all * N

        E_bat      : Nh_bat * N
        Gamma      : Nh_bat * N
        theta_bat  : Nh_bat * N
        f_on       : Nh_bat * N
        f_off      : Nh_bat * N

        u_pv       : Nh_pv * N
        g          : Nh_pv * N

        E_load     : Nh_all * N
        eps_h      : Nh_all * N
        eps_l      : Nh_all * N

        E_g        : N
    """

    # Get optimal x as a flat numpy vector
    x_opt = np.array(NLP_Solution["x"]).flatten()
    # or: x_opt = NLP_Solution["x"].full().flatten()  if using DM

    idx = 0

    def _take(block_size):
        nonlocal idx
        block = x_opt[idx:idx + block_size]
        idx += block_size
        return block

    # ---- sizes ----
    n_T      = Nh_all * N
    n_U_ac   = Nh_all * N
    n_bat    = Nh_bat * N
    n_pv     = Nh_pv * N
    n_load   = Nh_all * N
    n_eps    = Nh_all * N
    n_Eg     = N

    # ---- unpack in the SAME ORDER as vertcat ----
    T_wall   = _take(n_T).reshape(Nh_all, N)
    T_ave    = _take(n_T).reshape(Nh_all, N)
    T_att    = _take(n_T).reshape(Nh_all, N)
    T_im     = _take(n_T).reshape(Nh_all, N)

    U_ac     = _take(n_U_ac).reshape(Nh_all, N)

    E_bat    = _take(n_bat).reshape(Nh_bat, N)
    Gamma    = _take(n_bat).reshape(Nh_bat, N)

    u_pv     = _take(n_pv).reshape(Nh_pv, N)
    eps_h    = _take(n_eps).reshape(Nh_all, N)

    E_g      = _take(n_Eg)  # shape (N,)

    # Sanity check: we should have consumed all of x_opt
    if idx != len(x_opt):
        raise ValueError(f"Unpacking error: used {idx} of {len(x_opt)} entries in x_opt")

    return {
        "T_wall": T_wall,
        "T_ave": T_ave,
        "T_att": T_att,
        "T_im": T_im,
        "U_ac": U_ac,
        "E_bat": E_bat,
        "Gamma": Gamma,
        "u_pv": u_pv,
        "eps_h": eps_h,
        "E_g": E_g,
    }

def Exp_Gurobi_unpack_mpc_solution_OffGrid(
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
):
    """
    Extract optimized MPC variables from Gurobi MVar objects and reshape
    them into (house, time) style arrays.

    Assumes the following sizes (as in the model creation):

        T_wall, T_ave, T_att, T_im : Nh_all * N
        U_ac                       : Nh_all * N

        E_bat, Gamma, theta_bat,
        f_on, f_off                : Nh_bat * N

        u_pv, g                    : Nh_pv * N

        E_load, eps_h, eps_l       : Nh_all * N

        E_g                        : N
    """

    # helper for reshaping a length (Nh * N) vector into (Nh, N)
    def _reshape_house_time(vec, Nh):
        return np.array(vec).reshape(Nh, N)

    sol = {}

    # ---- Thermal states ----
    sol["T_wall"] = _reshape_house_time(T_wall.X, Nh_all)
    sol["T_ave"]  = _reshape_house_time(T_ave.X,  Nh_all)
    sol["T_att"]  = _reshape_house_time(T_att.X,  Nh_all)
    sol["T_im"]   = _reshape_house_time(T_im.X,   Nh_all)

    # ---- HVAC ----
    sol["U_ac"]   = _reshape_house_time(U_ac.X,   Nh_all)

    # ---- Battery vars ----
    sol["E_bat"]     = _reshape_house_time(E_bat.X,     Nh_bat)
    sol["Gamma"]     = _reshape_house_time(Gamma.X,     Nh_bat)
    sol["theta_bat"] = _reshape_house_time(theta_bat.X, Nh_bat)
    sol["f_on"]      = _reshape_house_time(f_on.X,      Nh_all)
    sol["f_off"]     = _reshape_house_time(f_off.X,     Nh_all)

    # ---- PV vars ----
    sol["g"]    = _reshape_house_time(g.X,    Nh_pv)

    # ---- Load and slack ----
    sol["E_load"] = _reshape_house_time(E_load.X, Nh_all)
    sol["eps_h"]  = _reshape_house_time(eps_h.X,  Nh_all)
    sol["eps_l"]  = _reshape_house_time(eps_l.X,  Nh_all)

    return sol

def Exp_Gurobi_unpack_mpc_solution_OnGrid(
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
):
    """
    Extract optimized MPC variables from Gurobi MVar objects and reshape
    them into (house, time) style arrays.

    Assumes the following sizes (as in the model creation):

        T_wall, T_ave, T_att, T_im : Nh_all * N
        U_ac                       : Nh_all * N

        E_bat, Gamma, theta_bat,
        f_on, f_off                : Nh_bat * N

        u_pv, g                    : Nh_pv * N

        E_load, eps_h, eps_l       : Nh_all * N

        E_g                        : N
    """

    # helper for reshaping a length (Nh * N) vector into (Nh, N)
    def _reshape_house_time(vec, Nh):
        return np.array(vec).reshape(Nh, N)

    sol = {}

    # ---- Thermal states ----
    sol["T_wall"] = _reshape_house_time(T_wall.X, Nh_all)
    sol["T_ave"]  = _reshape_house_time(T_ave.X,  Nh_all)
    sol["T_att"]  = _reshape_house_time(T_att.X,  Nh_all)
    sol["T_im"]   = _reshape_house_time(T_im.X,   Nh_all)

    # ---- HVAC ----
    sol["U_ac"]   = _reshape_house_time(U_ac.X,   Nh_all)

    # ---- Battery vars ----
    sol["E_bat"]     = _reshape_house_time(E_bat.X,     Nh_bat)
    sol["Gamma"]     = _reshape_house_time(Gamma.X,     Nh_bat)

    # ---- PV vars ----
    sol["u_pv"] = _reshape_house_time(u_pv.X, Nh_pv)

    # ---- Load and slack ----
    sol["eps_h"]  = _reshape_house_time(eps_h.X,  Nh_all)

    # ---- Grid energy ----
    sol["E_g"] = np.array(E_g.X).reshape(N,)   # (N,)

    return sol

def Exp_flatten_solution_dict(solution_dict):
    """
    Convert a dict of numpy arrays (e.g., shaped (Nh, N)) into
    a dict of flattened Python lists (size Nh*N or N).

    Example:
        input['T_wall'] = array shape (Nh_all, N)
        output['T_wall'] = list length Nh_all*N
    """
    flat_dict = {}

    for key, val in solution_dict.items():
        # Ensure numpy
        arr = np.asarray(val)

        # Flatten row-major to match MVar ordering
        flat_arr = arr.reshape(-1)

        # Convert to Python list
        flat_dict[key] = flat_arr.tolist()

    return flat_dict

def Exp_convert_OffGrid_solution_to_arrays(Solution_Dict_List, 
                                       N, Nh_all, Nh_bat, Nh_pv):
    """
    Convert Off-Grid solution dict of FLATTENED lists into
    reshaped NumPy arrays of size (Nh, N).
    """

    def reshape_flat(vec, Nh):
        return np.asarray(vec).reshape(Nh, N)

    sol = {}

    # Thermal states
    sol["T_wall"] = reshape_flat(Solution_Dict_List["T_wall"], Nh_all)
    sol["T_ave"]  = reshape_flat(Solution_Dict_List["T_ave"],  Nh_all)
    sol["T_att"]  = reshape_flat(Solution_Dict_List["T_att"],  Nh_all)
    sol["T_im"]   = reshape_flat(Solution_Dict_List["T_im"],   Nh_all)

    # HVAC
    sol["U_ac"]   = reshape_flat(Solution_Dict_List["U_ac"],   Nh_all)

    # Battery vars
    sol["E_bat"]     = reshape_flat(Solution_Dict_List["E_bat"],     Nh_bat)
    sol["Gamma"]     = reshape_flat(Solution_Dict_List["Gamma"],     Nh_bat)
    sol["theta_bat"] = reshape_flat(Solution_Dict_List["theta_bat"], Nh_bat)
    sol["f_on"]      = reshape_flat(Solution_Dict_List["f_on"],      Nh_bat)
    sol["f_off"]     = reshape_flat(Solution_Dict_List["f_off"],     Nh_bat)

    # PV
    sol["g"] = reshape_flat(Solution_Dict_List["g"], Nh_pv)

    # Load and slack
    sol["E_load"] = reshape_flat(Solution_Dict_List["E_load"], Nh_all)
    sol["eps_h"]  = reshape_flat(Solution_Dict_List["eps_h"],  Nh_all)
    sol["eps_l"]  = reshape_flat(Solution_Dict_List["eps_l"],  Nh_all)

    return sol

def Exp_convert_OnGrid_solution_to_arrays(Solution_Dict_List,
                                      N, Nh_all, Nh_bat, Nh_pv):
    """
    Convert On-Grid solution dict of FLATTENED lists into 
    reshaped NumPy arrays of size (Nh, N), plus E_g of size (N,).
    """

    def reshape_flat(vec, Nh):
        return np.asarray(vec).reshape(Nh, N)

    sol = {}

    # Thermal states
    sol["T_wall"] = reshape_flat(Solution_Dict_List["T_wall"], Nh_all)
    sol["T_ave"]  = reshape_flat(Solution_Dict_List["T_ave"],  Nh_all)
    sol["T_att"]  = reshape_flat(Solution_Dict_List["T_att"],  Nh_all)
    sol["T_im"]   = reshape_flat(Solution_Dict_List["T_im"],   Nh_all)

    # HVAC
    sol["U_ac"]   = reshape_flat(Solution_Dict_List["U_ac"],   Nh_all)

    # Battery (only SoC / charge power)
    sol["E_bat"] = reshape_flat(Solution_Dict_List["E_bat"], Nh_bat)
    sol["Gamma"] = reshape_flat(Solution_Dict_List["Gamma"], Nh_bat)

    # PV modulations
    sol["u_pv"] = reshape_flat(Solution_Dict_List["u_pv"], Nh_pv)

    # Load + slack
    # sol["E_load"] = reshape_flat(Solution_Dict_List["E_load"], Nh_all)
    sol["eps_h"]  = reshape_flat(Solution_Dict_List["eps_h"],  Nh_all)

    # Grid import/export
    sol["E_g"] = np.asarray(Solution_Dict_List["E_g"]).reshape(N,)

    return sol

def Exp_priority_stack_controller_mpc_smartcommunity(
    E_LoadData: np.ndarray,
    E_Control: float,
) -> np.ndarray:
    """
    Python version of PriorityStackController_MPC_SmartCommunity.

    Parameters
    ----------
    E_LoadData : np.ndarray
        1D array of equipment-wise energy usage (all columns for a single
        time step and house), length = Column_E_LoadData.
        First 9 entries are ignored; entries [9:] are prioritized loads.

    E_Control : float
        Scalar control from MPC (E_l), energy to be 'supplied' by shedding.

    Returns
    -------
    U_k_PriorityStack : np.ndarray
        1D array of length (Column_E_LoadData - 9), binary {0,1}:
        1 means that prioritized device is shed (controlled), 0 otherwise.
    """
    E_LoadData = np.asarray(E_LoadData).flatten()
    n_cols = E_LoadData.shape[0]

    # Number of prioritized loads (columns after the first 9)
    n_prior = n_cols - 9
    if n_prior <= 0:
        return np.zeros(0, dtype=float)

    U_k_PriorityStack = np.zeros(n_prior, dtype=float)

    E_Control_Abs = abs(E_Control)
    if E_Control_Abs <= 0.0:
        # No shedding required
        return U_k_PriorityStack

    # Priority stack logic
    E_Supplied = 0.0

    # MATLAB: for ii = 9+1 : Column_E_LoadData
    for ii in range(9, n_cols):  # Python 0-based, 9 is the 10th column
        if E_Supplied < E_Control_Abs:  # and E_LoadData[ii]>0
            # Tentatively shed this device
            E_Supplied = E_Supplied + E_LoadData[ii]
            U_k_PriorityStack[ii - 9] = 1.0

            if np.isclose(E_Supplied, E_Control_Abs):
                # Exactly matched → keep this device ON (shed) and break
                break
            elif E_Supplied > E_Control_Abs:
                # Overshoot: un-shed this device and break
                U_k_PriorityStack[ii - 9] = 0.0
                break

    return U_k_PriorityStack

def Exp_SingleMultiHouse_OffGrid_MPC_Sol_To_Action_Generator(
    Solution_Dict_np,
    N_House: int,
    N_PV_Bat: int,
    N_Bat: int,
    E_l_Array: np.ndarray | None = None,
    epsilon: float = 1e-5,
) -> np.ndarray:
    """
    OFF-GRID MPC → simulator action (FIRST timestep only)
    Output shape: (1, 13, N_House)
    """

    # Extract MPC outputs
    U_ac  = Solution_Dict_np["U_ac"]      # (N_House, N)
    Gamma = Solution_Dict_np["Gamma"]     # (N_PV_Bat + N_Bat, N)
    g_pv  = Solution_Dict_np["g"]         # (N_PV_Bat + N_PV, N)
    E_Load = Solution_Dict_np["E_load"]   # (N_House, N)

    Nh_bat = N_PV_Bat + N_Bat
    Nh_pv  = g_pv.shape[0]
    N_PV   = max(0, Nh_pv - N_PV_Bat)

    # Time horizon
    N = U_ac.shape[1]

    # Initialize full horizon control
    U_all = np.zeros((N, 13, N_House), dtype=float)

    # ---------------------------------------------------------
    # 1) AC on/off → col 3
    # ---------------------------------------------------------
    U_all[:, 2, :] = U_ac.T

    # ---------------------------------------------------------
    # 2) Battery charge/discharge → cols 1–2
    #    EXACT loop logic you requested
    # ---------------------------------------------------------
    for j in range(Nh_bat):
        h = j
        gamma_h = Gamma[j, :]   # (N,)

        charge    = np.zeros_like(gamma_h, dtype=float)
        discharge = np.zeros_like(gamma_h, dtype=float)

        # discharge → (0,1)
        mask_discharge = gamma_h > epsilon
        discharge[mask_discharge] = 1.0

        # charge → (1,0)
        mask_charge = gamma_h < -epsilon
        charge[mask_charge] = 1.0

        U_all[:, 0, h] = charge
        U_all[:, 1, h] = discharge

    # ---------------------------------------------------------
    # 3) Priority loads → cols 4–11 (computed via priority stack)
    #    E_l_Array: (N, Column_E_LoadData, N_House)
    #    For each (t, h), compute U_k_PriorityStack (length = Cols-9)
    #    and map into 8 control columns in U_all[t,3:11,h]
    # ---------------------------------------------------------
    N_time, n_cols_el, n_house_el = E_l_Array.shape
    assert N_time == N, "E_l_Array time dimension must match MPC horizon"
    assert n_house_el == N_House, "E_l_Array house dimension must match N_House"

    for t in range(N):
        for h in range(N_House):
            # Equipment-wise load profile for this time & house
            E_LoadData_th = E_l_Array[t, :, h]

            # Scalar control from MPC for this house & time
            E_Control_th = E_Load[h, t]

            U_k_PriorityStack = Exp_priority_stack_controller_mpc_smartcommunity(
                E_LoadData_th,
                E_Control_th,
            )

            # We expect 8 prioritized loads → cols 3..10 in U_all
            # (matching MATLAB: U_k(ii,4:end,jj) = U_k_PriorityStack)
            # If Column_E_LoadData-9 != 8, this will still map the first len(U_k_PriorityStack).
            n_prior = U_k_PriorityStack.shape[0]
            n_prior_to_assign = min(n_prior, 8)
            U_all[t, 3:3 + n_prior_to_assign, h] = U_k_PriorityStack[:n_prior_to_assign]

    # ---------------------------------------------------------
    # 4) PV curtailment (off-grid)
    #     → set to 1 for all PV houses (PV+BAT + PV-only)
    # ---------------------------------------------------------
    pvbat_idx = np.arange(N_PV_Bat)

    pv_only_start = N_PV_Bat + N_Bat
    pv_only_end   = pv_only_start + N_PV
    pv_only_idx   = np.arange(pv_only_start, pv_only_end)

    pv_global_idx = np.concatenate([pvbat_idx, pv_only_idx])

    U_all[:, 11, pv_global_idx] = 1.0

    # ---------------------------------------------------------
    # 5) Heating mode → col 13 = 0
    # ---------------------------------------------------------
    U_all[:, 12, :] = 0.0

    # ---------------------------------------------------------
    # RETURN ONLY FIRST TIMESTEP AS (1,13,N_House)
    # ---------------------------------------------------------
    return U_all[:1, :, :]

def Exp_SingleMultiHouse_OnGrid_MPC_Sol_To_Action_Generator(
    Solution_Dict_np,
    N_House: int,
    N_PV_Bat: int,
    N_Bat: int,
    E_l_Array: np.ndarray | None = None,
    epsilon: float = 1e-5,
) -> np.ndarray:
    """
    ON-GRID MPC → simulator action (FIRST timestep only)
    Output shape: (1, 13, N_House)
    """

    # Extract MPC outputs
    U_ac  = Solution_Dict_np["U_ac"]      # (N_House, N)
    Gamma = Solution_Dict_np["Gamma"]     # (N_PV_Bat + N_Bat, N)
    u_pv  = Solution_Dict_np["u_pv"]      # (N_PV_Bat + N_PV, N)

    Nh_bat = N_PV_Bat + N_Bat
    Nh_pv  = u_pv.shape[0]
    N_PV   = max(0, Nh_pv - N_PV_Bat)

    # Time horizon
    N = U_ac.shape[1]

    # Initialize full horizon control
    U_all = np.zeros((N, 13, N_House), dtype=float)

    # ---------------------------------------------------------
    # 1) AC on/off → col 3
    # ---------------------------------------------------------
    U_all[:, 2, :] = U_ac.T

    # ---------------------------------------------------------
    # 2) Battery charge/discharge → cols 1–2
    #    EXACT loop logic you requested
    # ---------------------------------------------------------
    for j in range(Nh_bat):
        h = j
        gamma_h = Gamma[j, :]   # (N,)

        charge    = np.zeros_like(gamma_h, dtype=float)
        discharge = np.zeros_like(gamma_h, dtype=float)

        mask_discharge = gamma_h > epsilon
        discharge[mask_discharge] = 1.0

        mask_charge = gamma_h < -epsilon
        charge[mask_charge] = 1.0

        U_all[:, 0, h] = charge
        U_all[:, 1, h] = discharge

    # ---------------------------------------------------------
    # 3) Priority loads → cols 4–11 (binary from E_l_Array)
    #    E_l_Array structure:
    #       axis 0: time (N)
    #       axis 1: columns, where:
    #           0..8   : ignored
    #           9..16  : 8 prioritized loads (kWh values)
    #       axis 2: houses
    # ---------------------------------------------------------
    if E_l_Array is not None:
        # Extract only the 8 prioritized load columns (10th–17th, 1-based)
        # Shape: (N, 8, N_House)
        prioritized_kwh = E_l_Array[:, 9:17, :]

        # Convert kWh to on/off flags: 1 if > 0, else 0
        prioritized_onoff = (prioritized_kwh > 0.0).astype(float)

        # Map to control columns 3..10 in U_all
        U_all[:, 3:11, :] = prioritized_onoff

    # ---------------------------------------------------------
    # 4) PV curtailment from u_pv → col 12
    #    Map u_pv rows to houses:
    #       rows 0..N_PV_Bat-1  → PV+BAT houses
    #       rows N_PV_Bat..end  → PV-only houses
    # ---------------------------------------------------------

    # PV+BAT houses
    for j in range(N_PV_Bat):
        U_all[:, 11, j] = u_pv[j, :]

    # PV-only houses
    pv_only_start = N_PV_Bat + N_Bat
    pv_only_end   = pv_only_start + N_PV
    for k, h in enumerate(range(pv_only_start, pv_only_end)):
        row = N_PV_Bat + k
        U_all[:, 11, h] = u_pv[row, :]

    # ---------------------------------------------------------
    # 5) Heating mode → col 13 = 0
    # ---------------------------------------------------------
    U_all[:, 12, :] = 0.0

    # ---------------------------------------------------------
    # RETURN ONLY FIRST TIMESTEP AS (1,13,N_House)
    # ---------------------------------------------------------
    return U_all[:1, :, :]



###############################################################################################################
## Experiment MPC RL Controllers Helper Module - RL Specific Custom Functions
###############################################################################################################

###############################################################################################################
## Environment Factory Module for SmartCommunitySimulator
###############################################################################################################

def make_env_fn(
    simulation_params,
    community_params,
    plant_initial_conditions,
    simulation_period,
    plant_dynamic_params,
    data_paths,
    result_filefolder_paths,
    simulation_ObservationActionSpace_Functions,
    simulation_RewardTerminateTruncate_Functions,
    rl_log_root,
):
    """
    Returns a function that creates a *single* SmartCommunitySimulator instance.
    This factory must return a function (not an env directly!) for DummyVecEnv.
    """

    def _init():
        # Create the environment
        env = SC_Plant.SmartCommunitySimulator(
            simulation_params=simulation_params,
            community_params=community_params,
            plant_initial_conditions=plant_initial_conditions,
            simulation_period=simulation_period,
            plant_dynamic_params=plant_dynamic_params,
            data_paths=data_paths,
            result_filefolder_paths=result_filefolder_paths,
            simulation_ObservationActionSpace_Functions=simulation_ObservationActionSpace_Functions,
            simulation_RewardTerminateTruncate_Functions=simulation_RewardTerminateTruncate_Functions,
        )

        # Log directory for monitor.csv
        monitor_file = os.path.join(rl_log_root, "monitor.csv")

        # Wrap with SB3 monitor
        env = Monitor(env, filename=monitor_file)

        # Gymnasium requires seeding via reset()
        # env.reset(seed=seed)

        return env

    return _init


def build_policy_kwargs(
    actor_layers=None,
    critic_layers=None,
    activation_name: str = "relu",
):
    """
    Build policy_kwargs for SAC in a flexible, user-controlled way.

    Parameters
    ----------
    actor_layers : list[int] | None
        Hidden layer sizes for the actor network (pi).
        Example: [256, 256]. If None, defaults to [256, 256].

    critic_layers : list[int] | None
        Hidden layer sizes for the critic networks (qf).
        If None, critic will share the same net_arch as actor
        (i.e., a single shared MLP for both).

    activation_name : str
        Name of activation function to use: "relu", "tanh",
        "leaky_relu", "elu", "silu".
    """

    # ------------------------------
    # 1. Map string -> activation
    # ------------------------------
    activation_name = activation_name.lower()
    activation_map = {
        "relu": nn.ReLU,
        "tanh": nn.Tanh,
        "leaky_relu": nn.LeakyReLU,
        "elu": nn.ELU,
        "silu": nn.SiLU,   # a.k.a. swish
    }

    if activation_name not in activation_map:
        raise ValueError(
            f"Unknown activation '{activation_name}'. "
            f"Supported: {list(activation_map.keys())}"
        )

    activation_fn = activation_map[activation_name]

    # ------------------------------
    # 2. Default actor layers
    # ------------------------------
    if actor_layers is None:
        actor_layers = [256, 256]

    # ------------------------------
    # 3. Build net_arch
    # ------------------------------
    if critic_layers is None:
        # Shared architecture for actor & critic
        net_arch = actor_layers
    else:
        # Separate architectures for actor (pi) and critic (qf)
        net_arch = dict(
            pi=actor_layers,
            qf=critic_layers,
        )

    # ------------------------------
    # 4. Return policy_kwargs dict
    # ------------------------------
    policy_kwargs = dict(
        activation_fn=activation_fn,
        net_arch=net_arch,
    )

    return policy_kwargs

# =====================================================================================
# Helper 5: RL tuning (Lambda’s etc.) from RL_Parameters
# =====================================================================================

def _get_rl_tuning(RL_Parameters):
    tuning = {
        "RL_HORIZON_HOURS": int(RL_Parameters["RL_HORIZON_HOURS"]),
        "RL_HORIZON_HOUR_AVG": int(RL_Parameters["RL_HORIZON_HOUR_AVG"]),
        "RL_DATA_RES": float(RL_Parameters["RL_DATA_RES"]),
        "RL_HORIZON_N": int(RL_Parameters["RL_HORIZON_N"]),
        "RL_HORIZON_AVG_N": int(RL_Parameters["RL_HORIZON_AVG_N"]),
    }
    return tuning

# =====================================================================================
# Helper 3: Build RL horizon disturbances (W_k_RL equivalent)
# =====================================================================================

def _build_rl_horizon_slices(env, RL_Parameters):
    """
    Builds the MPC horizon window for weather + load disturbances, mimicking W_k_MPC:
        E_l, E_l_Array, Ws, T_am, GHI, DNI
    plus Initial_DecisionVariables from MPC_Parameters.
    """
    N_horizon = int(RL_Parameters["RL_HORIZON_N"])
    t0 = int(env.time_iter)
    t1 = t0 + N_horizon

    # Full-series weather arrays
    Ws_full   = np.array(env.Ws)
    T_am_full = np.array(env.T_am)
    GHI_full  = np.array(env.GHI)
    DNI_full  = np.array(env.DNI)
    DateTime_Matrix_full = np.array(env.DateTime_Matrix)

    # Full-series load arrays
    E_LoadData_full      = np.array(env.E_LoadData)
    E_Load_Desired_Array = np.array(env.E_Load_Desired_Array)

    # Reshape for single house for consistency
    if (len(E_LoadData_full.shape) == 2):

        E_LoadData_full = np.reshape(E_LoadData_full, (E_LoadData_full.shape[0], E_LoadData_full.shape[1], 1))


    # Slice along time: [t0, t1)
    Ws   = Ws_full[t0:t1, 0]
    T_am = T_am_full[t0:t1, 0]
    GHI  = GHI_full[t0:t1, 0]
    DNI  = DNI_full[t0:t1, 0]
    DateTime_Matrix = DateTime_Matrix_full[t0:t1, :]

    # For loads: E_l = desired, E_l_Array = full data
    E_l       = E_Load_Desired_Array[t0:t1, :]   # (N, N_House)
    E_l_Array = E_LoadData_full[t0:t1, :, :]

    # Get E_l_Max for RL Action Normalization
    E_l_Max = E_Load_Desired_Array.max()

    # For Energy_Price
    Energy_Price_full   = np.array(env.Energy_Price)
    Energy_Price = Energy_Price_full[t0:t1, 4]

    

    return {
        "E_l": E_l,
        "E_l_Max": E_l_Max,
        "E_l_Array": E_l_Array,
        "Ws": Ws,
        "T_am": T_am,
        "GHI": GHI,
        "DNI": DNI,
        "DateTime_Matrix": DateTime_Matrix,
        "Energy_Price": Energy_Price,
    }

# =====================================================================================
# High-level context builder: bundles all of the above into one dict
# =====================================================================================

def build_Community_rl_context(env, RL_Parameters):
    """
    Builds a context dict containing everything the controller needs for
    the RL formulation, mirroring the MATLAB 'parameter unpacking' block.
    """
    # Community
    N_House, N_PV_Bat, N_Bat, N_PV, N_None = _get_community_sizes(env)

    # Initial states
    init = _get_initial_states(env, N_PV_Bat, N_Bat)

    # Horizon disturbances
    wmpc = _build_rl_horizon_slices(env, RL_Parameters)

    # Plant & house params
    plant, house = _get_plant_and_house_params(env)

    # MPC tuning
    tuning = _get_rl_tuning(RL_Parameters)

    # Simulation step
    sim_step = _get_sim_step(env)

    

    # Bundle everything into a single context dict
    ctx = {
        "N_House": N_House,
        "N_PV_Bat": N_PV_Bat,
        "N_Bat": N_Bat,
        "N_PV": N_PV,
        "N_None": N_None,

        # Initial states
        **init,

        # Disturbances / W_k_MPC-like
        **wmpc,

        # Plant / house params
        "plant": plant,
        "house": house,

        # Individual plant scalars (for convenience)
        "T_h_Max": plant["T_h_Max"],
        "T_h_Min": plant["T_h_Min"],
        "Q_AC": plant["Q_AC"],
        "E_AC": plant["E_AC"],
        "ACLoad_StartUp_Power": plant["ACLoad_StartUp_Power"],
        "Eff_Inv": plant["Eff_Inv"],
        "E_bat_Max": plant["E_bat_Max"],
        "E_bat_Min": plant["E_bat_Min"],
        "Gamma_Charging": plant["Gamma_Charging"],
        "Gamma_Discharging": plant["Gamma_Discharging"],
        "P_bat": plant["P_bat"],

        "Q_ac": house["Q_ac"],

        # RL tuning
        **tuning,

        # Simulation dt
        "Simulation_StepSize": sim_step,
    }

    # ---------------------------------------------------------------
    # Plant-level parameters (include these now!)
    # ---------------------------------------------------------------
    ctx["HEMSPlant_Params"] = env.HEMSPlant_Params
    ctx["HEMSHouse_Params"] = env.HEMSHouse_Params
    ctx["Simulation_Params"] = env.simulation_params

    return ctx

def build_Community_rl_short_context(env):
    """
    Builds a context dict containing everything the controller needs for
    the MRL formulation, mirroring the MATLAB 'parameter unpacking' block.
    """
    # Community
    N_House, N_PV_Bat, N_Bat, N_PV, N_None = _get_community_sizes(env)

    # Bundle everything into a single context dict
    ctx = {
        "N_House": N_House,
        "N_PV_Bat": N_PV_Bat,
        "N_Bat": N_Bat,
        "N_PV": N_PV,
        "N_None": N_None,
    }

    return ctx

# ---------------------------------------------------------------
# RL Observation/Action Parsers
# ---------------------------------------------------------------

# ============================================================
#  OFF-GRID: OBSERVATION PARSER
# ============================================================

def Exp_SingleMultiHouse_OffGrid_parse_observation(
    obs: np.ndarray,
    SmartComSim_Object, RL_Parameters
) -> dict:
    """
    Parse a flat OFF-GRID observation vector into named components.

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

    where H_factor = RL_HORIZON_N / RL_HORIZON_AVG_N (integer division).
    """

    # Build context from env
    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House  = int(ctx["N_House"])
    N_PV_Bat = int(ctx["N_PV_Bat"])
    N_Bat    = int(ctx["N_Bat"])

    RL_HORIZON_N     = int(RL_Parameters["RL_HORIZON_N"])
    RL_HORIZON_AVG_N = int(RL_Parameters["RL_HORIZON_AVG_N"])
    if RL_HORIZON_AVG_N <= 0:
        raise ValueError("RL_HORIZON_AVG_N must be > 0")

    H_factor = RL_HORIZON_N // RL_HORIZON_AVG_N

    out: dict[str, np.ndarray | float] = {}
    idx = 0

    # 1) Th(N_House)
    out["Th"] = obs[idx : idx + N_House]
    idx += N_House

    # 2) E_Bat(N_PV_Bat + N_Bat)
    n_e_bat = N_PV_Bat + N_Bat
    out["E_Bat"] = obs[idx : idx + n_e_bat]
    idx += n_e_bat

    # 3) U_ac_prev(N_House)
    out["U_ac_prev"] = obs[idx : idx + N_House]
    idx += N_House

    # 4) E_l_now(N_House)
    out["E_l_now"] = obs[idx : idx + N_House]
    idx += N_House

    # 5) E_cri_now(N_House)
    out["E_cri_now"] = obs[idx : idx + N_House]
    idx += N_House

    # 6) E_PV_now(1)
    out["E_PV_now"] = float(obs[idx])
    idx += 1

    # 7) T_am_now(1)
    out["T_am_now"] = float(obs[idx])
    idx += 1

    # 8) E_l_future(H_factor * N_House)
    n_l_future = H_factor * N_House
    out["E_l_future"] = obs[idx : idx + n_l_future]
    idx += n_l_future

    # 9) E_cri_future(H_factor * N_House)
    n_cri_future = H_factor * N_House
    out["E_cri_future"] = obs[idx : idx + n_cri_future]
    idx += n_cri_future

    # 10) E_PV_future(H_factor)
    out["E_PV_future"] = obs[idx : idx + H_factor]
    idx += H_factor

    # 11) T_am_future(H_factor)
    out["T_am_future"] = obs[idx : idx + H_factor]
    idx += H_factor

    return out


# ============================================================
#  ON-GRID: OBSERVATION PARSER
# ============================================================

def Exp_SingleMultiHouse_OnGrid_parse_observation(
    obs: np.ndarray,
    SmartComSim_Object, RL_Parameters
) -> dict:
    """
    Parse a flat ON-GRID observation vector into named components.

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

    where H_factor = RL_HORIZON_N / RL_HORIZON_AVG_N (integer division).
    """

    # Build context from env
    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House  = int(ctx["N_House"])
    N_PV_Bat = int(ctx["N_PV_Bat"])
    N_Bat    = int(ctx["N_Bat"])

    RL_HORIZON_N     = int(RL_Parameters["RL_HORIZON_N"])
    RL_HORIZON_AVG_N = int(RL_Parameters["RL_HORIZON_AVG_N"])
    if RL_HORIZON_AVG_N <= 0:
        raise ValueError("RL_HORIZON_AVG_N must be > 0")   
    

    H_factor = RL_HORIZON_N // RL_HORIZON_AVG_N

    out: dict[str, np.ndarray | float] = {}
    idx = 0

    # 1) Th(N_House)
    out["Th"] = obs[idx : idx + N_House]
    idx += N_House

    # 2) E_Bat(N_PV_Bat + N_Bat)
    n_e_bat = N_PV_Bat + N_Bat
    out["E_Bat"] = obs[idx : idx + n_e_bat]
    idx += n_e_bat

    # 3) E_l_now(N_House)
    out["E_l_now"] = obs[idx : idx + N_House]
    idx += N_House

    # 4) E_PV_now(1)
    out["E_PV_now"] = float(obs[idx])
    idx += 1

    # 5) T_am_now(1)
    out["T_am_now"] = float(obs[idx])
    idx += 1

    # 6) E_Price_now(1)
    out["E_Price_now"] = float(obs[idx])
    idx += 1

    # 7) E_l_future(H_factor * N_House)
    n_l_future = H_factor * N_House
    out["E_l_future"] = obs[idx : idx + n_l_future]
    idx += n_l_future

    # 8) E_PV_future(H_factor)
    out["E_PV_future"] = obs[idx : idx + H_factor]
    idx += H_factor

    # 9) T_am_future(H_factor)
    out["T_am_future"] = obs[idx : idx + H_factor]
    idx += H_factor

    # 10) E_price_future(H_factor)
    out["E_price_future"] = obs[idx : idx + H_factor]
    idx += H_factor

    return out


# ============================================================
#  OFF-GRID: ACTION PARSER
# ============================================================

def Exp_SingleMultiHouse_OffGrid_parse_action(
    action: np.ndarray,
    SmartComSim_Object,
) -> dict:
    """
    Parse a flat OFF-GRID action vector into named components.

    OFF-GRID Action:
        [ U_ac(N_House),
          Gamma(N_PV_Bat + N_Bat),
          E_Load(N_House) ]
    """

    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House  = int(ctx["N_House"])
    N_PV_Bat = int(ctx["N_PV_Bat"])
    N_Bat    = int(ctx["N_Bat"])

    out: dict[str, np.ndarray] = {}
    idx = 0

    # 1) U_ac(N_House)
    out["U_ac"] = action[idx : idx + N_House]
    idx += N_House

    # 2) Gamma(N_PV_Bat + N_Bat)
    n_gamma = N_PV_Bat + N_Bat
    out["Gamma"] = action[idx : idx + n_gamma]
    idx += n_gamma

    # 3) E_Load(N_House)
    out["E_Load"] = action[idx : idx + N_House]
    idx += N_House

    return out

# ============================================================
#  ON-GRID: ACTION PARSER
# ============================================================

def Exp_SingleMultiHouse_OnGrid_parse_action(
    action: np.ndarray,
    SmartComSim_Object,
) -> dict:
    """
    Parse a flat ON-GRID action vector into named components.

    ON-GRID Action:
        [ U_ac(N_House),
          Gamma(N_PV_Bat + N_Bat),
          u_pv(N_PV_Bat + N_PV) ]
    """

    ctx = build_Community_rl_short_context(SmartComSim_Object)

    N_House  = int(ctx["N_House"])
    N_PV_Bat = int(ctx["N_PV_Bat"])
    N_Bat    = int(ctx["N_Bat"])
    N_PV     = int(ctx["N_PV"])

    out: dict[str, np.ndarray] = {}
    idx = 0

    # 1) U_ac(N_House)
    out["U_ac"] = action[idx : idx + N_House]
    idx += N_House

    # 2) Gamma(N_PV_Bat + N_Bat)
    n_gamma = N_PV_Bat + N_Bat
    out["Gamma"] = action[idx : idx + n_gamma]
    idx += n_gamma

    # 3) u_pv(N_PV_Bat + N_PV)
    n_upv = N_PV_Bat + N_PV
    out["u_pv"] = action[idx : idx + n_upv]
    idx += n_upv

    return out

# =====================================================================================
# Reshaping MPC Data for Arbitrary Community RL - Main
# =====================================================================================

def reshape_and_sanitize_Community_rl_inputs(
    ctx,
    E_PV
):
    """
    Reshape initial states & disturbances and correct boundary violations
    for the Single-House Off-Grid MPC, mirroring the MATLAB block:

        - Reshapes:
            T_h_Init, T_wall_Init, T_attic_Init, T_im_Init
            E_bat_Init, U_ac_Init
            T_am, E_PV, T_sol_w, T_sol_r, Q_solar
        - Corrects:
            T_h_Init wrt [T_h_Min, T_h_Max]
            E_bat_Init wrt [E_bat_Min, E_bat_Max]
        - Processes:
            E_l, E_l_Array → DC side (via Eff_Inv)
            Builds E_PV_Reshaped stacked for all PV/PV+Bat houses

    Parameters
    ----------
    ctx : dict
        MPC context built from environment and MPC_Parameters.
    E_PV : array-like, shape (N,)
        PV energy over the MPC horizon (AC-side).
    T_sol_w, T_sol_r, Q_solar : array-like, shape (N,)
        Solar-related disturbances from RC generator.

    Returns
    -------
    reshaped : dict
        Dictionary containing:
            T_h_Init, T_wall_Init, T_attic_Init, T_im_Init
            E_bat_Init, U_ac_Init
            T_am, E_PV, T_sol_w, T_sol_r, Q_solar
            E_Load_Critical_Reshaped, E_l_Reshaped, E_l_Array_DC
            E_PV_Reshaped
    """

    # -------------------------------------------------------------------------
    # Unpack geometry & bounds from ctx
    # -------------------------------------------------------------------------
    N_House   = int(ctx["N_House"])
    N_PV_Bat  = int(ctx["N_PV_Bat"])
    N_Bat     = int(ctx["N_Bat"])
    N_PV      = int(ctx["N_PV"])
    N         = int(ctx["RL_HORIZON_N"])

    T_h_Min   = float(ctx["T_h_Min"])
    T_h_Max   = float(ctx["T_h_Max"])
    E_bat_Min = float(ctx["E_bat_Min"])
    E_bat_Max = float(ctx["E_bat_Max"])
    Eff_Inv   = float(ctx["Eff_Inv"])

    # Initial conditions from ctx
    T_h_Init     = np.array(ctx["T_h_Init"],     dtype=float)
    T_wall_Init  = np.array(ctx["T_wall_Init"],  dtype=float)
    T_attic_Init = np.array(ctx["T_attic_Init"], dtype=float)
    T_im_Init    = np.array(ctx["T_im_Init"],    dtype=float)
    E_bat_Init   = np.array(ctx["E_bat_Init"],   dtype=float)
    U_ac_Init    = np.array(ctx["U_ac_Init"],    dtype=float)

    # Weather & load from ctx
    T_am       = np.array(ctx["T_am"],      dtype=float)
    Ws         = np.array(ctx["Ws"],      dtype=float)
    E_l        = np.array(ctx["E_l"],       dtype=float)
    E_l_Array  = np.array(ctx["E_l_Array"], dtype=float)
    Energy_Price  = np.array(ctx["Energy_Price"], dtype=float)

    E_l_Max        = float(ctx["E_l_Max"])

    # -------------------------------------------------------------------------
    # 1) Reshape initial conditions to column-like vectors
    # -------------------------------------------------------------------------
    T_h_Init     = T_h_Init.reshape(N_House, 1)
    T_wall_Init  = T_wall_Init.reshape(N_House, 1)
    T_attic_Init = T_attic_Init.reshape(N_House, 1)
    T_im_Init    = T_im_Init.reshape(N_House, 1)

    E_bat_Init   = E_bat_Init.reshape(N_PV_Bat + N_Bat, 1)
    U_ac_Init    = U_ac_Init.reshape(N_House, 1)

    # -------------------------------------------------------------------------
    # 2) Reshape disturbances: weather, PV, RC outputs
    # -------------------------------------------------------------------------
    T_am   = T_am.reshape(N, 1)
    Ws     = Ws.reshape(N, 1)
    E_PV   = np.array(E_PV,   dtype=float).reshape(N, 1)
    Energy_Price = np.array(Energy_Price, dtype=float).reshape(N, 1)

    """ # -------------------------------------------------------------------------
    # 3) Correct initial states for boundary violations
    # -------------------------------------------------------------------------
    eps_T = (T_h_Max - T_h_Min) / 10000.0 if T_h_Max > T_h_Min else 1e-6
    eps_E = (E_bat_Max - E_bat_Min) / 10000.0 if E_bat_Max > E_bat_Min else 1e-6

    for ii in range(N_House):
        # House temperature correction
        if T_h_Init[ii, 0] < T_h_Min:
            T_h_Init[ii, 0] = T_h_Min + eps_T

        # House battery SOC correction (only for houses with batteries)
        if ii < (N_PV_Bat + N_Bat):
            if E_bat_Init[ii, 0] > E_bat_Max:
                E_bat_Init[ii, 0] = E_bat_Max - eps_E
            elif E_bat_Init[ii, 0] < E_bat_Min:
                E_bat_Init[ii, 0] = E_bat_Min + eps_E """

    # -------------------------------------------------------------------------
    # 4) Extract E_Load_Critical, reshape & convert loads to DC
    # -------------------------------------------------------------------------
    # E_l_Array assumed shape: (N, n_load_channels, N_House)
    # MATLAB: E_Load_Critical = E_l_Array(:,10,:);
    # Python index 9
    E_Load_Critical = E_l_Array[:, 9, :]                    # (N, N_House)
    E_Load_Critical_Reshaped = E_Load_Critical.reshape(N * N_House, 1)

    # Same flattening for total desired load
    E_l_Reshaped = E_l.reshape(N * N_House, 1)

    # Convert to DC side
    E_Load_Critical_Reshaped = E_Load_Critical_Reshaped / Eff_Inv
    E_l_Reshaped             = E_l_Reshaped / Eff_Inv

    # For per-channel loads: first 9 channels AC, channels >=10 converted
    if E_l_Array.shape[1] > 9:
        E_l_Array_DC = np.concatenate(
            [
                E_l_Array[:, :9, :],          # unchanged
                E_l_Array[:, 9:, :] / Eff_Inv # converted to DC
            ],
            axis=1
        )
    else:
        E_l_Array_DC = E_l_Array.copy()

    E_l_Max = E_l_Max / Eff_Inv

    # -------------------------------------------------------------------------
    # 5) Build PV energy stacked for all PV-bearing houses
    # -------------------------------------------------------------------------
    n_pv_total = N_PV_Bat + N_PV
    if n_pv_total > 0:
        # MATLAB:
        #  E_PV_Reshaped = [];
        #  for ii=1:N_PV_Bat+N_PV
        #      E_PV_Reshaped=[E_PV_Reshaped;E_PV];
        #  end
        E_PV_Reshaped = np.tile(E_PV, (n_pv_total, 1))  # (N * n_pv_total, 1)
    else:
        E_PV_Reshaped = np.zeros((0, 1))

    # -------------------------------------------------------------------------
    # Return everything in a single dictionary
    # -------------------------------------------------------------------------
    reshaped = {
        "T_h_Init": T_h_Init,
        "T_wall_Init": T_wall_Init,
        "T_attic_Init": T_attic_Init,
        "T_im_Init": T_im_Init,
        "E_bat_Init": E_bat_Init,
        "U_ac_Init": U_ac_Init,
        "T_am": T_am,
        "Ws": Ws,
        "E_PV": E_PV,
        "Energy_Price": Energy_Price,
        "E_Load_Critical_Reshaped": E_Load_Critical_Reshaped,
        "E_l_Reshaped": E_l_Reshaped,
        "E_l_Array_DC": E_l_Array_DC,
        "E_PV_Reshaped": E_PV_Reshaped,
        "E_l_Max": E_l_Max
    }

    return reshaped

# ---------------------------------------------------------------
# RL Observation Creators
# ---------------------------------------------------------------

def _aggregate_horizon_series(
    series: np.ndarray, 
    RL_Parameters: dict, 
    mode: str = "mean"
) -> np.ndarray:
    """
    Aggregate a 1D horizon-length array into H_factor blocks of size 
    RL_HORIZON_AVG_N using either mean or sum.

    Parameters
    ----------
    series : np.ndarray
        1D sequence of length RL_HORIZON_N.
    RL_Parameters : dict
        Contains RL_HORIZON_N and RL_HORIZON_AVG_N.
    mode : {"mean", "sum"}
        Aggregation rule:
            "mean" → block average   (use for T_am)
            "sum"  → block summation (use for loads, PV, price)

    Returns
    -------
    np.ndarray of shape (H_factor,)
    """

    series = np.asarray(series, dtype=float).ravel()

    RL_HORIZON_N     = int(RL_Parameters["RL_HORIZON_N"])
    RL_HORIZON_AVG_N = int(RL_Parameters["RL_HORIZON_AVG_N"])

    if RL_HORIZON_AVG_N <= 0:
        raise ValueError("RL_HORIZON_AVG_N must be > 0")

    H_factor = RL_HORIZON_N // RL_HORIZON_AVG_N

    # Trim for safety
    usable_len = H_factor * RL_HORIZON_AVG_N
    series = series[:usable_len]

    blocks = series.reshape(H_factor, RL_HORIZON_AVG_N)

    # Apply appropriate aggregation
    if mode == "mean":
        return blocks.mean(axis=1)
    elif mode == "sum":
        return blocks.sum(axis=1)
    else:
        raise ValueError(f"Invalid mode '{mode}'. Expected 'mean' or 'sum'.")


# ======================================================================
#  OFF-GRID OBSERVATION CREATOR
# ======================================================================

def Exp_SingleMultiHouse_OffGrid_observation_creator(
    ctx: dict,
    reshaped: dict,
    RL_Parameters: dict,
) -> np.ndarray:
    """
    Build OFF-GRID RL observation vector:

        State = [
            Th(N_House),
            E_Bat(N_PV_Bat + N_Bat),
            U_ac_prev(N_House),
            E_l_now(N_House),
            E_cri_now(N_House),
            E_PV_now(1),
            T_am_now(1),
            E_l_future(H_factor * N_House),
            E_cri_future(H_factor * N_House),
            E_PV_future(H_factor),
            T_am_future(H_factor)
        ]

    where H_factor = RL_HORIZON_N / RL_HORIZON_AVG_N.
    """

    # ------------------------------------------------------------
    # Unpack geometry & RL horizon
    # ------------------------------------------------------------
    N_House  = int(ctx["N_House"])
    N_PV_Bat = int(ctx["N_PV_Bat"])
    N_Bat    = int(ctx["N_Bat"])
    N_PV     = int(ctx["N_PV"])

    RL_HORIZON_N = int(RL_Parameters["RL_HORIZON_N"])
    RL_HORIZON_AVG_N = int(RL_Parameters["RL_HORIZON_AVG_N"])

    if RL_HORIZON_AVG_N <= 0:
        raise ValueError("RL_HORIZON_AVG_N must be > 0")

    H_factor = RL_HORIZON_N // RL_HORIZON_AVG_N
    N = RL_HORIZON_N

    # ------------------------------------------------------------
    # 1) Current states from reshaped
    # ------------------------------------------------------------
    # Th: current indoor temperature per house
    Th = np.asarray(reshaped["T_h_Init"], dtype=float).reshape(N_House)

    # Battery SOC for PV+Bat + Bat-only houses
    E_Bat = np.asarray(reshaped["E_bat_Init"], dtype=float).reshape(N_PV_Bat + N_Bat)

    # Previous HVAC action (per house)
    U_ac_prev = np.asarray(reshaped["U_ac_Init"], dtype=float).reshape(N_House)

    # ------------------------------------------------------------
    # 2) Loads (total + critical), now + future
    # ------------------------------------------------------------
    # Total load per house over horizon (DC side), shape (N * N_House, 1) -> (N, N_House)
    E_l_Reshaped = np.asarray(reshaped["E_l_Reshaped"], dtype=float).reshape(N, N_House)

    # Critical load per house over horizon (DC side), shape (N * N_House, 1) -> (N, N_House)
    E_cri_Reshaped = np.asarray(
        reshaped["E_Load_Critical_Reshaped"], dtype=float
    ).reshape(N, N_House)

    # "Now" = first time step in horizon
    E_l_now = E_l_Reshaped[0, :]      # (N_House,)
    E_cri_now = E_cri_Reshaped[0, :]  # (N_House,)

    # Future: aggregated into H_factor blocks per house
    E_l_future_blocks = []
    E_cri_future_blocks = []
    for h in range(N_House):
        E_l_series_h = E_l_Reshaped[:, h]        # (N,)
        E_cri_series_h = E_cri_Reshaped[:, h]    # (N,)

        E_l_future_blocks.append(
            _aggregate_horizon_series(E_l_series_h, RL_Parameters, mode="sum")
        )  # (H_factor,)
        E_cri_future_blocks.append(
            _aggregate_horizon_series(E_cri_series_h, RL_Parameters, mode="sum")
        )  # (H_factor,)

    # Stack into shape (H_factor * N_House,)
    E_l_future = np.concatenate(E_l_future_blocks, axis=0)
    E_cri_future = np.concatenate(E_cri_future_blocks, axis=0)

    # ------------------------------------------------------------
    # 3) PV and ambient temperature (now + future)
    # ------------------------------------------------------------
    # Base PV horizon (single profile), shape (N, 1)
    E_PV_base = np.asarray(reshaped["E_PV"], dtype=float).reshape(N)
    n_pv_total = N_PV_Bat + N_PV

    # Aggregate PV across all PV-bearing houses:
    # E_PV_add[t] = (N_PV + N_PV_Bat) * E_PV_base[t]
    if n_pv_total > 0:
        E_PV_add = n_pv_total * E_PV_base
    else:
        E_PV_add = np.zeros_like(E_PV_base)

    E_PV_now = float(E_PV_add[0])
    E_PV_future = _aggregate_horizon_series(E_PV_add, RL_Parameters, mode="sum")  # (H_factor,)

    # Ambient temperature horizon, shape (N, 1) -> (N,)
    T_am_series = np.asarray(reshaped["T_am"], dtype=float).reshape(N)
    T_am_now = float(T_am_series[0])
    T_am_future = _aggregate_horizon_series(T_am_series, RL_Parameters, mode="mean")  # (H_factor,)

    # ------------------------------------------------------------
    # 4) Concatenate into single observation vector
    # ------------------------------------------------------------
    obs_parts = [
        Th,                                # N_House
        E_Bat,                             # N_PV_Bat + N_Bat
        U_ac_prev,                         # N_House
        E_l_now,                           # N_House
        E_cri_now,                         # N_House
        np.array([E_PV_now]),              # 1
        np.array([T_am_now]),              # 1
        E_l_future,                        # H_factor * N_House
        E_cri_future,                      # H_factor * N_House
        E_PV_future,                       # H_factor
        T_am_future,                       # H_factor
    ]

    Observation = np.concatenate(obs_parts, axis=0).astype(np.float32)
    return Observation

# ======================================================================
#  ON-GRID OBSERVATION CREATOR
# ======================================================================

def Exp_SingleMultiHouse_OnGrid_observation_creator(
    ctx: dict,
    reshaped: dict,
    RL_Parameters: dict,
) -> np.ndarray:
    """
    Build ON-GRID RL observation vector:

        State = [
            Th(N_House),
            E_Bat(N_PV_Bat + N_Bat),
            E_l_now(N_House),
            E_PV_now(1),
            T_am_now(1),
            E_Price_now(1),
            E_l_future(H_factor * N_House),
            E_PV_future(H_factor),
            T_am_future(H_factor),
            E_price_future(H_factor)
        ]
    """

    # ------------------------------------------------------------
    # Unpack geometry & RL horizon
    # ------------------------------------------------------------
    N_House  = int(ctx["N_House"])
    N_PV_Bat = int(ctx["N_PV_Bat"])
    N_Bat    = int(ctx["N_Bat"])
    N_PV     = int(ctx["N_PV"])

    RL_HORIZON_N = int(RL_Parameters["RL_HORIZON_N"])
    RL_HORIZON_AVG_N = int(RL_Parameters["RL_HORIZON_AVG_N"])

    if RL_HORIZON_AVG_N <= 0:
        raise ValueError("RL_HORIZON_AVG_N must be > 0")

    H_factor = RL_HORIZON_N // RL_HORIZON_AVG_N
    N = RL_HORIZON_N

    # ------------------------------------------------------------
    # 1) Current states
    # ------------------------------------------------------------
    Th = np.asarray(reshaped["T_h_Init"], dtype=float).reshape(N_House)
    E_Bat = np.asarray(reshaped["E_bat_Init"], dtype=float).reshape(N_PV_Bat + N_Bat)

    # Total load per house (DC) over horizon
    E_l_Reshaped = np.asarray(reshaped["E_l_Reshaped"], dtype=float).reshape(N, N_House)
    E_l_now = E_l_Reshaped[0, :]  # (N_House,)

    # ------------------------------------------------------------
    # 2) PV, ambient temperature, and price (now + future)
    # ------------------------------------------------------------
    # PV
    E_PV_base = np.asarray(reshaped["E_PV"], dtype=float).reshape(N)
    n_pv_total = N_PV_Bat + N_PV
    if n_pv_total > 0:
        E_PV_add = n_pv_total * E_PV_base
    else:
        E_PV_add = np.zeros_like(E_PV_base)

    E_PV_now = float(E_PV_add[0])
    E_PV_future = _aggregate_horizon_series(E_PV_add, RL_Parameters, mode="sum")  # (H_factor,)

    # Ambient temperature
    T_am_series = np.asarray(reshaped["T_am"], dtype=float).reshape(N)
    T_am_now = float(T_am_series[0])
    T_am_future = _aggregate_horizon_series(T_am_series, RL_Parameters, mode="mean")  # (H_factor,)

    # Energy price
    Energy_Price_series = np.asarray(
        reshaped["Energy_Price"], dtype=float
    ).reshape(N)
    E_Price_now = float(Energy_Price_series[0])
    E_price_future = _aggregate_horizon_series(
        Energy_Price_series, RL_Parameters, mode="mean"
    )  # (H_factor,)

    # ------------------------------------------------------------
    # 3) Future loads (per house)
    # ------------------------------------------------------------
    E_l_future_blocks = []
    for h in range(N_House):
        E_l_series_h = E_l_Reshaped[:, h]  # (N,)
        E_l_future_blocks.append(
            _aggregate_horizon_series(E_l_series_h, RL_Parameters, mode="sum")
        )  # (H_factor,)

    E_l_future = np.concatenate(E_l_future_blocks, axis=0)  # (H_factor * N_House,)

    # ------------------------------------------------------------
    # 4) Concatenate into single observation vector
    # ------------------------------------------------------------
    obs_parts = [
        Th,                                # N_House
        E_Bat,                             # N_PV_Bat + N_Bat
        E_l_now,                           # N_House
        np.array([E_PV_now]),              # 1
        np.array([T_am_now]),              # 1
        np.array([E_Price_now]),           # 1
        E_l_future,                        # H_factor * N_House
        E_PV_future,                       # H_factor
        T_am_future,                       # H_factor
        E_price_future,                    # H_factor
    ]

    Observation = np.concatenate(obs_parts, axis=0).astype(np.float32)
    return Observation


# ---------------------------------------------------------------
# RL Action Creators
# ---------------------------------------------------------------

###############################################################################################################
# OFF-GRID: RL ACTION → SIMULATOR ACTION
###############################################################################################################

def Exp_SingleMultiHouse_OffGrid_action_creator(
    Action_Dict: dict,
    ctx: dict,
    reshaped: dict,
    RL_Parameters: dict,
) -> np.ndarray:
    """
    OFF-GRID RL action → simulator action for FIRST timestep only.

    Output
    ------
    U_k : np.ndarray, shape (1, 13, N_House)
        Simulator control array for one step, matching the layout used in
        Exp_SingleMultiHouse_OffGrid_MPC_Sol_To_Action_Generator.

    Expected Action_Dict keys
    -------------------------
    "U_ac"   : np.ndarray, shape (N_House,), in [-1, 1]
        RL HVAC control per house.
        - abs(U_ac) > 0.5 → AC ON (col 3 = 1), else OFF (col 3 = 0)
        - sign(U_ac) sets heating/cooling mode (col 13):
              U_ac <  0 → cooling  → 0
              U_ac >= 0 → heating  → 1
    "Gamma"  : np.ndarray, shape (N_PV_Bat + N_Bat,)
        RL battery control per battery house.
    "E_Load" : np.ndarray, shape (N_House,)
        RL desired aggregate DC load per house (used by priority stack).
    """

    # Small threshold for battery logic
    epsilon = 1e-8

    # ------------------------------------------------------------------
    # Unpack geometry from ctx
    # ------------------------------------------------------------------
    N_House  = int(ctx["N_House"])
    N_PV_Bat = int(ctx["N_PV_Bat"])
    N_Bat    = int(ctx["N_Bat"])
    N_PV     = int(ctx["N_PV"])

    Nh_bat = N_PV_Bat + N_Bat

    # ------------------------------------------------------------------
    # Unpack RL action components
    # ------------------------------------------------------------------
    U_ac   = np.asarray(Action_Dict["U_ac"],   dtype=float).reshape(N_House)
    Gamma  = np.asarray(Action_Dict["Gamma"],  dtype=float).reshape(Nh_bat)
    E_Load = np.asarray(Action_Dict["E_Load"], dtype=float).reshape(N_House)

    # ------------------------------------------------------------------
    # Initialize control for a single timestep: (1, 13, N_House)
    # ------------------------------------------------------------------
    U_k = np.zeros((1, 13, N_House), dtype=float)

    # ------------------------------------------------------------------
    # 1) AC on/off and mode
    #    - Column 3 (index 2): ON/OFF, based on abs(U_ac) > 0.5
    #    - Column 13 (index 12): heating/cooling mode, based on sign(U_ac)
    #         U_ac <  0 → cooling  → mode = 0
    #         U_ac >= 0 → heating  → mode = 1
    # ------------------------------------------------------------------
    ac_on = (np.abs(U_ac) > 0.5).astype(float)   # (N_House,)
    mode_heating = (U_ac >= 0.0).astype(float)   # 1 = heating, 0 = cooling

    U_k[0, 2, :] = ac_on
    # If you want mode only to matter when AC is ON:
    U_k[0, 12, :] = mode_heating 

    # ------------------------------------------------------------------
    # 2) Battery charge/discharge → cols 1–2 (same sign logic as MPC)
    #    gamma > +eps → discharge = 1
    #    gamma < -eps → charge    = 1
    # ------------------------------------------------------------------
    for j in range(Nh_bat):
        h = j  # battery-equipped houses are at front
        gamma_h = Gamma[j]

        charge    = 0.0
        discharge = 0.0

        if gamma_h > epsilon:
            discharge = 1.0
        elif gamma_h < -epsilon:
            charge = 1.0

        U_k[0, 0, h] = charge
        U_k[0, 1, h] = discharge

    # ------------------------------------------------------------------
    # 3) Priority loads → cols 4–11 via priority stack controller
    #    Use DC-side loads from reshaped["E_l_Array_DC"]:
    #      shape: (N, n_cols_el, N_House)
    #    We use ONLY t = 0 for the RL step.
    # ------------------------------------------------------------------
    E_l_Array = np.array(reshaped["E_l_Array_DC"], dtype=float)
    N_time, n_cols_el, n_house_el = E_l_Array.shape
    assert n_house_el == N_House, "E_l_Array_DC house dimension must match N_House"

    t = 0  # current RL step corresponds to horizon index 0
    for h in range(N_House):
        # Equipment-wise load profile for this time & house
        E_LoadData_th = E_l_Array[t, :, h]   # (n_cols_el,)

        # Scalar control from RL for this house
        E_Control_th = float(E_Load[h])

        U_k_PriorityStack = Exp_priority_stack_controller_mpc_smartcommunity(
            E_LoadData_th,
            E_Control_th,
        )

        # Map up to 8 prioritized loads → cols 4..11 (indices 3..10)
        n_prior = U_k_PriorityStack.shape[0]
        n_prior_to_assign = min(n_prior, 8)
        U_k[0, 3:3 + n_prior_to_assign, h] = U_k_PriorityStack[:n_prior_to_assign]

    # ------------------------------------------------------------------
    # 4) PV: off-grid → full PV usage (no curtailment) → col 12 = 1
    # ------------------------------------------------------------------
    Nh_pv_total = N_PV_Bat + N_PV
    pvbat_idx = np.arange(N_PV_Bat)  # PV+BAT houses at front
    pv_only_start = N_PV_Bat + N_Bat
    pv_only_end   = pv_only_start + N_PV
    pv_only_idx   = np.arange(pv_only_start, pv_only_end)
    pv_global_idx = np.concatenate([pvbat_idx, pv_only_idx])

    U_k[0, 11, pv_global_idx] = 1.0  # and if (E_PV > 0)

    return U_k

###############################################################################################################
# ON-GRID: RL ACTION → SIMULATOR ACTION
###############################################################################################################

def Exp_SingleMultiHouse_OnGrid_action_creator(
    Action_Dict: dict,
    ctx: dict,
    reshaped: dict,
    RL_Parameters: dict,
) -> np.ndarray:
    """
    ON-GRID RL action → simulator action for FIRST timestep only.

    Output
    ------
    U_k : np.ndarray, shape (1, 13, N_House)
        Simulator control array for one step, matching the layout used in
        Exp_SingleMultiHouse_OnGrid_MPC_Sol_To_Action_Generator.

    Expected Action_Dict keys
    -------------------------
    "U_ac" : np.ndarray, shape (N_House,), in [-1, 1]
        RL HVAC control per house.
        - abs(U_ac) > 0.5 → AC ON (col 3 = 1), else OFF (col 3 = 0)
        - sign(U_ac) sets heating/cooling mode (col 13):
              U_ac <  0 → cooling  → 0
              U_ac >= 0 → heating  → 1
    "Gamma": np.ndarray, shape (N_PV_Bat + N_Bat,)
        RL battery control per battery house.
    "u_pv" : np.ndarray, shape (N_PV_Bat + N_PV,)
        RL PV curtailment factor for all PV-bearing houses.
    """

    epsilon = 1e-8

    # ------------------------------------------------------------------
    # Unpack geometry from ctx
    # ------------------------------------------------------------------
    N_House  = int(ctx["N_House"])
    N_PV_Bat = int(ctx["N_PV_Bat"])
    N_Bat    = int(ctx["N_Bat"])
    N_PV     = int(ctx["N_PV"])

    Nh_bat = N_PV_Bat + N_Bat
    Nh_pv  = N_PV_Bat + N_PV

    # ------------------------------------------------------------------
    # Unpack RL action components
    # ------------------------------------------------------------------
    U_ac = np.asarray(Action_Dict["U_ac"], dtype=float).reshape(N_House)
    Gamma = np.asarray(Action_Dict["Gamma"], dtype=float).reshape(Nh_bat)
    u_pv = np.asarray(Action_Dict["u_pv"], dtype=float).reshape(Nh_pv)

    # ------------------------------------------------------------------
    # Initialize control for a single timestep: (1, 13, N_House)
    # ------------------------------------------------------------------
    U_k = np.zeros((1, 13, N_House), dtype=float)

    # ------------------------------------------------------------------
    # 1) AC on/off and mode
    # ------------------------------------------------------------------
    ac_on = (np.abs(U_ac) > 0.5).astype(float)
    mode_heating = (U_ac >= 0.0).astype(float)

    U_k[0, 2, :] = ac_on
    U_k[0, 12, :] = mode_heating 

    # ------------------------------------------------------------------
    # 2) Battery charge/discharge → cols 1–2
    # ------------------------------------------------------------------
    for j in range(Nh_bat):
        h = j
        gamma_h = Gamma[j]

        charge    = 0.0
        discharge = 0.0

        if gamma_h > epsilon:
            discharge = 1.0
        elif gamma_h < -epsilon:
            charge = 1.0

        U_k[0, 0, h] = charge
        U_k[0, 1, h] = discharge

    # ------------------------------------------------------------------
    # 3) Priority loads → cols 4–11 from DC-side E_l_Array_DC
    #    E_l_Array_DC in reshaped: (N, n_cols_el, N_House)
    #    For t = 0, columns 9..16 (0-based 9:17) are prioritized loads.
    # ------------------------------------------------------------------
    E_l_Array = np.array(reshaped["E_l_Array_DC"], dtype=float)
    N_time, n_cols_el, n_house_el = E_l_Array.shape
    assert n_house_el == N_House, "E_l_Array_DC house dimension must match N_House"

    t = 0
    if n_cols_el > 9:
        # (1, 8, N_House)
        prioritized_kwh = E_l_Array[t : t + 1, 9:17, :]
        prioritized_onoff = (prioritized_kwh > 0.0).astype(float)
        # Map → cols 4..11 (indices 3..10)
        U_k[0, 3:11, :] = prioritized_onoff[0, :, :]

    # ------------------------------------------------------------------
    # 4) PV curtailment from u_pv → col 12 (index 11)
    # ------------------------------------------------------------------
    # PV+BAT houses
    for j in range(N_PV_Bat):
        U_k[0, 11, j] = u_pv[j]

    # PV-only houses
    pv_only_start = N_PV_Bat + N_Bat
    pv_only_end   = pv_only_start + N_PV
    for k, h in enumerate(range(pv_only_start, pv_only_end)):
        row = N_PV_Bat + k
        U_k[0, 11, h] = u_pv[row]

    return U_k
