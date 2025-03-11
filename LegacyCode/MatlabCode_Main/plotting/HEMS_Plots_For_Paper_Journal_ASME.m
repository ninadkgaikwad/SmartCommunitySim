function [h5,h10] = HEMS_Plots_For_Paper_Journal_ASME(HEMS_Plant_Baseline_FigurePlotter_Input,HEMS_Plant_Baseline_New_FigurePlotter_Input, HEMS_Plant_OptimalController_FigurePlotter_Input, HEMS_Plant_Baseline_IntelligentController_FigurePlotter_Input)

% Author: Ninad Kiran Gaikwad
% Date: Oct/7/2019
% Description: HEMS_Plant_FigurePlotter_Input - Plotting Figures for the Paper

close all;

EToP_Converter=(60/14)*(1400); % kWh --> W

%% HEMS_Plant_FigurePlotter_Input - Plotting Figures for the Paper

%% Getting the desired data from the HEMS_Plant_FigurePlotter_Input - Struct

%% BaseLine

    %----------------HEMS_Plant_Baseline_FigurePlotter_Input------------------%
    HEMS_Plant_Baseline_Output_B=HEMS_Plant_Baseline_FigurePlotter_Input.HEMS_Plant_Baseline_Output;
    HEMSWeatherData_Output_B=HEMS_Plant_Baseline_FigurePlotter_Input.HEMSWeatherData_Output;
    HEMSPlant_Params_B=HEMS_Plant_Baseline_FigurePlotter_Input.HEMSPlant_Params;
    MPC_Output_Images_Path_B=HEMS_Plant_Baseline_FigurePlotter_Input.MPC_Output_Images_Path;

    %---------------------HEMS_Plant_Baseline_Output--------------------------%
    TotalGeneration_B=HEMS_Plant_Baseline_Output_B.TotalGeneration;
    TotalDemand_B=HEMS_Plant_Baseline_Output_B.TotalDemand;
    NetGeneration_B=HEMS_Plant_Baseline_Output_B.NetGeneration;
    NetDemand_B=HEMS_Plant_Baseline_Output_B.NetDemand;
    Ta_Outside_B=HEMS_Plant_Baseline_Output_B.Ta_Outside;
    Ta_Room_B=HEMS_Plant_Baseline_Output_B.Ta_Room;
    T_z_B=HEMS_Plant_Baseline_Output_B.Tz;
    HouseLoad_B=HEMS_Plant_Baseline_Output_B.HouseLoad; 
    PVEnergy_Available_B=HEMS_Plant_Baseline_Output_B.PVEnergy_Available;
    PVEnergy_Used_B=HEMS_Plant_Baseline_Output_B.PVEnergy_Used;
    PVEnergy_Unused_B=HEMS_Plant_Baseline_Output_B.PVEnergy_Unused;
    BatteryLevel_B=HEMS_Plant_Baseline_Output_B.BatteryLevel;
    BatteryEnergy_Charging_B=HEMS_Plant_Baseline_Output_B.BatteryEnergy_Charging;
    BatteryEnergy_Discharging_B=HEMS_Plant_Baseline_Output_B.BatteryEnergy_Discharging;  
    SoC_B=HEMS_Plant_Baseline_Output_B.SoC;
    DoD_B=HEMS_Plant_Baseline_Output_B.DoD; 
    c_k_bc_B=HEMS_Plant_Baseline_Output_B.c_k_bc;
    d_k_bc_B=HEMS_Plant_Baseline_Output_B.d_k_bc;  
    u_k_fr_bc_B=HEMS_Plant_Baseline_Output_B.u_k_fr_bc; 

    %-----------------------HEMSWeatherData_Output----------------------------%
    Ws_B=HEMSWeatherData_Output_B.Ws;
    T_am_B=HEMSWeatherData_Output_B.T_am;
    GHI_B=HEMSWeatherData_Output_B.GHI;
    DNI_B=HEMSWeatherData_Output_B.DNI;
    DateTimeVector=HEMSWeatherData_Output_B.DateTimeVector;
    DateTime_Matrix=HEMSWeatherData_Output_B.DateTime_Matrix;

    %---------------------------HEMSPlant_Params------------------------------%
    Battery_Energy_Max_B=HEMSPlant_Params_B.Battery_Energy_Max;
    Battery_Energy_Min_B=HEMSPlant_Params_B.Battery_Energy_Min;
    T_max_B=HEMSPlant_Params_B.Battery_T_max;
    T_min_B=HEMSPlant_Params_B.Battery_T_min;

    PVSource_B=[PVEnergy_Available_B PVEnergy_Used_B PVEnergy_Unused_B];
    BatterySource_B=[BatteryLevel_B(1:(end-1),1) BatteryEnergy_Charging_B BatteryEnergy_Discharging_B SoC_B DoD_B];

