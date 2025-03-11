function X_k_Plant = HEMS_Plant_StateInitialization_Func(simulation_params, community_params, plant_initial_conditions, HEMSPlant_Params)
    % Initialize_States - Initializes system states, disturbances, and control structures.
    %
    % Inputs:
    %   simulation_params       - Struct containing simulation settings.
    %   community_params        - Struct defining the community setup (houses with PV/Battery).
    %   plant_initial_conditions - Struct containing initial temperature & battery energy settings.
    %
    % Outputs:
    %   X_k_Plant - Initialized state matrix.
    %
    % Example:
    %   X_k_Plant = Initialize_States(simulation_params, community_params, plant_initial_conditions);

    % Extract values from input structs
    N_House = community_params.N_PV_Bat + community_params.N_PV + community_params.N_Bat + community_params.N_None;
    N_PV_Bat = community_params.N_PV_Bat;
    N_Bat = community_params.N_Bat;
    T_AC_Base = plant_initial_conditions.T_AC_Base;
    T_House_Variance = plant_initial_conditions.T_House_Variance;
    N1 = plant_initial_conditions.N1;  % Battery capacity multiplier
    Battery_Energy_Max = HEMSPlant_Params.Battery_Energy_Max;
    Simulation_ModeType = simulation_params.Simulation_ModeType;
    
    Battery_Energy_Max_Init = Battery_Energy_Max * N1;

    % --------------------------- Initial Conditions -------------------------- %
    rng(1); % Set random seed for reproducibility

    % Generate initial house temperatures (normal distribution)
    T_House_Initial = T_AC_Base * ones(1, N_House) + (T_House_Variance * randn(1, N_House));

    % Battery Initial Conditions
    E_Bat_Initial = [Battery_Energy_Max_Init * ones(1, N_PV_Bat + N_Bat), zeros(1, N_House - (N_PV_Bat + N_Bat))];

    % ------------------------ Current State X_k_Plant ------------------------ %
    % Define size of state matrix
    if Simulation_ModeType == 0  % Off-Grid
        X_k_Plant = zeros(2, 39, N_House);
    elseif Simulation_ModeType == 1  % On-Grid
        X_k_Plant = zeros(2, 39, N_House);
    else
        error("Invalid Simulation_ModeType. Choose 0 (Off-Grid) or 1 (On-Grid).");
    end

    % Initialize states for each house
    for ii = 1:N_House
        % House Temperatures (X_k_Plant row 1, columns 7-10)
        X_k_Plant(1, 7:10, ii) = [T_House_Initial(ii), T_House_Initial(ii), T_House_Initial(ii), T_House_Initial(ii)];

        % Battery Initial Conditions (X_k_Plant row 1, column 4)
        if ii <= (N_PV_Bat + N_Bat)
            X_k_Plant(1, 4, ii) = E_Bat_Initial(ii);
        end

        % AC On/Off Status Previous (X_k_Plant row 1, column 30)
        X_k_Plant(1, 30, ii) = 1;

        % AC Heating Mode Status Previous (X_k_Plant row 1, column 39)
        X_k_Plant(1, 39, ii) = 0;

        % Prioritized Loads On/Off Status Previous (X_k_Plant row 1, columns 31-38)
        X_k_Plant(1, 31:38, ii) = ones(1, 8);
    end

    fprintf("State Initialization Complete.\n");

end
