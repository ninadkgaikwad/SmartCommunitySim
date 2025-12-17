###############################################################################################################
## Import Desired Packages
###############################################################################################################


###############################################################################################################
## Import Custom Packages
###############################################################################################################


###############################################################################################################
## Experiment RL Configuration Module - Custom Constants
###############################################################################################################

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