%% BaseLine-New

    %----------------HEMS_Plant_Baseline_FigurePlotter_Input------------------%
    HEMS_Plant_Baseline_Output_BN=HEMS_Plant_Baseline_New_FigurePlotter_Input.HEMS_Plant_Baseline_Output;
    HEMSWeatherData_Output_BN=HEMS_Plant_Baseline_New_FigurePlotter_Input.HEMSWeatherData_Output;
    HEMSPlant_Params_BN=HEMS_Plant_Baseline_New_FigurePlotter_Input.HEMSPlant_Params;
    MPC_Output_Images_Path_BN=HEMS_Plant_Baseline_New_FigurePlotter_Input.MPC_Output_Images_Path;

    %---------------------HEMS_Plant_Baseline_Output--------------------------%
    TotalGeneration_BN=HEMS_Plant_Baseline_Output_BN.TotalGeneration;
    TotalDemand_BN=HEMS_Plant_Baseline_Output_BN.TotalDemand;
    NetGeneration_BN=HEMS_Plant_Baseline_Output_BN.NetGeneration;
    NetDemand_BN=HEMS_Plant_Baseline_Output_BN.NetDemand;
    Ta_Outside_BN=HEMS_Plant_Baseline_Output_BN.Ta_Outside;
    Ta_Room_BN=HEMS_Plant_Baseline_Output_BN.Ta_Room;
    T_z_BN=HEMS_Plant_Baseline_Output_BN.Tz;
    HouseLoad_Actual_BN=HEMS_Plant_Baseline_Output_BN.HouseLoad_Actual; 
    HouseLoad_BN=HEMS_Plant_Baseline_Output_BN.HouseLoad; 
    PVEnergy_Available_BN=HEMS_Plant_Baseline_Output_BN.PVEnergy_Available;
    PVEnergy_Used_BN=HEMS_Plant_Baseline_Output_BN.PVEnergy_Used;
    PVEnergy_Unused_BN=HEMS_Plant_Baseline_Output_BN.PVEnergy_Unused;
    BatteryLevel_BN=HEMS_Plant_Baseline_Output_BN.BatteryLevel;
    BatteryEnergy_Charging_BN=HEMS_Plant_Baseline_Output_BN.BatteryEnergy_Charging;
    BatteryEnergy_Discharging_BN=HEMS_Plant_Baseline_Output_BN.BatteryEnergy_Discharging;  
    SoC_BN=HEMS_Plant_Baseline_Output_BN.SoC;
    DoD_BN=HEMS_Plant_Baseline_Output_BN.DoD; 
    c_k_bc_BN=HEMS_Plant_Baseline_Output_BN.c_k_bc;
    d_k_bc_BN=HEMS_Plant_Baseline_Output_BN.d_k_bc;  
    u_k_fr_bc_BN=HEMS_Plant_Baseline_Output_BN.u_k_fr_bc; 

    %-----------------------HEMSWeatherData_Output----------------------------%
    Ws_BN=HEMSWeatherData_Output_BN.Ws;
    T_am_BN=HEMSWeatherData_Output_BN.T_am;
    GHI_BN=HEMSWeatherData_Output_BN.GHI;
    DNI_BN=HEMSWeatherData_Output_BN.DNI;

    %---------------------------HEMSPlant_Params------------------------------%
    Battery_Energy_Max_BN=HEMSPlant_Params_BN.Battery_Energy_Max;
    Battery_Energy_Min_BN=HEMSPlant_Params_BN.Battery_Energy_Min;
    T_max_BN=HEMSPlant_Params_BN.Battery_T_max;
    T_min_BN=HEMSPlant_Params_BN.Battery_T_min;

    PVSource_BN=[PVEnergy_Available_BN PVEnergy_Used_BN PVEnergy_Unused_BN];
    BatterySource_BN=[BatteryLevel_BN(1:(end-1),1) BatteryEnergy_Charging_BN BatteryEnergy_Discharging_BN SoC_BN DoD_BN];    
    
%% Intelligent Baseline Controller    
    
    %----------------HEMS_Plant_Baseline_FigurePlotter_Input------------------%
    HEMS_Optimizer_OutputsFull_I=HEMS_Plant_Baseline_IntelligentController_FigurePlotter_Input.HEMS_Optimizer_OutputsFull;
    HEMS_Plant_MPC_Output_Final_I=HEMS_Plant_Baseline_IntelligentController_FigurePlotter_Input.HEMS_Plant_MPC_Output_Final;
    HEMSWeatherData_MPC_Output_I=HEMS_Plant_Baseline_IntelligentController_FigurePlotter_Input.HEMSWeatherData_MPC_Output;
    MPC_Plotting_Iterator_I=HEMS_Plant_Baseline_IntelligentController_FigurePlotter_Input.MPC_Plotting_Iterator;
    HEMS_Optimal_Controller_Input_I=HEMS_Plant_Baseline_IntelligentController_FigurePlotter_Input.HEMS_Optimal_Controller_Input;
    Simulation_Params_I=HEMS_Plant_Baseline_IntelligentController_FigurePlotter_Input.Simulation_Params;
    MPC_Params_I=HEMS_Plant_Baseline_IntelligentController_FigurePlotter_Input.MPC_Params;
    MPC_Output_Images_Path_I=HEMS_Plant_Baseline_IntelligentController_FigurePlotter_Input.MPC_Output_Images_Path;
    E_Total_Disturbance_I=HEMS_Plant_Baseline_IntelligentController_FigurePlotter_Input.E_Total_Disturbance;

    %HEMS_Optimizer_OutputsFull_Desired_O=HEMS_Optimizer_OutputsFull(1);

    %---------------------HEMS_Plant_MPC_Output_Final-------------------------%
    TotalGeneration_I=HEMS_Plant_MPC_Output_Final_I.TotalGeneration;
    TotalDemand_I=HEMS_Plant_MPC_Output_Final_I.TotalDemand;
    NetGeneration_I=HEMS_Plant_MPC_Output_Final_I.NetGeneration;
    NetDemand_I=HEMS_Plant_MPC_Output_Final_I.NetDemand;
    Ta_Outside_I=HEMS_Plant_MPC_Output_Final_I.Ta_Outside;
    Ta_Room_I=HEMS_Plant_MPC_Output_Final_I.Ta_Room;
    T_z_I=HEMS_Plant_MPC_Output_Final_I.Tz;
    HouseLoad_I=HEMS_Plant_MPC_Output_Final_I.HouseLoad; 
%     HouseLoad_Desired_I=HEMS_Plant_MPC_Output_Final_I.HouseLoad_Desired; 
    PVEnergy_Available_I=HEMS_Plant_MPC_Output_Final_I.PVEnergy_Available;
    PVEnergy_Used_I=HEMS_Plant_MPC_Output_Final_I.PVEnergy_Used;
    PVEnergy_Unused_I=HEMS_Plant_MPC_Output_Final_I.PVEnergy_Unused;
    BatteryLevel_I=HEMS_Plant_MPC_Output_Final_I.BatteryLevel;
    BatteryEnergy_Charging_I=HEMS_Plant_MPC_Output_Final_I.BatteryEnergy_Charging;
    BatteryEnergy_Discharging_I=HEMS_Plant_MPC_Output_Final_I.BatteryEnergy_Discharging;  
    SoC_I=HEMS_Plant_MPC_Output_Final_I.SoC;
    %SoC=((BatteryLevel-2.1984)/(14.9920-2.1984))*140;
    DoD=HEMS_Plant_MPC_Output_Final_I.DoD; 
    c_k_bc_I=HEMS_Plant_MPC_Output_Final_I.c_k;
    d_k_bc_I=HEMS_Plant_MPC_Output_Final_I.d_k;  
    u_k_fr_bc_I=HEMS_Plant_MPC_Output_Final_I.u_k_fr; 

    %-----------------------HEMSWeatherDat    %---------------------------%
    
    Ws_I=HEMSWeatherData_MPC_Output_I.Ws;
    T_am_I=HEMSWeatherData_MPC_Output_I.T_am;
    GHI_I=HEMSWeatherData_MPC_Output_I.GHI;
    DNI_I=HEMSWeatherData_MPC_Output_I.DNI;

    
