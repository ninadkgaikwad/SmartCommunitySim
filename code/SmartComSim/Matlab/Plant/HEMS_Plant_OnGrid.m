function [X_k_Plus_Plant] = HEMS_Plant_OnGrid(X_k_Plant,W_k_Plant,U_k,HEMSPlant_Params,HEMSHouse_Params,Community_Params,Simulation_Params)
% some changes by shishir
% Author: Ninad Kiran Gaikwad  
% Date: Mar/20/2021
% Description: HEMS_Plant - Plant Dynamics

%% HEMS_Plant - Plant Dynamics

%% Getting desired Data from Input - Structs
% From W_k_Plant
Weather_k_Plant=W_k_Plant.Weather_k_Plant;
LoadData_k_Plant=W_k_Plant.LoadData_k_Plant;

GHI=Weather_k_Plant.GHI;
DNI=Weather_k_Plant.DNI;
T_am=Weather_k_Plant.T_am;
Ws=Weather_k_Plant.Ws;
DateTime_Matrix(1,1:4)=Weather_k_Plant.DateTime_Matrix;

E_Load_Desired=LoadData_k_Plant.E_Load_Desired;
E_LoadData=LoadData_k_Plant.E_LoadData;

% From HEMSPlant_Params
T_AC_Base=HEMSPlant_Params.T_AC_Base;
T_AC_DeadBand=HEMSPlant_Params.T_AC_DeadBand;
ACLoad_StartUp_Power=HEMSPlant_Params.ACLoad_StartUp_Power;

PV_TotlaModules_Num=HEMSPlant_Params.PV_TotlaModules_Num;
PV_RatedPower=HEMSPlant_Params.PV_RatedPower;
PV_TempCoeff=HEMSPlant_Params.PV_TempCoeff;
GHI_Std=HEMSPlant_Params.GHI_Std;
Temp_Std=HEMSPlant_Params.Temp_Std;
Eff_Inv=HEMSPlant_Params.Eff_Inv;
Uo=HEMSPlant_Params.Uo;
U1=HEMSPlant_Params.U1;

Eff_Charging_Battery=HEMSPlant_Params.Eff_Charging_Battery;
Eff_Discharging_Battery=HEMSPlant_Params.Eff_Discharging_Battery;

MaxRate_Charging=HEMSPlant_Params.MaxRate_Charging;
MaxRate_Discharging=HEMSPlant_Params.MaxRate_Discharging;
Battery_Energy_Max=HEMSPlant_Params.Battery_Energy_Max;
Battery_Energy_Min=HEMSPlant_Params.Battery_Energy_Min;
MaxRate_Discharging_StartUp=HEMSPlant_Params.MaxRate_Discharging_StartUp;

E_AC=HEMSPlant_Params.E_AC;

% From Community_Params
N_House=double(Community_Params.N_House);
N_PV_Bat=double(Community_Params.N_PV_Bat);
N_Bat=double(Community_Params.N_Bat);
N_PV=double(Community_Params.N_PV);
N_None=double(Community_Params.N_None);   

% From Simulation_Params
Simulation_StepSize=Simulation_Params.Simulation_StepSize;

%% Initializing X_k_Plus_Plant

X_k_Plus_Plant=X_k_Plant;

%% Step 1: Computing PV Energy Potential

% Creating Input for PV Energy Available Generator
PVEnergy_Generator_Input.PV_TotlaModules_Num=PV_TotlaModules_Num;
PVEnergy_Generator_Input.PV_RatedPower=PV_RatedPower;
PVEnergy_Generator_Input.PV_TempCoeff=PV_TempCoeff;

PVEnergy_Generator_Input.T_am=T_am;
PVEnergy_Generator_Input.GHI=GHI;
PVEnergy_Generator_Input.Ws=Ws;

PVEnergy_Generator_Input.Uo=Uo;
PVEnergy_Generator_Input.U1=U1;

PVEnergy_Generator_Input.Temp_Std=Temp_Std;
PVEnergy_Generator_Input.GHI_Std=GHI_Std;

PVEnergy_Generator_Input.Simulation_StepSize=Simulation_StepSize;

