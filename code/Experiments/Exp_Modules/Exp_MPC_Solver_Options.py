###############################################################################################################
## Import Desired Packages
###############################################################################################################



###############################################################################################################
## Import Custom Packages
###############################################################################################################


###############################################################################################################
## Experiment MPC Solver Options Module - Custom Constants/Functions
###############################################################################################################

# -----------------------------------------------------------------------------
# Global GUROBI options dictionary
# -----------------------------------------------------------------------------
#
# IMPORTANT:
#   - Users modify this dict directly to tune Gurobi.
#   - For CasADi, Gurobi parameters must live under the 'gurobi' key:
#         {'gurobi': {<Gurobi params>}}
#   - Most options are commented out with explanations; uncomment as needed.
#
#   Example usage with CasADi:
#
#       from casadi import qpsol
#       from Exp_MPC_Solver_Options import GUROBI_OPTIONS_func
#
#       Gurobi_Options_Dict = GUROBI_OPTIONS_func()
#       QP_Solver = qpsol('qp_solver', 'gurobi', QP_Problem, Gurobi_Options_Dict)
#
#   Example usage with gurobipy (direct):
#
#       import gurobipy as gp
#       from Exp_MPC_Solver_Options import GUROBI_OPTIONS_func
#
#       gu_opts = GUROBI_OPTIONS_func()['gurobi']
#       model = gp.Model()
#       for k, v in gu_opts.items():
#           model.setParam(k, v)
#
# -----------------------------------------------------------------------------

GUROBI_OPTIONS_DICT = {
    # CasADi-level options (if any) can go here
    # 'verbose': True,
    'gurobi': {
        # ---------------------------------------------------------------------
        # High-level solution strategy
        # ---------------------------------------------------------------------
        'Threads': 8,
        #   Number of threads (cores) to use.
        #   MATLAB: params.Threads

        'MIPFocus': 2,
        #   High-level emphasis:
        #       0 = Balanced (default)
        #       1 = Feasibility
        #       2 = Optimality
        #       3 = Best bound
        #   MATLAB: params.MIPFocus

        # ---------------------------------------------------------------------
        # Solution improvement / termination
        # ---------------------------------------------------------------------
        'TimeLimit': 2.0,
        #   Hard wall-clock time limit (seconds).
        #   MATLAB: params.TimeLimit

        'MIPGap': 0.01,
        #   Relative MIP gap: (bestPrimal - bestDual) / |bestPrimal|.
        #   0.01 = 1% gap. MATLAB: params.MIPGap

        # 'MIPGapAbs': 0.0,
        #   Absolute gap tolerance. MATLAB: params.MIPGapAbs

        # 'NodeLimit': 10000,
        #   Max number of nodes to explore in the branch-and-bound tree.
        #   MATLAB: params.NodeLimit

        # 'IterationLimit': 100000,
        #   Max simplex/Barrier iterations.
        #   MATLAB: params.IterationLimit

        # 'SolutionLimit': 10000,
        #   Stop after a given number of feasible solutions.
        #   MATLAB: params.SolutionLimit

        # ---------------------------------------------------------------------
        # Memory usage (node files)
        # ---------------------------------------------------------------------
        # 'NodefileStart': 0.5,
        #   Start writing node data to disk (in GB of memory used).
        #   MATLAB: params.NodeFileStart

        # 'NodefileDir': '.',
        #   Directory for node files on disk.
        #   MATLAB: params.NodeFileDir

        # ---------------------------------------------------------------------
        # Root relaxation & method selection
        # ---------------------------------------------------------------------
        # 'NodeMethod': -1,
        #   Algorithm at the root node:
        #       -1 = Automatic (default)
        #        1 = Dual Simplex
        #        2 = Barrier
        #        3 = Concurrent
        #   MATLAB: params.NodeMethod

        # 'Method': 4,
        #   Continuous relaxation algorithm:
        #       -1 = Automatic (default)
        #        0 = Primal Simplex
        #        1 = Dual Simplex
        #        2 = Barrier
        #        3 = Concurrent
        #        4 = Deterministic concurrent
        #   MATLAB: params.Method

        # ---------------------------------------------------------------------
        # Heuristics (usually not changed)
        # ---------------------------------------------------------------------
        # 'SubMIPNodes': 0,
        #   Max nodes for local MIP heuristics.
        #   MATLAB: params.SubMIPNodes

        # 'MinRelNodes': 0,
        #   Minimum explored nodes before running some heuristics.
        #   MATLAB: params.MinRelNodes

        # 'PumpPasses': 0,
        #   Number of feasibility pump passes.
        #   MATLAB: params.PumpPasses

        # 'ZeroObjNodes': 0,
        #   Nodes explored in zero objective heuristics.
        #   MATLAB: params.ZeroObjNodes

        # ---------------------------------------------------------------------
        # Cutting planes
        # ---------------------------------------------------------------------
        'Cuts': 2,
        #   Cutting plane aggressiveness:
        #       -1 = Automatic
        #        0 = None
        #        1 = Conservative
        #        2 = Aggressive
        #   MATLAB: params.Cuts

        # ---------------------------------------------------------------------
        # Presolve
        # ---------------------------------------------------------------------
        'Presolve': 2,
        #   Presolve aggressiveness:
        #       -1 = Automatic
        #        0 = None
        #        1 = Conservative
        #        2 = Aggressive
        #   MATLAB: params.Presolve

        # ---------------------------------------------------------------------
        # Tolerances (usually not changed)
        # ---------------------------------------------------------------------
        # 'FeasibilityTol': 1e-6,
        #   Primal feasibility tolerance.
        #   MATLAB: params.FeasibilityTol

        # 'IntFeasTol': 1e-5,
        #   Integrality tolerance.
        #   MATLAB: params.IntFeasTol

        # 'MarkowitzTol': 0.01,
        #   Markowitz tolerance for factorization.
        #   MATLAB: params.MarkowitzTol

        # 'OptimalityTol': 1e-6,
        #   Dual feasibility tolerance.
        #   MATLAB: params.OptimalityTol

        # ---------------------------------------------------------------------
        # Display / logging
        # ---------------------------------------------------------------------
        'OutputFlag': 1,
        #   1 = Print solver log, 0 = Silent.

        'DisplayInterval': 25,
        #   Interval in seconds between log lines.
        #   MATLAB: params.DisplayInterval

        # 'LogFile': "",
        #   Write detailed log to file if non-empty.
    }
}