%% Optimal Controller
    
    %----------------HEMS_Plant_Baseline_FigurePlotter_Input------------------%
    HEMS_Optimizer_OutputsFull_O=HEMS_Plant_OptimalController_FigurePlotter_Input.HEMS_Optimizer_OutputsFull;
    HEMS_Plant_MPC_Output_Final_O=HEMS_Plant_OptimalController_FigurePlotter_Input.HEMS_Plant_MPC_Output_Final;
    HEMSWeatherData_MPC_Output_O=HEMS_Plant_OptimalController_FigurePlotter_Input.HEMSWeatherData_MPC_Output;
    MPC_Plotting_Iterator_O=HEMS_Plant_OptimalController_FigurePlotter_Input.MPC_Plotting_Iterator;
    HEMS_Optimal_Controller_Input_O=HEMS_Plant_OptimalController_FigurePlotter_Input.HEMS_Optimal_Controller_Input;
    Simulation_Params_O=HEMS_Plant_OptimalController_FigurePlotter_Input.Simulation_Params;
    MPC_Params_O=HEMS_Plant_OptimalController_FigurePlotter_Input.MPC_Params;
    MPC_Output_Images_Path_O=HEMS_Plant_OptimalController_FigurePlotter_Input.MPC_Output_Images_Path;
    E_Total_Disturbance_O=HEMS_Plant_OptimalController_FigurePlotter_Input.E_Total_Disturbance;

    %HEMS_Optimizer_OutputsFull_Desired_O=HEMS_Optimizer_OutputsFull(1);

    %---------------------HEMS_Plant_MPC_Output_Final-------------------------%
    TotalGeneration_O=HEMS_Plant_MPC_Output_Final_O.TotalGeneration;
    TotalDemand_O=HEMS_Plant_MPC_Output_Final_O.TotalDemand;
    NetGeneration_O=HEMS_Plant_MPC_Output_Final_O.NetGeneration;
    NetDemand_O=HEMS_Plant_MPC_Output_Final_O.NetDemand;
    Ta_Outside_O=HEMS_Plant_MPC_Output_Final_O.Ta_Outside;
    Ta_Room_O=HEMS_Plant_MPC_Output_Final_O.Ta_Room;
    T_z_O=HEMS_Plant_MPC_Output_Final_O.Tz;
    HouseLoad_O=HEMS_Plant_MPC_Output_Final_O.HouseLoad; 
    HouseLoad_Desired_O=HEMS_Plant_MPC_Output_Final_O.HouseLoad_Desired; 
    PVEnergy_Available_O=HEMS_Plant_MPC_Output_Final_O.PVEnergy_Available;
    PVEnergy_Used_O=HEMS_Plant_MPC_Output_Final_O.PVEnergy_Used;
    PVEnergy_Unused_O=HEMS_Plant_MPC_Output_Final_O.PVEnergy_Unused;
    BatteryLevel_O=HEMS_Plant_MPC_Output_Final_O.BatteryLevel;
    BatteryEnergy_Charging_O=HEMS_Plant_MPC_Output_Final_O.BatteryEnergy_Charging;
    BatteryEnergy_Discharging_O=HEMS_Plant_MPC_Output_Final_O.BatteryEnergy_Discharging;  
    SoC_O=HEMS_Plant_MPC_Output_Final_O.SoC;
    %SoC=((BatteryLevel-2.1984)/(14.9920-2.1984))*140;
    DoD=HEMS_Plant_MPC_Output_Final_O.DoD; 
    c_k_bc_O=HEMS_Plant_MPC_Output_Final_O.c_k;
    d_k_bc_O=HEMS_Plant_MPC_Output_Final_O.d_k;  
    u_k_fr_bc_O=HEMS_Plant_MPC_Output_Final_O.u_k_fr; 

    %-----------------------HEMSWeatherDat    %---------------------------%
    
    Ws_O=HEMSWeatherData_MPC_Output_O.Ws;
    T_am_O=HEMSWeatherData_MPC_Output_O.T_am;
    GHI_O=HEMSWeatherData_MPC_Output_O.GHI;
    DNI_O=HEMSWeatherData_MPC_Output_O.DNI;
    DateTimeVector=HEMSWeatherData_MPC_Output_O.DateTimeVector_Plotting;
    DateTimeVector_Full=HEMSWeatherData_MPC_Output_O.DateTimeVector;
    DateTime_Matrix=HEMSWeatherData_MPC_Output_O.DateTime_Matrix;
    Duration_TimeSteps=HEMSWeatherData_MPC_Output_O.Duration_TimeSteps;

    %--------------------HEMS_Optimal_Controller_Input------------------------%
    T_k_fr_max_O=HEMS_Optimal_Controller_Input_O.T_k_fr_max;
    T_k_fr_min_O=HEMS_Optimal_Controller_Input_O.T_k_fr_min;
    E_delta_fr_O=HEMS_Optimal_Controller_Input_O.E_delta_fr;
    E_delta_fr_d_O=HEMS_Optimal_Controller_Input_O.E_delta_fr_d;
    E_bat_delta_O=HEMS_Optimal_Controller_Input_O.E_bat_delta;
    E_bat_max_O=HEMS_Optimal_Controller_Input_O.E_bat_max;
    E_bat_min_O=HEMS_Optimal_Controller_Input_O.E_bat_min;

    %-------------------------Simulation_Parmas-------------------------------%
    FileRes=Simulation_Params_O.FileRes;
    Simulation_StepSize=Simulation_Params_O.Simulation_StepSize;
    StepSize=Simulation_Params_O.StepSize;

    %-----------------------------MPC_Params----------------------------------%
    MPC_ComputationLength_Day=MPC_Params_O.MPC_ComputationLength_Day;    
    MPC_StepLengthUsed=MPC_Params_O.MPC_StepLengthUsed;   

    %----------------------------State Bounds---------------------------------%
    T_k_fr_max_O=HEMS_Plant_OptimalController_FigurePlotter_Input.T_k_fr_max;
    T_k_fr_min_O=HEMS_Plant_OptimalController_FigurePlotter_Input.T_k_fr_min;
    E_bat_max_O=HEMS_Plant_OptimalController_FigurePlotter_Input.E_bat_max;
    E_bat_min_O=HEMS_Plant_OptimalController_FigurePlotter_Input.E_bat_min;
    
