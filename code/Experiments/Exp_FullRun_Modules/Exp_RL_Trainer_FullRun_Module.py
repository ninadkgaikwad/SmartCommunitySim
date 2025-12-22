###############################################################################################################
## RL Training Script (SAC) for SmartCommunitySimulator
###############################################################################################################

import sys
import os
import time
import numpy as np
import pandas as pd

import torch
import torch.nn as nn

import tensorboard

from stable_baselines3 import SAC
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.utils import set_random_seed

###############################################################################################################
## Import Custom Packages
###############################################################################################################

torch.set_num_threads(8)
torch.set_num_interop_threads(2)

# Adding paths to find local modules
paths_to_add = [
    r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Modules",
    r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code",
]

for p in paths_to_add:
    if p not in sys.path and os.path.isdir(p):
        sys.path.append(p)

from Exp_Config_Module import *
from Exp_MPC_RL_Helpers import *
from Exp_RL_Utilities_Module import *  # you can plug callbacks/utilities here if you want

from SmartComSim import SmartCommunity_Simulator as SC_Plant

###############################################################################################################
## RL Trainer Full Run - Main Function
###############################################################################################################

def Exp_RL_Trainer_FullRun(Community_Type, Grid_Type):

    # -------------------- Community Specifications -------------------- #
    COMMUNITY_TYPE = Community_Type      # "House", "Community"
    GRID_TYPE       = Grid_Type  # "Off-Grid", "On-Grid"
    CONTROLLER_TYPE = "RL-Training"  # IMPORTANT: "MPC", "RL-Training", "RL-Testing"

    # These flags control whether MATLAB pre-processors recompute/load weather/load data
    LOAD_DATA_INITIALIZE    = True  # True = Initialize Load Data ; False = Use existing
    WEATHER_DATA_INITIALIZE = True  # True = Initialize Weather Data ; False = Use existing

    # -------------------- RL / SAC Hyperparameters -------------------- #
    RL_SEED           = 42
    TOTAL_TIMESTEPS   = 300_000      # adjust based on compute
    LEARNING_RATE     = 3e-4
    BUFFER_SIZE       = 50_000
    BATCH_SIZE        = 256
    GAMMA             = 0.99
    TAU               = 0.005
    TRAIN_FREQ        = 1            # env steps between gradient updates
    GRADIENT_STEPS    = 1            # gradient steps per train step
    LEARNING_STARTS   = 10_000       # how many steps before learning begins
    ENT_COEF          = "auto"       # SAC temperature
    TARGET_ENTROPY    = "auto"       # can set to a float for fine control

    # Evaluation / checkpoint settings
    EVAL_FREQ_STEPS   = 5_000       # evaluate every N env steps
    SAVE_FREQ_STEPS   = 10_000       # checkpoint every N env steps

    # -------------------- User Controls for SAC Policy Network -------------------- #
    # Actor (policy) hidden layers
    ACTOR_HIDDEN_LAYERS = [256, 256]          # e.g., [128, 128] or [256, 256, 128]

    # Critic (Q-function) hidden layers
    # If you want same as actor, you can set this to None and it will copy ACTOR_HIDDEN_LAYERS
    CRITIC_HIDDEN_LAYERS = [512, 512, 256]    # or None to share with actor

    # Activation function: one of {"relu", "tanh", "leaky_relu", "elu", "silu"}
    POLICY_ACTIVATION = "relu"

    # Results folder (already created inside the env, but we reuse the path for logs)
    RESULTS_ROOT = r"C:\Users\ninad\Dropbox\NinadGaikwad_PhD\Gaikwad_Research\Gaikwad_Research_Work\SmartCommunitySim\code\Experiments\Exp_Results\RL\Trainer"

    ###############################################################################################################
    ## Build Config and Environment Factory
    ###############################################################################################################

    # --------------------------------------------------
    # 1) Build experiment configuration via your helper
    # --------------------------------------------------
    Config = Exp_Configuration_Generator(
        COMMUNITY_TYPE,
        GRID_TYPE,
        CONTROLLER_TYPE,
        LOAD_DATA_INITIALIZE,
        WEATHER_DATA_INITIALIZE,
    )

    # Extract SmartSimCom parameters from Config
    simulation_params                         = Config["simulation_params"]
    community_params                          = Config["community_params"]
    plant_initial_conditions                  = Config["plant_initial_conditions"]
    simulation_period                         = Config["simulation_period"]
    plant_dynamic_params                      = Config["plant_dynamic_params"]
    data_paths                                = Config["data_paths"]
    result_filefolder_paths                   = Config["result_filefolder_paths"]
    simulation_ObservationActionSpace_Functions = Config["simulation_ObservationActionSpace_Functions"]
    simulation_RewardTerminateTruncate_Functions = Config["simulation_RewardTerminateTruncate_Functions"]

    # RL log directories
    rl_run_name        = f"RL_SAC_{COMMUNITY_TYPE}_{GRID_TYPE}"
    rl_log_root        = os.path.join(RESULTS_ROOT, "RL", rl_run_name)
    tensorboard_logdir = os.path.join(rl_log_root, "tb")
    checkpoint_dir     = os.path.join(rl_log_root, "checkpoints")
    best_model_dir     = os.path.join(rl_log_root, "best_model")
    eval_log_dir       = os.path.join(rl_log_root, "eval_logs")

    for d in [rl_log_root, tensorboard_logdir, checkpoint_dir, best_model_dir, eval_log_dir]:
        os.makedirs(d, exist_ok=True)

    ###############################################################################################################
    ## Create VecEnv (single environment) and set seeds
    ###############################################################################################################

    set_random_seed(RL_SEED)

    # Single-environment DummyVecEnv (because MATLAB engine is not vectorized)
    train_env = DummyVecEnv([make_env_fn(simulation_params,
                                            community_params,
                                            plant_initial_conditions,
                                            simulation_period,
                                            plant_dynamic_params,
                                            data_paths,
                                            result_filefolder_paths,
                                            simulation_ObservationActionSpace_Functions,
                                            simulation_RewardTerminateTruncate_Functions,
                                            rl_log_root,
                                        )])
    train_env = VecMonitor(train_env, filename=os.path.join(rl_log_root, "vec_monitor.csv"))

    # Separate evaluation environment (fresh instance, same config)
    eval_env = DummyVecEnv([make_env_fn(simulation_params,
                                        community_params,
                                        plant_initial_conditions,
                                        simulation_period,
                                        plant_dynamic_params,
                                        data_paths,
                                        result_filefolder_paths,
                                        simulation_ObservationActionSpace_Functions,
                                        simulation_RewardTerminateTruncate_Functions,
                                        rl_log_root,
                                        )])
    eval_env = VecMonitor(eval_env, filename=os.path.join(eval_log_dir, "vec_monitor_eval.csv"))

    ###############################################################################################################
    ## Define Callbacks: Checkpoints & Evaluation
    ###############################################################################################################

    checkpoint_callback = CheckpointCallback(
        save_freq=SAVE_FREQ_STEPS,
        save_path=checkpoint_dir,
        name_prefix="sac_hems",
        save_replay_buffer=True,
        save_vecnormalize=True,
    )

    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=best_model_dir,
        log_path=eval_log_dir,
        eval_freq=EVAL_FREQ_STEPS,
        deterministic=True,
        render=False,
    )

    callback_list = [checkpoint_callback, eval_callback]

    ###############################################################################################################
    ## Build policy_kwargs dynamically from user controls
    ###############################################################################################################

    policy_kwargs = build_policy_kwargs(
        actor_layers=ACTOR_HIDDEN_LAYERS,
        critic_layers=CRITIC_HIDDEN_LAYERS,
        activation_name=POLICY_ACTIVATION,
    )

    ###############################################################################################################
    ## Create SAC Model
    ###############################################################################################################

    model = SAC(
        policy="MlpPolicy",
        env=train_env,
        learning_rate=LEARNING_RATE,
        buffer_size=BUFFER_SIZE,
        batch_size=BATCH_SIZE,
        gamma=GAMMA,
        tau=TAU,
        train_freq=TRAIN_FREQ,
        gradient_steps=GRADIENT_STEPS,
        learning_starts=LEARNING_STARTS,
        ent_coef=ENT_COEF,
        target_entropy=TARGET_ENTROPY,
        verbose=1,
        seed=RL_SEED,
        tensorboard_log=tensorboard_logdir,
        # USE THE CUSTOM ARCHITECTURE
        policy_kwargs=policy_kwargs
    )

    print("\n===================== SAC TRAINING SETUP =====================")
    print(f"Community Type      : {COMMUNITY_TYPE}")
    print(f"Grid Type           : {GRID_TYPE}")
    print(f"Controller Type     : {CONTROLLER_TYPE}")
    print(f"Total Timesteps     : {TOTAL_TIMESTEPS}")
    print(f"Results Root        : {RESULTS_ROOT}")
    print(f"RL Log Root         : {rl_log_root}")
    print("==============================================================\n")

    ###############################################################################################################
    ## Train the SAC Agent
    ###############################################################################################################

    start_time = time.time()

    model.learn(
        total_timesteps=TOTAL_TIMESTEPS,
        callback=callback_list,
        log_interval=10,
        progress_bar=True,
    )

    end_time = time.time()
    train_time = end_time - start_time

    print("\n===================== SAC TRAINING COMPLETE ====================")
    print(f"Total training time: {train_time:.2f} seconds")
    print("===============================================================\n")

    ###############################################################################################################
    ## Save Final Model
    ###############################################################################################################

    final_model_path = os.path.join(rl_log_root, "sac_hems_final")
    model.save(final_model_path)
    print(f"Final SAC model saved to: {final_model_path}")

    ###############################################################################################################
    ## Cleanup
    ###############################################################################################################

    train_env.close()
    eval_env.close()

    print("Environments closed. RL training script completed.")


    # tensorboard --logdir "C:\Users\ninad\Dropbox\...\SmartComSim_Results\RL\RL_SAC_House_Off-Grid\tb"

    return train_time, TOTAL_TIMESTEPS