% Computing Total Available PV Energy
[PVEnergy_Available] = HEMS_PVEnergy_Available_Generator(PVEnergy_Generator_Input);

Total_PVEnergy_Available = (N_PV_Bat+N_PV)*PVEnergy_Available;

%% Step 2: Computing - PV Available (1), PV Used (2), PV Unused (3) for Houses with PV 

for jj=1:N_House

    % Computing PV Energy Available
    if((jj<=N_PV_Bat)||((jj>(N_PV_Bat+N_Bat))&&(jj<=(N_PV_Bat+N_Bat+N_PV)))) % For PV installed Houses

        % PV Available - On AC Side
        X_k_Plus_Plant(1,1,jj) = PVEnergy_Available*Eff_Inv;

        % PV Used  - On AC Side
        X_k_Plus_Plant(1,2,jj) = U_k(1,12,jj) * PVEnergy_Available*Eff_Inv;

        % PV Unused  - On AC Side
        X_k_Plus_Plant(1,3,jj) = X_k_Plant(1,1,jj) - X_k_Plant(1,2,jj);

    end

end 

%% Step 3: Computing Energy Consumed by All Loads (11 - 20) for All Houses

% Computing Load on the DC Side
E_Load_Desired_DC=E_Load_Desired/Eff_Inv;
E_LoadData_DC=[E_LoadData(1,1:9,:) E_LoadData(1,9+1:end,:)/Eff_Inv];

% Computing Total energy desired by other loads (Not ACs) - On AC Side
for jj=1:N_House % For Each House
    
    OtherLoad_Energy_Desired(1,1,jj)=U_k(1,4:11,jj)*E_LoadData(1,9+1:end,jj)';

    % OtherLoad_Energy_Desired(1,1,jj)=U_k(1,4:11,jj)*E_LoadData_DC(1,9+1:end,jj)'; % On DC Side
    
end

% Energy Consumed by AC and Other Loads - On AC Side
X_k_Plus_Plant(1,11:20,:) = [(E_AC)*U_k(1,3,:)...
                              OtherLoad_Energy_Desired...
                              U_k(1,4:11,:).*E_LoadData(1,9+1:end,:)]; 

% Energy Consumed by AC and Other Loads - On DC Side
% X_k_Plus_Plant(1,11:20,:) = [(E_AC/Eff_Inv)*U_k(1,3,:) OtherLoad_Energy_Desired U_k(1,4:11,:).*E_LoadData_DC(1,9+1:end,:)]; 

%% Step 4: Computing ON-OFF Status of ALL Loads (21 - 38) for All Houses

% AC and Other Loads Current On-Off Status 
X_k_Plus_Plant(1,21:29,:) = U_k(1,3:11,:);

% AC and Other Loads Previous On-Off Status (None On)
X_k_Plus_Plant(2,30:38,:) = X_k_Plus_Plant(1,21:29,:); 

%% Step 5: Computing House Thermal Dynamics (7 - 10) for All Houses

% Setting up HEMSWeatherData_Output1
HEMSWeatherData_Output1.Ws=Ws;
HEMSWeatherData_Output1.T_am=T_am;
HEMSWeatherData_Output1.GHI=GHI;
HEMSWeatherData_Output1.DNI=DNI;
HEMSWeatherData_Output1.DateTime_Matrix=DateTime_Matrix;

% House Thermal Dynamics Simulation