%     %% RPi MILP Controller
%     
%     BatteryLevel_RL=HEMS_Plant_RpiMILP_FigurePlotter_Input.E_bat;
%     T_z_RL=HEMS_Plant_RpiMILP_FigurePlotter_Input.T_fr;    
%     HouseLoad_RL=HEMS_Plant_RpiMILP_FigurePlotter_Input.E_s_provided;
%     
%     %BatteryLevel_RL(end+1,1)=BatteryLevel_RL(end,1);
%     %T_z_RL(end+1,1)=T_z_RL(end,1);
%     %HouseLoad_RL(end+1:end+2,1)=[HouseLoad_RL(end,1);HouseLoad_RL(end,1)];
%     
%     
%     SoC_RPi=(1-(E_bat_max_O-BatteryLevel_RL)/(E_bat_max_O-E_bat_min_O))*100;    

    %% Basic Computations

    PVSource_O=[PVEnergy_Available_O PVEnergy_Used_O PVEnergy_Unused_O];
    %BatterySource=[BatteryLevel(1:(end-1),1) BatteryEnergy_Charging BatteryEnergy_Discharging SoC DoD];

%% DateTime Vector to Hours

D=DateTimeVector(2)-DateTimeVector(1);

M=minutes(D);

H=M/60;

L=length(DateTimeVector);

HoursVector=zeros(1008,1);
HoursVector=zeros(1008,1);

for ii=2:1008
    HoursVector(ii,1)=HoursVector(ii-1,1)+H;
end

% for ii=2:L
%     HoursVector(ii,1)=HoursVector(ii-1,1)+H;
%     if (abs(HoursVector(ii,1)-24) < 1e4*eps(min(abs(HoursVector(ii,1)),abs(24))))
%         HoursVector(ii,1)=0;
%     end
% end

%% Plotting the Figures
    
% Fridge Temperature , House Temperature , Battery SOC - Baseline    
h1=figure(1);
hold on
box on

yyaxis left
P2 = plot(HoursVector,T_z_B(1:1008,1),'-b','LineWidth',1.5);
plot(HoursVector,T_max_B*ones(1008,1),'-k','LineWidth',1);
plot(HoursVector,T_min_B*ones(1008,1),'-k','LineWidth',1);

xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([-6 35]);
xlim([0 170]);
%title('Temperature Outside/House/Refrigerator');
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P2, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;
yrule_1(1).Color='b';
ylabel('$^{\circ}C$','Interpreter','latex','FontSize', 16);



yyaxis right
P3 = plot(HoursVector,SoC_B(1:1008,1),'LineStyle','-','Color',[1,0.5729,0],'LineWidth',2);
% P4 = plot(HoursVector,100*ones(1008,1),'--r','LineWidth',2);
% P5 = plot(HoursVector,0*ones(1008,1),'--r','LineWidth',2);
ylim([0 100]);
xlim([0 170]);
ax1 = ancestor(P3, 'axes');
yrule_2 = ax1.YAxis;
yrule_2(2).FontSize=14;  
yrule_2(2).Color=[1,0.5729,0];
ylabel('$\%$','Interpreter','latex','FontSize', 16);

legend1=legend([P2,P3],'Refrigerator - Temp.','Battery - SOC');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;  

% Desired Vs. Serviced Non-Critical Loads - Baseline
h2=figure(2);
hold on 
box on

P1=plot(HoursVector,EToP_Converter*(HouseLoad_B(1:1008,1)+HouseLoad_B(1:1008,2)),'--r','LineWidth',2);
P2=plot(HoursVector,EToP_Converter*(HouseLoad_B(1:1008,7)-HouseLoad_B(1:1008,3)),'-b','LineWidth',2);

xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([0 400]);
xlim([0 170]);
ax1 = ancestor(P1, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;    

xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ylabel('$W$','Interpreter','latex','FontSize', 16);
legend1=legend('Desired - Secondary demand','Serviced - Secondary demand');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;  

% Fridge Temperature , House Temperature , Battery SOC - Optimal    
h3=figure(3);
hold on
box on

yyaxis left
P2 = plot(HoursVector,T_z_O(1:1008,1),'-b','LineWidth',1.5);
plot(HoursVector,T_k_fr_max_O*ones(1008,1),'-k','LineWidth',1);
plot(HoursVector,T_k_fr_min_O*ones(1008,1),'-k','LineWidth',1);

xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([-6 35]);
xlim([0 170]);
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P2, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;
yrule_1(1).Color='b';
ylabel('$^{\circ}C$','Interpreter','latex','FontSize', 16);

yyaxis right
P3 = plot(HoursVector,SoC_O(1:1008,1),'LineStyle','-','Color',[1,0.5729,0],'LineWidth',2);
% P4 = plot(HoursVector,100*ones(1008,1),'--r','LineWidth',2);
% P5 = plot(HoursVector,0*ones(1008,1),'--r','LineWidth',2);
ylim([0 100]);
xlim([0 170]);
ax1 = ancestor(P3, 'axes');
yrule_2 = ax1.YAxis;
yrule_2(2).FontSize=14;   
yrule_2(2).Color=[1,0.5729,0];
ylabel('$\%$','Interpreter','latex','FontSize', 16);

legend1=legend([P2,P3],'Refrigerator - Temp.','Battery - SOC');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;

% Desired Vs. Serviced Non-Critical Loads - Optimal 
h4=figure(4);

hold on
box on

P1=plot(HoursVector,EToP_Converter*(HouseLoad_Desired_O(1:1008,2)+HouseLoad_Desired_O(1:1008,1)),'--r','LineWidth',2.5);
P2=plot(HoursVector,EToP_Converter*(HouseLoad_O(1:1008,2)+HouseLoad_O(1:1008,1)),'-b','LineWidth',2);

xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([0 450]);
xlim([0 170]);
ax1 = ancestor(P1, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;  

xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ylabel('$W$','Interpreter','latex','FontSize', 16);
legend1=legend( 'Desired - Secondary demand','Serviced - Secondary demand ');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;


% Fridge Temperature , House Temperature , Battery SOC - Intelligent    
h5=figure(5);
hold on
box on

yyaxis left
P2 = plot(HoursVector,T_z_I(1:1008,1),'-b','LineWidth',1.5);
plot(HoursVector,T_k_fr_max_O*ones(1008,1),'-k','LineWidth',1);
plot(HoursVector,T_k_fr_min_O*ones(1008,1),'-k','LineWidth',1);

xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([-6 35]);
xlim([0 170]);
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P2, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;
yrule_1(1).Color='b';
ylabel('$^{\circ}C$','Interpreter','latex','FontSize', 16);

yyaxis right
P3 = plot(HoursVector,SoC_I(1:1008,1),'LineStyle','-','Color',[1,0.5729,0],'LineWidth',2);
% P4 = plot(HoursVector,100*ones(1008,1),'--r','LineWidth',2);
% P5 = plot(HoursVector,0*ones(1008,1),'--r','LineWidth',2);
ylim([0 100]);
xlim([0 170]);
ax1 = ancestor(P3, 'axes');
yrule_2 = ax1.YAxis;
yrule_2(2).FontSize=14;   
yrule_2(2).Color=[1,0.5729,0];
ylabel('$\%$','Interpreter','latex','FontSize', 16);

legend1=legend([P2,P3],'Refrigerator - Temp.','Battery - SOC');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;

% Desired Vs. Serviced Non-Critical Loads - Intelligent
h6=figure(6);

hold on
box on

P1=plot(HoursVector,EToP_Converter*(HouseLoad_Desired_O(1:1008,2)+HouseLoad_Desired_O(1:1008,1)),'--r','LineWidth',2.5);
P2=plot(HoursVector,EToP_Converter*(HouseLoad_I(1:1008,2)+HouseLoad_I(1:1008,1)),'-b','LineWidth',2);

xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([0 450]);
xlim([0 170]);
ax1 = ancestor(P1, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;  

xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ylabel('$W$','Interpreter','latex','FontSize', 16);
legend1=legend( 'Desired - Secondary demand','Serviced - Secondary demand ');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;

% Fridge Temperature , House Temperature , Battery SOC - Baseline New   
h7=figure(7);
hold on
box on

yyaxis left
P2 = plot(HoursVector,T_z_BN(1:1008,1),'-b','LineWidth',1.5);
plot(HoursVector,T_max_BN*ones(1008,1),'-k','LineWidth',1);
plot(HoursVector,T_min_BN*ones(1008,1),'-k','LineWidth',1);

xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([-6 35]);
xlim([0 170]);
%title('Temperature Outside/House/Refrigerator');
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P2, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;
yrule_1(1).Color='b';
ylabel('$^{\circ}C$','Interpreter','latex','FontSize', 16);



yyaxis right
P3 = plot(HoursVector,SoC_BN(1:1008,1),'LineStyle','-','Color',[1,0.5729,0],'LineWidth',2);
% P4 = plot(HoursVector,100*ones(1008,1),'--r','LineWidth',2);
% P5 = plot(HoursVector,0*ones(1008,1),'--r','LineWidth',2);
ylim([0 100]);
xlim([0 170]);
ax1 = ancestor(P3, 'axes');
yrule_2 = ax1.YAxis;
yrule_2(2).FontSize=14;  
yrule_2(2).Color=[1,0.5729,0];
ylabel('$\%$','Interpreter','latex','FontSize', 16);

legend1=legend([P2,P3],'Refrigerator - Temp.','Battery - SOC');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;  

% Desired Vs. Serviced Non-Critical Loads - Baseline New
h8=figure(8);
hold on 
box on

P1=plot(HoursVector,EToP_Converter*(HouseLoad_BN(1:1008,1)+HouseLoad_BN(1:1008,2)),'--r','LineWidth',2);
P2=plot(HoursVector,EToP_Converter*(HouseLoad_Actual_BN(1:1008,1)+HouseLoad_Actual_BN(1:1008,2)),'-b','LineWidth',2);

xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([0 400]);
xlim([0 170]);
ax1 = ancestor(P1, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;    

xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ylabel('$W$','Interpreter','latex','FontSize', 16);
legend1=legend('Desired - Secondary demand','Serviced - Secondary demand');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;  


% Comparison of Baseline and Optimal Controller and RL

% Baseline Tz distance from Temperature band
for ii=1:length(T_z_B)
    if ((T_z_B(ii,1)<=T_max_B)&&(T_z_B(ii,1)>=T_min_B)) % T_z within Temperature Band
        T_z_B_d(ii,1)=0;
    elseif (T_z_B(ii,1)>T_max_B) % T_z greater than T_max
        T_z_B_d(ii,1)=T_z_B(ii,1)-T_max_B;
    elseif (T_z_B(ii,1)<T_min_B) % T_z lesser than T_min
        T_z_B_d(ii,1)=abs(T_z_B(ii,1)-T_min_B);
    end
    
end

% Optimal Tz distance from Temperature band
for ii=1:length(T_z_O)
    if ((T_z_O(ii,1)<=T_k_fr_max_O)&&(T_z_O(ii,1)>=T_k_fr_min_O)) % T_z within Temperature Band
        T_z_O_d(ii,1)=0;
    elseif (T_z_O(ii,1)>T_k_fr_max_O) % T_z greater than T_max
        T_z_O_d(ii,1)=T_z_O(ii,1)-T_max_B;
    elseif (T_z_O(ii,1)<T_k_fr_min_O) % T_z lesser than T_min
        T_z_O_d(ii,1)=abs(T_z_O(ii,1)-T_min_B);
    end
    
end

% Intelligent Tz distance from Temperature band
for ii=1:length(T_z_I)
    if ((T_z_I(ii,1)<=T_k_fr_max_O)&&(T_z_I(ii,1)>=T_k_fr_min_O)) % T_z within Temperature Band
        T_z_I_d(ii,1)=0;
    elseif (T_z_I(ii,1)>T_k_fr_max_O) % T_z greater than T_max
        T_z_I_d(ii,1)=T_z_I(ii,1)-T_max_B;
    elseif (T_z_I(ii,1)<T_k_fr_min_O) % T_z lesser than T_min
        T_z_I_d(ii,1)=abs(T_z_I(ii,1)-T_min_B);
    end
    
end

% Baseline-New Tz distance from Temperature band
for ii=1:length(T_z_BN)
    if ((T_z_BN(ii,1)<=T_max_B)&&(T_z_BN(ii,1)>=T_min_B)) % T_z within Temperature Band
        T_z_BN_d(ii,1)=0;
    elseif (T_z_BN(ii,1)>T_max_B) % T_z greater than T_max
        T_z_BN_d(ii,1)=T_z_BN(ii,1)-T_max_B;
    elseif (T_z_BN(ii,1)<T_min_B) % T_z lesser than T_min
        T_z_BN_d(ii,1)=abs(T_z_BN(ii,1)-T_min_B);
    end
    
end

h9=figure(9);
hold on
box on

%P4=plot(HoursVector,T_z_RL_d(1:1008,1),'-k','LineWidth',2);
P2=plot(HoursVector,T_z_O_d(1:1008,1),'-k','LineWidth',2);
P5=plot(HoursVector,T_z_I_d(1:1008,1),'-b','LineWidth',2);
P1=plot(HoursVector,T_z_B_d(1:1008,1),'-r','LineWidth',2);
P4=plot(HoursVector,T_z_BN_d(1:1008,1),'-r','LineWidth',2);
P3=plot(HoursVector,zeros(1008,1),'-k','LineWidth',2);

xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([0 30]);
xlim([0 170]);
ax1 = ancestor(P1, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;  

xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ylabel('Refrigerator temp. violations $^{\circ}C$','Interpreter','latex','FontSize', 14);
legend1=legend('MPC','Intelligent Baseline','Baseline','Baseline New');
set(legend1,'Interpreter','latex','FontSize', 12);

box off
hold off;

%% For Reviewer Comments

% Zoomed-In Temp and SOC for Optimal
h10=figure(10);
box on

subplot(2,1,1); % Temp
hold on;

P2 = plot(HoursVector,T_z_O(1:1008,1),'-b','LineWidth',1.5);
plot(HoursVector,T_k_fr_max_O*ones(1008,1),'-k','LineWidth',1);
plot(HoursVector,T_k_fr_min_O*ones(1008,1),'-k','LineWidth',1);

title('MPC Controller');
%xticks([0 24 48 72 96 120 144 168])
%xticklabels({'0','24','48','72','96','120','144','168'})
ylim([-6 20]);
xlim([115 155]);
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P2, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;
yrule_1(1).Color='k';
ylabel('$^{\circ}C$','Interpreter','latex','FontSize', 16);

legend1=legend([P2],'Refrigerator - Temp.');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 10);

hold off;

subplot(2,1,2); % SOC
hold on;

P3 = plot(HoursVector,SoC_O(1:1008,1),'LineStyle','-','Color',[1,0.5729,0],'LineWidth',2);
% P4 = plot(HoursVector,100*ones(1008,1),'--r','LineWidth',2);
% P5 = plot(HoursVector,0*ones(1008,1),'--r','LineWidth',2);
ylim([0 100]);
xlim([115 155]);
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P3, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_2 = ax1.YAxis;
yrule_2.FontSize=14;   
yrule_2.Color='k';
ylabel('$\%$','Interpreter','latex','FontSize', 16);

legend1=legend([P3],'Battery - SOC');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 10);

hold off;

box off
% Zoomed-In Temp and SOC for Intelligent
h11=figure(11);
box on

subplot(2,1,1); % Temp
hold on;

P2 = plot(HoursVector,T_z_I(1:1008,1),'-b','LineWidth',1.5);
plot(HoursVector,T_k_fr_max_O*ones(1008,1),'-k','LineWidth',1);
plot(HoursVector,T_k_fr_min_O*ones(1008,1),'-k','LineWidth',1);

title('Rule-Based Controller');
%xticks([0 24 48 72 96 120 144 168])
%xticklabels({'0','24','48','72','96','120','144','168'})
ylim([-6 20]);
xlim([115 155]);
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P2, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1.FontSize=14;
yrule_1.Color='k';
ylabel('$^{\circ}C$','Interpreter','latex','FontSize', 16);

legend1=legend([P2],'Refrigerator - Temp.');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 10);

hold off;

subplot(2,1,2); % SOC
hold on;

P3 = plot(HoursVector,SoC_I(1:1008,1),'LineStyle','-','Color',[1,0.5729,0],'LineWidth',2);
% P4 = plot(HoursVector,100*ones(1008,1),'--r','LineWidth',2);
% P5 = plot(HoursVector,0*ones(1008,1),'--r','LineWidth',2);
ylim([0 100]);
xlim([115 155]);
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P3, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_2 = ax1.YAxis;
yrule_2.FontSize=14;   
yrule_2.Color='k';
ylabel('$\%$','Interpreter','latex','FontSize', 16);

legend1=legend([P3],'Battery - SOC');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 10);

hold off;

box off

% Zoomed-In Temp and SOC for Optimal-Intelligent
h12=figure(12);
box on

subplot(2,2,1); % Temp-MPC
hold on;

P2 = plot(HoursVector,T_z_O(1:1008,1),'-b','LineWidth',1.5);
plot(HoursVector,T_k_fr_max_O*ones(1008,1),'-k','LineWidth',1);
plot(HoursVector,T_k_fr_min_O*ones(1008,1),'-k','LineWidth',1);

title('MPC Controller');
%xticks([0 24 48 72 96 120 144 168])
%xticklabels({'0','24','48','72','96','120','144','168'})
ylim([-6 20]);
xlim([115 155]);
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P2, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1.FontSize=14;
yrule_1.Color='k';
ylabel('$^{\circ}C$','Interpreter','latex','FontSize', 16);

legend1=legend([P2],'Refrigerator - Temp.');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 10);

