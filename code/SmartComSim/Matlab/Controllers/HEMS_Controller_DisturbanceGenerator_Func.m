function W_k_Plant = HEMS_Controller_DisturbanceGenerator_Func(Ws, T_am, GHI, DNI, E_Load_Desired, E_LoadData, Time_Iter)
    % Initialize_Disturbance - Initializes the current disturbance data (weather & load).
    %
    % Inputs:
    %   Ws                 - Wind speed data (vector)
    %   T_am               - Ambient temperature data (vector)
    %   GHI                - Global Horizontal Irradiance (vector)
    %   DNI                - Direct Normal Irradiance (vector)
    %   E_Load_Desired     - Total load per house
    %   E_LoadData         - Full load dataset (time x house x load levels)
    %
    % Outputs:
    %   W_k_Plant          - Struct containing both weather and load data
    %
    % Example:
    %   W_k_Plant = Initialize_Disturbance(Ws, T_am, GHI, DNI, DateTime_Matrix, E_Load_Desired, E_LoadData);

    Time_Iter = Time_Iter + 1;

    % ---------------------- Weather Data ---------------------- %
    Weather_k_Plant = struct();
    Weather_k_Plant.Ws = Ws(Time_Iter);  % First time-step wind speed
    Weather_k_Plant.T_am = T_am(Time_Iter);  % First time-step ambient temperature
    Weather_k_Plant.GHI = GHI(Time_Iter);  % First time-step global horizontal irradiance
    Weather_k_Plant.DNI = DNI(Time_Iter);  % First time-step direct normal irradiance
  
    % ---------------------- Load Data ---------------------- %
    LoadData_k_Plant = struct();
    LoadData_k_Plant.E_Load_Desired = E_Load_Desired(Time_Iter, :);  % First time-step total load per house
    LoadData_k_Plant.E_LoadData = E_LoadData(Time_Iter, :, :);  % First time-step full load data

    % ---------------------- Final Disturbance Struct ---------------------- %
    W_k_Plant = struct();
    W_k_Plant.Weather_k_Plant = Weather_k_Plant;
    W_k_Plant.LoadData_k_Plant = LoadData_k_Plant;

    if (Time_Iter == 1)

        fprintf("Disturbance Initialization Complete.\n");

    end
    
end