for jj=1:N_House % For each House in Smart Comuunity       

    % Creating 
    HEMSHouse_States=[]; % Initialization

    % Setting up House States initial conditions for the first time

    HEMSHouse_States.T_wall1=X_k_Plant(1,8,jj);
    HEMSHouse_States.T_ave1=X_k_Plant(1,7,jj);
    HEMSHouse_States.T_attic1=X_k_Plant(1,9,jj);
    HEMSHouse_States.T_im1=X_k_Plant(1,10,jj);        

    % Getting Correct Actual AC ON-OFF for this time Step for the House
    HEMSHouse_States.u_k_hvac=X_k_Plus_Plant(1,21,jj);

    HEMSHouse_States.u_k_HeatingMode=U_k(1,13,jj);

    % Calling external function for House Thermal Dynamics
    [HEMSHouseRCModel_Output1] = HEMS_HouseRCModel_WithHeatingMode(HEMSHouse_Params,HEMSWeatherData_Output1,Simulation_Params,HEMSPlant_Params,HEMSHouse_States);

    % Setting up House States
    HEMSHouse_States.T_wall1=HEMSHouseRCModel_Output1.T_wall(end);
    HEMSHouse_States.T_ave1=HEMSHouseRCModel_Output1.T_ave(end);
    HEMSHouse_States.T_attic1=HEMSHouseRCModel_Output1.T_attic(end);
    HEMSHouse_States.T_im1=HEMSHouseRCModel_Output1.T_im(end);

    % Updating House_DataMatrix with House Thermal States
    X_k_Plus_Plant(2,7:10,jj)=[HEMSHouseRCModel_Output1.T_ave(end),HEMSHouseRCModel_Output1.T_wall(end),HEMSHouseRCModel_Output1.T_attic(end),HEMSHouseRCModel_Output1.T_im(end)];

end    

%% Step 6: Computing Battery Dynamics (4 - 6) for All Houses with Batteries

% For Each House with Battery Storage in this Time Step
for jj=1:(N_PV_Bat+N_Bat)

    % Getting Current House Battery State
    E_bat_CurrentHouse = X_k_Plant(1,4,jj);

    % Getting Current Battery Control
    c_k = U_k(1,1,jj);
    d_k = U_k(1,2,jj);

    % Creating Input for Battery Logic Controller
    Current_BatteryPlant_Input.E_bat_CurrentHouse = E_bat_CurrentHouse;

    Current_BatteryPlant_Input.c_k = c_k;
    Current_BatteryPlant_Input.d_k = d_k;

    Current_BatteryPlant_Input.Battery_Energy_Max = Battery_Energy_Max;
    Current_BatteryPlant_Input.MaxRate_Charging = MaxRate_Charging;
    Current_BatteryPlant_Input.MaxRate_Discharging = MaxRate_Discharging;
    Current_BatteryPlant_Input.Battery_Energy_Min = Battery_Energy_Min;

    Current_BatteryPlant_Input.Eff_Charging_Battery = Eff_Charging_Battery;
    Current_BatteryPlant_Input.Eff_Discharging_Battery = Eff_Discharging_Battery;

    Current_BatteryPlant_Input.Eff_Inv = Eff_Inv;

    Current_BatteryPlant_Input.Simulation_StepSize = Simulation_StepSize;

    % Computing Current Battery Dynamics
    [B_Soc_k, B_Ch_k, B_Dch_k] = HEMS_Battery_Plant_OnGrid(Current_BatteryPlant_Input);
    
    % Updating SOC (Within Battery), Charging (On AC Side), Discharging (On AC Side) for Current Battery
    X_k_Plus_Plant(2,4,jj) = B_Soc_k;

    X_k_Plus_Plant(1,5,jj) = B_Ch_k;

    X_k_Plus_Plant(1,6,jj) = B_Dch_k;
    
end


%% Step 7: Computing Grid Energy (39) 

% Computing Total PV Used
Total_PV_Used = sum(X_k_Plant(1,2,:), 3);

% Computing Total Battery Discharging
Total_Bat_Discharging = sum(X_k_Plant(1,6,:), 3);

% Computing Total Battery Charging
Total_Bat_Charging = sum(X_k_Plant(1,5,:), 3);

% Computing Total Load
Total_Load = sum(X_k_Plant(1,11,:), 3) + sum(X_k_Plant(1,12,:), 3);

% Computing Total Local Generation
Total_Local_Generation = Total_PV_Used + Total_Bat_Discharging;

% Computing Total Local Demand
Total_Local_Demand = Total_Load + Total_Bat_Charging;

% Computing Grid Energy ( + : Community Supplies Grid ; - : Community is served by Grid)
Grid_Energy = Total_Local_Generation - Total_Local_Demand;

% Updating Grid Energy in System State
X_k_Plus_Plant(1,39,:) = Grid_Energy*ones(1,1,N_House);

 
end