hold off;

subplot(2,2,2); % Temp-Intelligent
hold on;

P2 = plot(HoursVector,T_z_I(1:1008,1),'-b','LineWidth',1.5);
plot(HoursVector,T_k_fr_max_O*ones(1008,1),'-k','LineWidth',1);
plot(HoursVector,T_k_fr_min_O*ones(1008,1),'-k','LineWidth',1);

title('Rule-Based Controller');
%xticks([0 24 48 72 96 120 144 168])
%xticklabels({'0','24','48','72','96','120','144','168'})
ylim([-6 20]);
xlim([115 155]);
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P2, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1.FontSize=14;
yrule_1.Color='k';
ylabel('$^{\circ}C$','Interpreter','latex','FontSize', 16);

legend1=legend([P2],'Refrigerator - Temp.');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 10);

hold off;

subplot(2,2,3); % SOC-MPC
hold on;

P3 = plot(HoursVector,SoC_O(1:1008,1),'LineStyle','-','Color',[1,0.5729,0],'LineWidth',2);
% P4 = plot(HoursVector,100*ones(1008,1),'--r','LineWidth',2);
% P5 = plot(HoursVector,0*ones(1008,1),'--r','LineWidth',2);
ylim([0 100]);
xlim([115 155]);
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P3, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_2 = ax1.YAxis;
yrule_2.FontSize=14;   
yrule_2.Color='k';
ylabel('$\%$','Interpreter','latex','FontSize', 16);

