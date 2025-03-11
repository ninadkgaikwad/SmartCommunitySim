function [] = SmartCommunity_PerformanceComputer_Func(X_k_Plant_History, U_k_History, E_LoadData, E_Load_Desired, HEMSWeatherData_Output, HEMSPlant_Params, Community_Params, result_filefolder_paths, Simulation_Params)
    %SMARTCOMMUNITY_PERFORMANCECOMPUTER_FUNC Computes performance metrics for the Smart Community simulation.
    %
    % This function evaluates the system's performance based on historical state data, 
    % control actions, and energy parameters. It dynamically calls different performance 
    % computation functions based on the simulation mode (On-Grid or Off-Grid).
    %
    % INPUTS:
    %   - X_k_Plant_History      : History of plant states over time
    %   - U_k_History            : History of control inputs applied to the system
    %   - E_LoadData             : Load energy data (adjusted for efficiency)
    %   - E_Load_Desired         : Desired load energy values (adjusted for efficiency)
    %   - HEMSWeatherData_Output : Weather data used in simulation
    %   - HEMSPlant_Params       : Parameters related to the Home Energy Management System (HEMS)
    %   - Community_Params       : Parameters defining community-level simulation settings
    %   - result_filefolder_paths: Struct containing paths for saving output files
    %   - Simulation_ModeType    : Mode selection (0 = Off-Grid, 1 = On-Grid)
    %
    % OUTPUT:
    %   - No direct output; the function saves a .mat file containing the computed 
    %     performance metrics in the specified folder.

    % Initialize an empty struct to store performance computation data
    HEMS_PerformanceComputation = struct();

    % Assigning relevant variables to the struct
    HEMS_PerformanceComputation.X_k_Plant_History = X_k_Plant_History;
    HEMS_PerformanceComputation.U_k_History = U_k_History; 
    HEMS_PerformanceComputation.E_LoadData = E_LoadData(:, 10:end, :) / HEMSPlant_Params.Eff_Inv;
    HEMS_PerformanceComputation.E_Load_Desired = E_Load_Desired / HEMSPlant_Params.Eff_Inv;
    HEMS_PerformanceComputation.HEMSWeatherData_Output = HEMSWeatherData_Output;
    HEMS_PerformanceComputation.HEMSPlant_Params = HEMSPlant_Params;
    HEMS_PerformanceComputation.Community_Params = Community_Params;

    Simulation_ModeType = Simulation_Params.Simulation_ModeType;

    % Determine performance computation function based on simulation mode
    if Simulation_ModeType == 0  % Off-Grid Mode
        Plant_Performance = HEMS_Plant_Performance_Computer_OffGrid(HEMS_PerformanceComputation);
    elseif Simulation_ModeType == 1  % On-Grid Mode
        Plant_Performance = HEMS_Plant_Performance_Computer_OnGrid(HEMS_PerformanceComputation);
    else
        error('Invalid Simulation_ModeType. Use 0 for Off-Grid or 1 for On-Grid.');
    end

    % Construct the filename for saving performance data
    SimulationPerformanceData_FileName = fullfile(result_filefolder_paths.Results_FolderPath, 'PerformanceData', strcat(result_filefolder_paths.SimulationPerformanceData_FileName,'.mat'));

    % Save the computed performance data
    save(SimulationPerformanceData_FileName, 'Plant_Performance');

    % Display a confirmation message
    fprintf('Performance data saved successfully to: %s\n', SimulationPerformanceData_FileName);

end
