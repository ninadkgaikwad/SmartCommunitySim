function [HEMSWeatherData_Output, HEMSWeatherData_Input] = Process_WeatherData_Func(simulation_params, simulation_period, data_paths, result_filefolder_paths)
    % Process_WeatherData - Handles weather data extraction or loading for the simulation.
    %
    % Inputs:
    %   simulation_params        - Struct containing simulation configuration
    %   simulation_period        - Struct containing start/end times
    %   data_paths               - Struct containing file paths for weather data
    %   result_filefolder_paths  - Struct containing file and folder names for output storage
    %
    % Example:
    %   Process_WeatherData(simulation_params, simulation_period, data_paths, result_filefolder_paths)

    % ------------------ Creating Simulation_Params Struct ------------------ %
    Simulation_Params = struct();
    Simulation_Params.FileRes = simulation_params.FileRes;
    Simulation_Params.Simulation_StepSize = simulation_params.Simulation_StepSize;  % Convert minutes to hours
    Simulation_Params.StepSize = simulation_params.StepSize;  % Convert minutes to seconds
    Simulation_Params.SmartCommunity_ControllerType = simulation_params.SmartCommunity_ControllerType;
    Simulation_Params.OffGrid_Simulation_ModeType = simulation_params.OffGrid_Simulation_ModeType;

    % ------------------ Creating HEMSWeatherData_Input Struct ------------------ %
    HEMSWeatherData_Input = struct();
    HEMSWeatherData_Input.WeatherDataFile_Path = data_paths.WeatherDataFile_Path;
    HEMSWeatherData_Input.StartYear = simulation_period.StartYear;
    HEMSWeatherData_Input.StartMonth = simulation_period.StartMonth;
    HEMSWeatherData_Input.StartDay = simulation_period.StartDay;
    HEMSWeatherData_Input.StartTime = simulation_period.StartTime;
    HEMSWeatherData_Input.EndYear = simulation_period.EndYear;
    HEMSWeatherData_Input.EndMonth = simulation_period.EndMonth;
    HEMSWeatherData_Input.EndDay = simulation_period.EndDay;
    HEMSWeatherData_Input.EndTime = simulation_period.EndTime;

    % Get the Weather Data File Name
    WeatherData_FileName = result_filefolder_paths.WeatherData_FileName;

    WeatherData_FilePath = fullfile(result_filefolder_paths.Results_FolderPath, 'WeatherData', WeatherData_FileName);

    % ------------------ Handling Weather Data Extraction or Loading ------------------ %
    if simulation_params.WeatherDataType == 1
        % No pre-existing weather data file -> Extract data using function
        fprintf('Extracting Weather Data...\n');
        HEMSWeatherData_Output = WeatherData_Extractor(HEMSWeatherData_Input, Simulation_Params, WeatherData_FilePath);
    elseif simulation_params.WeatherDataType == 2
        % Load existing weather data file
        matFile = strcat(WeatherData_FilePath, '.mat');
        if isfile(matFile)
            fprintf('Loading Weather Data from %s...\n', matFile);
            load(matFile);
        else
            error('Weather data file not found: %s', matFile);
        end
    else
        error('Invalid WeatherDataType. Choose 1 (extract) or 2 (load).');
    end

    fprintf('Weather Data Processing Complete.\n');

end