legend1=legend([P3],'Battery - SOC');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 10);

hold off;

subplot(2,2,4); % SOC-Intelligent
hold on;

P3 = plot(HoursVector,SoC_I(1:1008,1),'LineStyle','-','Color',[1,0.5729,0],'LineWidth',2);
% P4 = plot(HoursVector,100*ones(1008,1),'--r','LineWidth',2);
% P5 = plot(HoursVector,0*ones(1008,1),'--r','LineWidth',2);
ylim([0 100]);
xlim([115 155]);
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P3, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_2 = ax1.YAxis;
yrule_2.FontSize=14;   
yrule_2.Color='k';
ylabel('$\%$','Interpreter','latex','FontSize', 16);

legend1=legend([P3],'Battery - SOC');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 10);

hold off;

box off

%% Printing Figures to PDF

Figures={h1,h2,h3,h4,h5,h6,h7,h8,h9,h10,h11,h12};

FigureName={'Temperature_Baseline_Nominal.pdf','DesiredServicedNC_Baseline_Nominal.pdf',...
    'Temperature_MILP_Nominal.pdf','DesiredServicedNC_MILP_Nominal.pdf',...
    'Temperature_Intelligent_Nominal.pdf','DesiredServicedNC_Intelligent_Nominal.pdf',...
    'Temperature_BaselineNew_Nominal.pdf','DesiredServicedNC_BaselineNew_Nominal.pdf',...
    'TemperatureViolations.pdf',...
    'Temperature_SOC_Zoomed_MPC.pdf',...
    'Temperature_SOC_Zoomed_Intelligent.pdf',...
    'Temperature_SOC_Zoomed_MPC_Intelligent.pdf'};

for ii=1:12
   
    F_prep_fig4printing(Figures{ii}); % Preparing Figure
    
    print(Figures{ii},'-dpdf', FigureName{ii}); % Printing figure in PDF
    
end

 % print h2 -dpdf SoC_Baseline_Optimal.pdf
 
%% Computing Quatitaive Analysis
 
% Computing Fridge Death

% For Baseline [T_z_B;T_max_B;DateTimeVector]
Fridge_Death_TimeTotal_B=0;
for ii=1:length(T_z_B)
    if(T_z_B(ii,1)>(T_max_B+2))
        Fridge_Death_TimeTotal_B=Fridge_Death_TimeTotal_B+(10/60); % Hours
    end
end
Fridge_Death_AvgPerDay_B=Fridge_Death_TimeTotal_B/(7);

% For MPC [T_z_O;T_max_O;DateTimeVector]
Fridge_Death_TimeTotal_O=0;
for ii=1:length(T_z_O)
    if(T_z_O(ii,1)>(T_k_fr_max_O+2))
        Fridge_Death_TimeTotal_O=Fridge_Death_TimeTotal_O+(10/60); % Hours
    end
end
Fridge_Death_AvgPerDay_O=Fridge_Death_TimeTotal_O/(7);

% For Intelligent [T_z_I;T_max_O;DateTimeVector]
Fridge_Death_TimeTotal_I=0;
for ii=1:length(T_z_I)
    if(T_z_I(ii,1)>(T_k_fr_max_O+2))
        Fridge_Death_TimeTotal_I=Fridge_Death_TimeTotal_I+(10/60); % Hours
    end
end
Fridge_Death_AvgPerDay_I=Fridge_Death_TimeTotal_I/(7);

% For Baseline-New [T_z_B;T_max_B;DateTimeVector]
Fridge_Death_TimeTotal_BN=0;
for ii=1:length(T_z_BN)
    if(T_z_BN(ii,1)>(T_max_B+2))
        Fridge_Death_TimeTotal_BN=Fridge_Death_TimeTotal_BN+(10/60); % Hours
    end
end
Fridge_Death_AvgPerDay_BN=Fridge_Death_TimeTotal_BN/(7);

% % For RPi [T_z_RL;T_max_O;DateTimeVector]
% Fridge_Death_TimeTotal_RL=0;
% for ii=1:length(T_z_RL)
%     if(T_z_RL(ii,1)>(T_k_fr_max_O+2))
%         Fridge_Death_TimeTotal_RL=Fridge_Death_TimeTotal_RL+(10/60); % Hours
%     end
% end
% Fridge_Death_AvgPerDay_RL=Fridge_Death_TimeTotal_RL/(7);

% Computing % of Non Critical Loads Served

% For Baseline [(HouseLoad_B(:,1)+HouseLoad_B(:,2)),(HouseLoad_B(:,7)-HouseLoad_B(:,3)),DateTimeVector]
NC_Served_B=HouseLoad_B(:,7)-HouseLoad_B(:,3);
NC_Desired_B=HouseLoad_B(:,1)+HouseLoad_B(:,2);

NC_Desired_Points_B=0;
NC_Served_Points_B=0;
for ii=1:length(NC_Served_B)
    if(NC_Desired_B(ii,1)>0)
        NC_Desired_Points_B=NC_Desired_Points_B+1;
    end
    if((NC_Served_B(ii,1)<NC_Desired_B(ii,1))&&(~(NC_Served_B(ii,1)<0)))
        % NC Load Not Served
    elseif ((NC_Served_B(ii,1)==NC_Desired_B(ii,1))&&(~(NC_Served_B(ii,1)<=0)))
        NC_Served_Points_B=NC_Served_Points_B+1;
    end
