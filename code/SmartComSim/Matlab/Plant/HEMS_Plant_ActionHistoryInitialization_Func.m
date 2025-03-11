function U_k_History = HEMS_Plant_ActionHistoryInitialization_Func(simulation_params, community_params)
    % Initialize_ControllerHistory - Initializes the control action history matrix.
    %
    % Inputs:
    %   simulation_params  - Struct containing simulation settings.
    %   community_params   - Struct defining the community setup (houses with PV/Battery).
    %
    % Outputs:
    %   U_k_History - Initialized control action history matrix.
    %
    % Example:
    %   U_k_History = Initialize_ControllerHistory(simulation_params, community_params);

    % Extract number of houses from community parameters
    N_House = community_params.N_PV_Bat + community_params.N_PV + community_params.N_Bat + community_params.N_None;
    
    % ------------------ Initializing Controller History ------------------ %
    % Control variables:
    % - 1:11 → General control actions
    % - 12 → Control of PV
    % - 13 → Control of AC Heating Mode

    % Define size of control action history matrix
    if simulation_params.Simulation_ModeType == 0  % Off-Grid
        U_k_History = zeros(1, 13, N_House);
    elseif simulation_params.Simulation_ModeType == 1  % On-Grid
        U_k_History = zeros(1, 13, N_House);
    else
        error("Invalid Simulation_ModeType. Choose 0 (Off-Grid) or 1 (On-Grid).");
    end

    fprintf("Controller History Initialization Complete.\n");

end