def GUROBI_OPTIONS_func():
    """
    Returns the global Gurobi options dictionary.

    Users are expected to modify GUROBI_OPTIONS_DICT above to tune the
    solver. This helper simply returns that dict so other modules can
    import a function rather than a global variable if preferred.
    """
    return GUROBI_OPTIONS_DICT


# -----------------------------------------------------------------------------
# Global IPOPT options dictionary
# -----------------------------------------------------------------------------
#
# IMPORTANT:
#   - Users modify this dict directly to tune IPOPT.
#   - All IPOPT-specific parameters are under the 'ipopt' key, as required
#     by CasADi's nlpsol interface.
#   - Most options are commented out with explanations; uncomment as needed.
#
#   Example usage in your MPC code:
#
#       from casadi import nlpsol
#       from Exp_MPC_Solver_Options import IPOPT_OPTIONS_func
#
#       Ipopt_Options_Dict = IPOPT_OPTIONS_func()
#       NLP_Solver = nlpsol('nlp_solver',
#                           'ipopt',
#                           NLP_Problem,
#                           Ipopt_Options_Dict)
#
# -----------------------------------------------------------------------------

IPOPT_OPTIONS_DICT = {
    # CasADi-level options can be added here if desired, e.g.:
    # 'print_time': False,    # Suppress timing info
    # 'verbose': True,        # CasADi verbosity
    'ipopt': {
        # ---------------------------------------------------------------------
        # Basic stopping criteria
        # ---------------------------------------------------------------------
        'tol': 1e-4,       # Valid range: 0 < tol, Default: 1e-08
        # 's_max': 100,    # Valid range: 0 < s_max, Default: 100
        'max_iter': 3000,  # Valid range: 0 ≤ max_iter, Default: 3000
        # 'max_wall_time': 1e+20,   # 0 < max_wall_time, Default: 1e+20
        # 'max_cpu_time': 1e+20,    # 0 < max_cpu_time, Default: 1e+20

        # 'dual_inf_tol': 1,        # 0 < dual_inf_tol, Default: 1
        # 'constr_viol_tol': 1e-4,  # 0 < constr_viol_tol, Default: 0.0001
        # 'compl_inf_tol': 1e-4,    # 0 < compl_inf_tol, Default: 0.0001
        # 'acceptable_tol': 1e-06,  # 0 < acceptable_tol, Default: 1e-06
        # 'acceptable_iter': 15,    # 0 ≤ acceptable_iter, Default: 15
        # 'acceptable_dual_inf_tol': 1e+10,
        # 'acceptable_constr_viol_tol': 0.01,
        # 'acceptable_compl_inf_tol': 0.01,
        # 'acceptable_obj_change_tol': 1e+20,
        # 'diverging_iterates_tol': 1e+20,

        # ---------------------------------------------------------------------
        # Printing / logging
        # ---------------------------------------------------------------------
        # 'print_level': 5,               # 0 ≤ print_level ≤ 12, Default: 5
        # 'output_file': "",              # Log file name
        # 'file_print_level': 5,          # 0 ≤ file_print_level ≤ 12
        # 'print_user_options': "no",     # yes / no
        # 'print_options_documentation': "no",
        # 'print_timing_statistics': "no",
        # 'print_options_mode': "text",   # text / latex / doxygen
        # 'print_advanced_options': "no",
        # 'print_info_string': "no",
        # 'inf_pr_output': "original",    # internal / original
        # 'print_frequency_iter': 1,      # ≥ 1
        # 'print_frequency_time': 0,      # ≥ 0

        # ---------------------------------------------------------------------
        # NLP bounds and fixed variables
        # ---------------------------------------------------------------------
        # 'nlp_lower_bound_inf': -1e+19,
        # 'nlp_upper_bound_inf': 1e+19,
        # 'fixed_variable_treatment': "make_parameter",
        #     # make_parameter / make_parameter_nodual / make_constraint /
        #     # relax_bounds
        # 'dependency_detector': "none",  # none / mumps / wsmp / ma28
        # 'dependency_detection_with_rhs': "no",
        # 'num_linear_variables': 0,

        # ---------------------------------------------------------------------
        # Derivative and Jacobian / Hessian approximations
        # ---------------------------------------------------------------------
        'jacobian_approximation': "exact",    # exact / finite-difference-values
        'gradient_approximation': "exact",    # exact / finite-difference-values
        # 'findiff_perturbation': 1e-07,
        # 'kappa_d': 1e-05,
        # 'bound_relax_factor': 1e-08,
        # 'honor_original_bounds': "no",
        # 'check_derivatives_for_naninf': "no",
        # 'grad_f_constant': "no",
        # 'jac_c_constant': "no",
        # 'jac_d_constant': "no",
        # 'hessian_constant': "no",

        # ---------------------------------------------------------------------
        # Scaling
        # ---------------------------------------------------------------------
        'nlp_scaling_method': "gradient-based",
        #     none / user-scaling / gradient-based / equilibration-based
        # 'obj_scaling_factor': 1,
        # 'nlp_scaling_max_gradient': 100,
        # 'nlp_scaling_obj_target_gradient': 0,
        # 'nlp_scaling_constr_target_gradient': 0,
        # 'nlp_scaling_min_value': 1e-08,

        # ---------------------------------------------------------------------
        # Bounds handling
        # ---------------------------------------------------------------------
        # 'bound_push': 0.01,
        # 'bound_frac': 0.01,
        # 'slack_bound_push': 0.01,
        # 'slack_bound_frac': 0.01,
        # 'constr_mult_init_max': 1000,
        # 'bound_mult_init_val': 1,
        # 'bound_mult_init_method': "constant",
        # 'least_square_init_primal': "no",
        # 'least_square_init_duals': "no",

        # ---------------------------------------------------------------------
        # Warm start
        # ---------------------------------------------------------------------
        'warm_start_init_point': "yes",
        # 'warm_start_same_structure': "no",
        # 'warm_start_bound_push': 0.001,
        # 'warm_start_bound_frac': 0.001,
        # 'warm_start_slack_bound_push': 0.001,
        # 'warm_start_slack_bound_frac': 0.001,
        # 'warm_start_mult_bound_push': 0.001,
        # 'warm_start_mult_init_max': 1e+06,
        # 'warm_start_entire_iterate': "no",
        # 'warm_start_target_mu': 0,

        # 'option_file_name': "ipopt.opt",
        # 'replace_bounds': "no",
        # 'skip_finalize_solution_call': "no",
        # 'timing_statistics': "no",

        # ---------------------------------------------------------------------
        # Barrier parameter (mu) strategy
        # ---------------------------------------------------------------------
        # 'mu_max_fact': 1000,
        # 'mu_max': 100000,
        # 'mu_min': 1e-11,
        'mu_strategy': "adaptive",  # monotone / adaptive
        # 'mu_oracle': "quality-function",
        # 'fixed_mu_oracle': "average_compl",
        # 'mu_init': 0.1,
        # 'barrier_tol_factor': 10,
        # 'mu_linear_decrease_factor': 0.2,
        # 'mu_superlinear_decrease_power': 1.5,
        # 'mu_allow_fast_monotone_decrease': "yes",
        # 'tau_min': 0.99,
        # 'sigma_max': 100,
        # 'sigma_min': 1e-06,
        # 'quality_function_norm_type': "2-norm-squared",
        # 'quality_function_centrality': "none",
        # 'quality_function_balancing_term': "none",
        # 'quality_function_max_section_steps': 8,
        # 'quality_function_section_sigma_tol': 0.01,
        # 'quality_function_section_qf_tol': 0,

        # ---------------------------------------------------------------------
        # Line-search parameters
        # ---------------------------------------------------------------------
        # 'line_search_method': "filter",   # filter / cg-penalty / penalty
        # 'alpha_red_factor': 0.5,
        'accept_every_trial_step': "yes",  # yes / no (aggressive)
        # 'accept_after_max_steps': -1,
        # 'alpha_for_y': "primal",
        # 'alpha_for_y_tol': 10,
        # 'tiny_step_tol': 2.22045e-15,
        # 'tiny_step_y_tol': 0.01,
        # 'watchdog_shortened_iter_trigger': 10,
        # 'watchdog_trial_iter_max': 3,
        # 'theta_max_fact': 10000,
        # 'theta_min_fact': 0.0001,
        # 'eta_phi': 1e-08,
        # 'delta': 1,
        # 's_phi': 2.3,
        # 's_theta': 1.1,
        # 'gamma_phi': 1e-08,
        # 'gamma_theta': 1e-05,
        # 'alpha_min_frac': 0.05,

        # ---------------------------------------------------------------------
        # Second-order corrections
        # ---------------------------------------------------------------------
        # 'max_soc': 4,
        # 'kappa_soc': 0.99,

        # 'obj_max_inc': 5,
        # 'max_filter_resets': 5,
        # 'filter_reset_trigger': 5,
        # 'corrector_type': "none",
        # 'skip_corr_if_neg_curv': "yes",
        # 'skip_corr_in_monotone_mode': "yes",
        # 'corrector_compl_avrg_red_fact': 1,
        # 'soc_method': 0,
        # 'nu_init': 1e-06,
        # 'nu_inc': 0.0001,
        # 'rho': 0.1,
        # 'kappa_sigma': 1e+10,
        # 'recalc_y': "no",
        # 'recalc_y_feas_tol': 1e-06,
        # 'slack_move': 1.81899e-12,

        # ---------------------------------------------------------------------
        # Linear solver selection
        # ---------------------------------------------------------------------
        'linear_solver': "mumps",  # ma27 / ma57 / ... / mumps / custom
        # 'linear_system_scaling': "mc19",
        # 'hsllib': "libhsl.so",
        # 'pardisolib': "/path/to/libpardiso.so",
        # 'linear_scaling_on_demand': "yes",
        # 'mehrotra_algorithm': "no",
        # 'fast_step_computation': "no",
        # 'min_refinement_steps': 1,
        # 'max_refinement_steps': 10,
        # 'residual_ratio_max': 1e-10,
        # 'residual_ratio_singular': 1e-05,
        # 'residual_improvement_factor': 1,
        # 'neg_curv_test_tol': 0,
        # 'neg_curv_test_reg': "yes",
        # 'max_hessian_perturbation': 1e+20,
        # 'min_hessian_perturbation': 1e-20,
        # 'perturb_inc_fact_first': 100,
        # 'perturb_inc_fact': 8,
        # 'perturb_dec_fact': 0.333333,
        # 'first_hessian_perturbation': 0.0001,
        # 'jacobian_regularization_value': 1e-08,
        # 'jacobian_regularization_exponent': 0.25,
        # 'perturb_always_cd': "no",

        # ---------------------------------------------------------------------
        # Infeasibility handling / restoration
        # ---------------------------------------------------------------------
        # 'expect_infeasible_problem': "no",
        # 'expect_infeasible_problem_ctol': 0.001,
        # 'expect_infeasible_problem_ytol': 1e+08,
        # 'start_with_resto': "no",
        # 'soft_resto_pderror_reduction_factor': 0.9999,
        # 'max_soft_resto_iters': 10,
        # 'required_infeasibility_reduction': 0.9,
        # 'max_resto_iter': 3000000,
        # 'evaluate_orig_obj_at_resto_trial': "yes",
        # 'resto_penalty_parameter': 1000,
        # 'resto_proximity_weight': 1,
        # 'bound_mult_reset_threshold': 1000,
        # 'constr_mult_reset_threshold': 0,
        # 'resto_failure_feasibility_threshold': 0,

        # ---------------------------------------------------------------------
        # Limited-memory Hessian approximation
        # ---------------------------------------------------------------------
        'hessian_approximation': "limited-memory",
        # 'hessian_approximation_space': "nonlinear-variables",
        # 'limited_memory_aug_solver': "sherman-morrison",
        # 'limited_memory_max_history': 6,
        # 'limited_memory_update_type': "bfgs",
        # 'limited_memory_initialization': "scalar1",
        # 'limited_memory_init_val': 1,
        # 'limited_memory_init_val_max': 1e+08,
        # 'limited_memory_init_val_min': 1e-08,
        # 'limited_memory_max_skipping': 2,
        # 'limited_memory_special_for_resto': "no",

        # ---------------------------------------------------------------------
        # Derivative testing (for debugging)
        # ---------------------------------------------------------------------
        # 'derivative_test': "none",   # none / first-order / second-order
        # 'derivative_test_first_index': -2,
        # 'derivative_test_perturbation': 1e-08,
        # 'derivative_test_tol': 0.0001,
        # 'derivative_test_print_all': "no",
        # 'point_perturbation_radius': 10,

        # ---------------------------------------------------------------------
        # MA27 / MA57 / MA77 / MA86 / MA97 / PARDISO / SPRAL / MUMPS options
        # ---------------------------------------------------------------------
        # (Only MUMPS options are partially configured above; the rest are
        # left as references if you ever switch linear solvers.)

        # 'ma27_print_level': 0,
        # 'ma27_pivtol': 1e-08,
        # 'ma27_pivtolmax': 0.0001,
        # ...

        # MUMPS-specific (we keep a few enabled here)
        'mumps_print_level': 0,     # 0 = no print, higher = more verbose
        'mumps_pivtol': 1e-06,
        'mumps_pivtolmax': 0.1,
        'mumps_mem_percent': 200,   # Memory reservation (%)
        'mumps_permuting_scaling': 3,
        'mumps_scaling': 7,
    }
}


def IPOPT_OPTIONS_func():
    """
    Returns the global IPOPT options dictionary.

    Users are expected to modify IPOPT_OPTIONS_DICT above to tune the
    solver. This helper simply returns that dict so that other modules
    can import a function rather than a global variable if preferred.
    """
    return IPOPT_OPTIONS_DICT