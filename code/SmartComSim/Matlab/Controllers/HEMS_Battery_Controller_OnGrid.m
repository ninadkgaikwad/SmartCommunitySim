function [c_k_bc,d_k_bc] = HEMS_Battery_Controller_OnGrid(Baseline_BatteryController_Input)

% Author: Ninad Kiran Gaikwad
% Date: Feb/12/2021
% Description: HEMS_Baseline_Controller - Baseline Controller Logic

%% HEMS_Baseline_Controller - Baseline Controller Logic

%% Getting desired Data from the BaselineController_Input - Struct

PVEnergy_Available=Baseline_BatteryController_Input.PVEnergy_Available;
E_Tot_Desired=Baseline_BatteryController_Input.E_Tot_Desired;

E_bat_CurrentHouse = Baseline_BatteryController_Input.E_bat_CurrentHouse;
Battery_Energy_Max = Baseline_BatteryController_Input.Battery_Energy_Max;



%% Rule Based Logic Controller - Battery

if (E_bat_CurrentHouse < Battery_Energy_Max)

    c_k_bc=1; % Basic Controller Action - Charging
    d_k_bc=0; % Basic Controller Action - Discharging
    
else
    
    c_k_bc=0; % Basic Controller Action - Charging
    d_k_bc=0; % Basic Controller Action - Discharging
    
end 
    

end