end

Percentage_NC_Served_B = 100-((NC_Served_Points_B)/(NC_Desired_Points_B)*(100));

% For MPC [HouseLoad_Desired_O(:,1)+HouseLoad_Desired_O(:,2),HouseLoad_O(:,1)+HouseLoad_O(:,2),DateTimeVector]
NC_Served_O=HouseLoad_O(:,1)+HouseLoad_O(:,2);
NC_Desired_O=HouseLoad_Desired_O(:,1)+HouseLoad_Desired_O(:,2);

NC_Desired_Points_O=0;
NC_Served_Points_O=0;
for ii=1:length(NC_Served_O)
    if(NC_Desired_O(ii,1)>0)
        NC_Desired_Points_O=NC_Desired_Points_O+1;
    end
    if((NC_Served_O(ii,1)<NC_Desired_O(ii,1)))
        % NC Load Not Served
    elseif ((NC_Served_O(ii,1)==NC_Desired_O(ii,1))&&(~(NC_Served_O(ii,1)<=0)))
        NC_Served_Points_O=NC_Served_Points_O+1;
    end
end

Percentage_NC_Served_O = 100-((NC_Served_Points_O)/(NC_Desired_Points_O)*(100));

% For Intelligent [HouseLoad_Desired_O(:,1)+HouseLoad_Desired_O(:,2),HouseLoad_O(:,1)+HouseLoad_O(:,2),DateTimeVector]
NC_Served_I=HouseLoad_I(:,1)+HouseLoad_I(:,2);
NC_Desired_I=HouseLoad_Desired_O(:,1)+HouseLoad_Desired_O(:,2);

NC_Desired_Points_I=0;
NC_Served_Points_I=0;
for ii=1:length(NC_Served_I)
    if(NC_Desired_I(ii,1)>0)
        NC_Desired_Points_I=NC_Desired_Points_I+1;
    end
    if((NC_Served_I(ii,1)<NC_Desired_I(ii,1)))
        % NC Load Not Served
    elseif ((NC_Served_I(ii,1)==NC_Desired_I(ii,1))&&(~(NC_Served_I(ii,1)<=0)))
        NC_Served_Points_I=NC_Served_Points_I+1;
    end
end

Percentage_NC_Served_I = 100-((NC_Served_Points_I)/(NC_Desired_Points_I)*(100));

% For Baseline-New [(HouseLoad_B(:,1)+HouseLoad_B(:,2)),(HouseLoad_B(:,7)-HouseLoad_B(:,3)),DateTimeVector]
NC_Served_BN=sum(HouseLoad_Actual_BN(:,1:2),2);
NC_Desired_BN=sum(HouseLoad_BN(:,1:2),2);

NC_Desired_Points_BN=0;
NC_Served_Points_BN=0;
for ii=1:length(NC_Served_BN)
    if(NC_Desired_BN(ii,1)>0)
        NC_Desired_Points_BN=NC_Desired_Points_BN+1;
    end
    if((NC_Served_BN(ii,1)<NC_Desired_BN(ii,1))&&(~(NC_Served_BN(ii,1)<0)))
        % NC Load Not Served
    elseif ((NC_Served_BN(ii,1)==NC_Desired_BN(ii,1))&&(~(NC_Served_BN(ii,1)<=0)))
        NC_Served_Points_BN=NC_Served_Points_BN+1;
    end
end

Percentage_NC_Served_BN = 100-((NC_Served_Points_BN)/(NC_Desired_Points_BN)*(100));

% % For RPi [HouseLoad_Desired_O(:,1)+HouseLoad_Desired_O(:,2),HouseLoad_O(:,1)+HouseLoad_O(:,2),DateTimeVector]
% NC_Served_RL=HouseLoad_RL;
% NC_Desired_RL=HouseLoad_Desired_O(:,1)+HouseLoad_Desired_O(:,2);
% 
% NC_Desired_Points_RL=0;
% NC_Served_Points_RL=0;
% for ii=1:length(NC_Served_RL)
%     if(NC_Desired_RL(ii,1)>0)
%         NC_Desired_Points_RL=NC_Desired_Points_RL+1;
%     end
%     if((NC_Served_RL(ii,1)<NC_Desired_RL(ii,1)))
%         % NC Load Not Served
%     elseif ((NC_Served_RL(ii,1)==NC_Desired_RL(ii,1))&&(~(NC_Served_RL(ii,1)<=0)))
%         NC_Served_Points_RL=NC_Served_Points_RL+1;
%     end
% end
% 
% Percentage_NC_Served_RL = 100-((NC_Served_Points_RL)/(NC_Desired_Points_RL)*(100));


% Pring Quantitative Results
fprintf('Average Fridge Death for Baseline = %f Hours/Day',Fridge_Death_AvgPerDay_B);
fprintf('\n')
fprintf('Average Fridge Death for MPC = %f Hours/Day',Fridge_Death_AvgPerDay_O);
fprintf('\n')
fprintf('Average Fridge Death for Intelligent = %f Hours/Day',Fridge_Death_AvgPerDay_I);
fprintf('\n')
fprintf('Average Fridge Death for Baseline-New = %f Hours/Day',Fridge_Death_AvgPerDay_BN);
fprintf('\n')
% fprintf('Average Fridge Death for RPi = %f Hours/Day',Fridge_Death_AvgPerDay_RL);
% fprintf('\n')
fprintf('Percentage of Non-Critical Loads not served for Baseline = %f %/Day',Percentage_NC_Served_B);
fprintf('\n')
fprintf('Percentage of Non-Critical Loads not served for MPC = %f %/Day',Percentage_NC_Served_O);
fprintf('\n')
fprintf('Percentage of Non-Critical Loads not served for Intelligent = %f %/Day',Percentage_NC_Served_I);
fprintf('\n')
fprintf('Percentage of Non-Critical Loads not served for Baseline-New = %f %/Day',Percentage_NC_Served_BN);
fprintf('\n')
% fprintf('Percentage of Non-Critical Loads not served for RPi = %f %/Day',Percentage_NC_Served_RL);
% fprintf('\n')



end
