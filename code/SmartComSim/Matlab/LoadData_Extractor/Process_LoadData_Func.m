function [E_LoadData, E_Load_Desired, E_Load_Desired_Array] = Process_LoadData_Func(simulation_params, data_paths, result_filefolder_paths, HEMSWeatherData_Output, community_params)
    % Process_LoadData - Handles load data extraction or loading for the simulation.
    %
    % Inputs:
    %   simulation_params        - Struct containing simulation configuration
    %   data_paths               - Struct containing file paths for load data
    %   result_filefolder_paths  - Struct containing file and folder names for output storage
    %   HEMSWeatherData_Input    - Struct containing weather data information
    %   community_params         - Struct defining the community setup (houses with PV/Battery)
    %
    % Outputs:
    %   E_LoadData   - Processed Load Data including priority levels
    %   E_Load_Desired - Desired total energy load per house
    
    % Extract input values
    LoadData_FileName = result_filefolder_paths.LoadData_FileName;
    LoadDataFolder_Path = data_paths.LoadDataFolder_Path;
    N_House_Vector = [community_params.N_PV_Bat, community_params.N_Bat, community_params.N_PV, community_params.N_None];
    SimulationType = simulation_params.SimulationType;
    
    Results_FolderPath = result_filefolder_paths.Results_FolderPath;

    LoadData_FilePath = fullfile(Results_FolderPath, 'LoadData', LoadData_FileName);

    % ------------------ Handling Load Data Extraction or Loading ------------------ %
    if simulation_params.LoadDataType == 1
        % No pre-existing load data file -> Extract data using function
        fprintf('Extracting Load Data...\n');
        PecanStreet_Data_Output = PecanStreet_Data_Extractor_Updated(HEMSWeatherData_Output, simulation_params, LoadDataFolder_Path, N_House_Vector, SimulationType, LoadData_FilePath);
    elseif simulation_params.LoadDataType == 2
        % Load existing load data file
        matFile = strcat(LoadData_FilePath, '.mat');
        if isfile(matFile)
            fprintf('Loading Load Data from %s...\n', matFile);
            load(matFile);
        else
            error('Load data file not found: %s', matFile);
        end
    else
        error('Invalid LoadDataType. Choose 1 (extract) or 2 (load).');
    end
    
    % ------------------------ Process Extracted Load Data ------------------------ %
    % Getting Renewable Source Data
    SolarGen_Data = PecanStreet_Data_Output(:, 5:6, :); % Extract columns for solar generation
    
    % Battery Charge/Discharge Data
    Battery_ChargerDischarge_Data = PecanStreet_Data_Output(:, 7, :);
    
    % EV Charging Data
    EVCharging_Data = PecanStreet_Data_Output(:, 8:9, :);
    
    % Load Data
    E_LoadData = PecanStreet_Data_Output(:, :, :);

    % Ensuring No Negative Load Values
    % E_LoadData(E_LoadData(:, 10:end, :) < 0) = 0;
    E_LoadData(:, 10:end,:) = max(E_LoadData(:, 10:end,:), 0);

    % ------------------------ Creating Priority Load Data ------------------------ %
    % Creating 8-Level Priority Load Data
    E_Load_P1 = sum(E_LoadData(:, 10:21, :), 2); % Priority Level 1
    E_Load_P2 = sum(E_LoadData(:, 22:26, :), 2); % Priority Level 2
    E_Load_P3 = sum(E_LoadData(:, 27:29, :), 2); % Priority Level 3
    E_Load_P4 = sum(E_LoadData(:, 30:36, :), 2); % Priority Level 4
    E_Load_P5 = sum(E_LoadData(:, 37:42, :), 2); % Priority Level 5
    E_Load_P6 = sum(E_LoadData(:, 43:48, :), 2); % Priority Level 6
    E_Load_P7 = sum(E_LoadData(:, 49:51, :), 2); % Priority Level 7
    E_Load_P8 = sum(E_LoadData(:, 52:57, :), 2); % Priority Level 8

    % Append Priority Load Data to Main Load Data
    E_LoadData = [E_LoadData(:, 1:9, :) ...
                  E_Load_P1, E_Load_P2, E_Load_P3, E_Load_P4, ...
                  E_Load_P5, E_Load_P6, E_Load_P7, E_Load_P8];

    % ------------------------ Summing All Loads per House ------------------------ %
    E_Load_Desired_Array = sum(E_LoadData(:, 10:end, :), 2);

    % Initialize the desired load per house
    N_House = sum(N_House_Vector);
    E_Load_Desired = zeros(size(E_Load_Desired_Array, 1), N_House);

    for ii = 1:N_House
        E_Load_Desired(:, ii) = E_Load_Desired_Array(:, :, ii);
    end

    fprintf('Load Data Processing Complete.\n');

end
