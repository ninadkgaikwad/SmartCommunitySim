function [U_k] = HEMS_Controller_Func(Simulation_ModeType, SmartCommunity_ControllerType, X_k_Plant,W_k_Plant,HEMSPlant_Params,Community_Params,Simulation_Params)

    if (Simulation_ModeType == 0) % Off-Grid Mode
    
        if (SmartCommunity_ControllerType==1) % Smart Local Controller
            
            [U_k] = HEMS_Smart_LocalController_OffGrid(X_k_Plant,W_k_Plant,HEMSPlant_Params,Community_Params,Simulation_Params);
            
        elseif (SmartCommunity_ControllerType==2) % Dumb Local Controller
            
            [U_k] = HEMS_Dumb_LocalController_OffGrid(X_k_Plant,W_k_Plant,HEMSPlant_Params,Community_Params,Simulation_Params);
            
        end

    elseif (Simulation_ModeType == 1) % On-Grid Mode

        [U_k] = HEMS_Dumb_LocalController_OnGrid(X_k_Plant,W_k_Plant,HEMSPlant_Params,Community_Params,Simulation_Params);
    
    end
end

