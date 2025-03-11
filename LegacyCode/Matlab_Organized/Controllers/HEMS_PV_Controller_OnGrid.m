function [pv_con] = HEMS_PV_Controller_OnGrid(Baseline_PVController_Input)

% Author: Ninad Kiran Gaikwad
% Date: Feb/12/2021
% Description: HEMS_Baseline_Controller - Baseline Controller Logic

%% HEMS_Baseline_Controller - Baseline Controller Logic

%% Getting desired Data from the BaselineController_Input - Struct

 PVEnergy_Available = Baseline_PVController_Input.PVEnergy_Available;

%% Rule Based Logic Controller - Battery

if (PVEnergy_Available>0)

    pv_con = 1; % Basic Controller Action - Generate at Rated Power
    
else
    
    pv_con = 0; % Basic Controller Action - Generate at None
    
end 
    

end



