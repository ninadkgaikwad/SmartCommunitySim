function [] = SmartCommunity_FigurePlotter_Func(X_k_Plant_History, U_k_History, E_LoadData, E_Load_Desired, HEMSWeatherData_Output, HEMSPlant_Params, Community_Params, Simulation_Params, result_filefolder_paths)
    %SMARTCOMMUNITY_FIGUREPLOTTER_FUNC Saves simulation data for Smart Community simulations.
    %
    % This function stores relevant simulation variables in a structured format and 
    % saves them to a .mat file for later analysis.
    %
    % INPUTS:
    %   - X_k_Plant_History      : History of plant states over time
    %   - U_k_History            : History of control inputs applied to the system
    %   - E_LoadData             : Load energy data (adjusted for efficiency)
    %   - E_Load_Desired         : Desired load energy values (adjusted for efficiency)
    %   - HEMSWeatherData_Output : Weather data used in simulation
    %   - HEMSPlant_Params       : Parameters related to the Home Energy Management System (HEMS)
    %   - Community_Params       : Parameters defining community-level simulation settings
    %   - Simulation_Params      : General parameters related to the simulation
    %   - result_filefolder_paths: Struct containing paths for saving output files
    %
    % OUTPUT:
    %   - No direct output; the function saves a .mat file containing the structured 
    %     simulation data in the specified folder.
    
    % Extract the image folder name from the provided file paths
    ImageFolder_Name = result_filefolder_paths.ImageFolder_Name;

    % Define the path for saving baseline output images
    Baseline_Output_Images_Path = fullfile(result_filefolder_paths.Results_FolderPath, 'Plots', ImageFolder_Name);

    % Initialize an empty struct to store figure plotting input data
    HEMS_Plant_FigurePlotter_Input = struct();

    % Assigning relevant variables to the struct
    HEMS_Plant_FigurePlotter_Input.X_k_Plant_History = X_k_Plant_History;
    HEMS_Plant_FigurePlotter_Input.U_k_History = U_k_History; 
    HEMS_Plant_FigurePlotter_Input.E_LoadData = E_LoadData(:, 10:end, :) / HEMSPlant_Params.Eff_Inv;
    HEMS_Plant_FigurePlotter_Input.E_Load_Desired = E_Load_Desired / HEMSPlant_Params.Eff_Inv;
    HEMS_Plant_FigurePlotter_Input.HEMSWeatherData_Output = HEMSWeatherData_Output;
    HEMS_Plant_FigurePlotter_Input.HEMSPlant_Params = HEMSPlant_Params;
    HEMS_Plant_FigurePlotter_Input.Community_Params = Community_Params;
    HEMS_Plant_FigurePlotter_Input.Baseline_Output_Images_Path = Baseline_Output_Images_Path;
    HEMS_Plant_FigurePlotter_Input.Single_House_Plotting_Index = Simulation_Params.Single_House_Plotting_Index;
    HEMS_Plant_FigurePlotter_Input.Simulation_Params = Simulation_Params;

    Simulation_ModeType = Simulation_Params.Simulation_ModeType;   

    % Plotting using External Function
    if (Simulation_ModeType == 0) % Off-Grid Mode
        
        HEMS_Plant_FigurePlotter_OffGrid(HEMS_Plant_FigurePlotter_Input);

    elseif (Simulation_ModeType == 1) % On-Grid Mode

        HEMS_Plant_FigurePlotter_OnGrid(HEMS_Plant_FigurePlotter_Input);

    end

    % Display a confirmation message
    fprintf('Simulation Plots saved successfully to: %s\n', fullfile(result_filefolder_paths.Results_FolderPath, 'Plots'));
    
end