function [B_Soc_k, B_Ch_k, B_Dch_k] = HEMS_Battery_Plant_OnGrid(Current_BatteryPlant_Input)

% Author: Ninad Kiran Gaikwad
% Date: Mar/15/2021
% Description: HEMS_Plant_FigurePlotter_Input - Plotting Figures for the
% Baseline


%% HEMS_Plant_FigurePlotter - Battery Dynamics

% Getting Desired Data from Current_BatteryPlant_Input 

E_bat_CurrentHouse = Current_BatteryPlant_Input.E_bat_CurrentHouse;

c_k = Current_BatteryPlant_Input.c_k;
d_k = Current_BatteryPlant_Input.d_k;

Battery_Energy_Max = Current_BatteryPlant_Input.Battery_Energy_Max;
MaxRate_Charging = Current_BatteryPlant_Input.MaxRate_Charging;
MaxRate_Discharging = Current_BatteryPlant_Input.MaxRate_Discharging;
Battery_Energy_Min = Current_BatteryPlant_Input.Battery_Energy_Min;

Eff_Charging_Battery = Current_BatteryPlant_Input.Eff_Charging_Battery;
Eff_Discharging_Battery = Current_BatteryPlant_Input.Eff_Discharging_Battery;

Eff_Inv = Current_BatteryPlant_Input.Eff_Inv;

Simulation_StepSize = Current_BatteryPlant_Input.Simulation_StepSize;

%% Computing Battery Dynamics

% Computing Battery Charging - Within Battery
B_Ch_k_bat =  min(Battery_Energy_Max-E_bat_CurrentHouse , c_k*MaxRate_Charging*Simulation_StepSize);

% Computing Battery Discharging  - Within Battery
B_Dch_k_bat =  min(E_bat_CurrentHouse-Battery_Energy_Min , d_k*MaxRate_Discharging*Simulation_StepSize);

% Computing Battery State - Within Battery
B_Soc_k =  E_bat_CurrentHouse + B_Ch_k_bat - B_Dch_k_bat;

% Computing Battery Charging - Within Battery
B_Ch_k =  B_Ch_k_bat/(Eff_Charging_Battery*Eff_Inv);

% Computing Battery Discharging  - On AC Side
B_Dch_k =  B_Dch_k_bat*(Eff_Discharging_Battery*Eff_Inv);


end


