function [ ] = HEMS_Plant_FigurePlotter_debug(simulation_data,controller_type)

% Author: Ninad Kiran Gaikwad
% Date: Mar/15/2021
% Description: HEMS_Plant_FigurePlotter_Input - Plotting Figures for the
% Baseline
close all;

EToP_Converter=(60/10); % kWh --> W

%% HEMS_Plant_FigurePlotter - Plotting Figures for Controller and Plant

%% Getting the desired data from the HEMS_Plant_Baseline_FigurePlotter_Input - Struct
HEMS_Plant_FigurePlotter_Input = simulation_data.HEMS_Plant_FigurePlotter_Input;
%----------------HEMS_Plant_Baseline_FigurePlotter_Input------------------%
X_k_Plant_History=HEMS_Plant_FigurePlotter_Input.X_k_Plant_History;
U_k_History=HEMS_Plant_FigurePlotter_Input.U_k_History; 
E_LoadData=HEMS_Plant_FigurePlotter_Input.E_LoadData;
E_Load_Desired=HEMS_Plant_FigurePlotter_Input.E_Load_Desired;
HEMSWeatherData_Output=HEMS_Plant_FigurePlotter_Input.HEMSWeatherData_Output;
HEMSPlant_Params=HEMS_Plant_FigurePlotter_Input.HEMSPlant_Params;
Community_Params=HEMS_Plant_FigurePlotter_Input.Community_Params;
Baseline_Output_Images_Path=HEMS_Plant_FigurePlotter_Input.Baseline_Output_Images_Path;
Single_House_Plotting_Index=HEMS_Plant_FigurePlotter_Input.Single_House_Plotting_Index;
Simulation_Params=HEMS_Plant_FigurePlotter_Input.Simulation_Params;
E_LoadData = E_LoadData(1:1152);
E_Load_Desired = E_Load_Desired(1:1152);
%-----------------------HEMSWeatherData_Output----------------------------%
Ws=HEMSWeatherData_Output.Ws;
T_am=HEMSWeatherData_Output.T_am;
GHI=HEMSWeatherData_Output.GHI;
DNI=HEMSWeatherData_Output.DNI;
DateTimeVector=HEMSWeatherData_Output.DateTimeVector;
DateTime_Matrix=HEMSWeatherData_Output.DateTime_Matrix;

Ws=Ws(1:1152);
T_am=T_am(1:1152);
GHI=GHI(1:1152);
DNI=DNI(1:1152);
DateTimeVector=DateTimeVector(1:1152);
DateTime_Matrix=DateTime_Matrix(1:1152);

%---------------------------HEMSPlant_Params------------------------------%

E_AC=HEMSPlant_Params.E_AC;
T_AC_max=HEMSPlant_Params.T_AC_max;
T_AC_min=HEMSPlant_Params.T_AC_min;
ACLoad_StartUp_Power=HEMSPlant_Params.ACLoad_StartUp_Power;
Eff_Inv=HEMSPlant_Params.Eff_Inv;

Battery_Energy_Max=HEMSPlant_Params.Battery_Energy_Max;
Battery_Energy_Min=HEMSPlant_Params.Battery_Energy_Min;
MaxRate_Charging=HEMSPlant_Params.MaxRate_Charging;
MaxRate_Discharging=HEMSPlant_Params.MaxRate_Discharging;
Eff_Charging_Battery=HEMSPlant_Params.Eff_Charging_Battery;
Eff_Discharging_Battery=HEMSPlant_Params.Eff_Discharging_Battery;
MaxRate_Discharging_StartUp=HEMSPlant_Params.MaxRate_Discharging_StartUp;

%---------------------------Community_Params.-----------------------------%
N_House=Community_Params.N_House;
N_PV_Bat=Community_Params.N_PV_Bat;
N_Bat=Community_Params.N_Bat;
N_PV=Community_Params.N_PV;
N_None=Community_Params.N_None; 

%---------------------------Simulation_Params-----------------------------%

Simulation_StepSize=Simulation_Params.Simulation_StepSize;

%% Basic Computation and Generating plotable quantities

% House Numbers
N1=N_PV_Bat;
N2=N_Bat;
N3=N_PV;
N4=N_None;

% Truncating Plant History
X_k_Plant_History=X_k_Plant_History(1:end-1,:,:);

% PV Quantities - Individual Houses
House_PV_E_Available=X_k_Plant_History(:,1,:);
House_PV_E_Used=X_k_Plant_History(:,2,:);
House_PV_E_UnUsed=X_k_Plant_History(:,3,:);

% Battery Quantities - Individual Houses
House_Bat_E_State=X_k_Plant_History(:,4,:);
House_Bat_E_Charging=X_k_Plant_History(:,5,:);
House_Bat_E_Discharging=X_k_Plant_History(:,6,:);

% House Temperature Quantities - Individual Houses
House_Temprature=X_k_Plant_History(:,7,:);

% House Energy Quantities - Individual Houses
House_Bat_E_OtherLoad_Desired=E_Load_Desired(1:1152,1,:);
House_Bat_E_ACLoad_Desired=U_k_History(:,3,:).*(E_AC/Eff_Inv);%***
House_Bat_E_TotalLoad_Desired=House_Bat_E_OtherLoad_Desired(1:1008)+House_Bat_E_ACLoad_Desired(1:1008);

House_Bat_E_OtherLoad_Actual=X_k_Plant_History(:,12,:);
House_Bat_E_ACLoad_Actual=X_k_Plant_History(:,11,:);
House_Bat_E_TotalLoad_Actual=House_Bat_E_OtherLoad_Actual+House_Bat_E_ACLoad_Actual;

% House Controller Quantities - Individual Houses
House_Bat_Controller_Charging_Desired=U_k_History(:,1,:);
House_Bat_Controller_Discharging_Desired=U_k_History(:,2,:);

House_AC_Controller_TurnOn_Desired=U_k_History(:,3,:);
House_AC_Controller_TurnOn_Actual=X_k_Plant_History(:,21,:);


% PV Quantities - All Houses (Addup)
Community_PV_E_Available=sum(X_k_Plant_History(:,1,:),3);
Community_PV_E_Used=sum(X_k_Plant_History(:,2,:),3);
Community_PV_E_UnUsed=sum(X_k_Plant_History(:,3,:),3);

% Battery Quantities - Individual Houses - All Houses (Addup)
Community_Bat_E_State=sum(X_k_Plant_History(:,4,:),3);
Community_Bat_E_Charging=sum(X_k_Plant_History(:,5,:),3);
Community_Bat_E_Discharging=sum(X_k_Plant_History(:,6,:),3);

% House Temperature Quantities - Individual Houses - All Houses (Average)
Community_Temprature=mean(X_k_Plant_History(:,7,:),3);

% House Energy Quantities - Individual Houses - All Houses (Addup)
Community_Bat_E_OtherLoad_Desired=sum(E_Load_Desired(1:1152,1,:),3);
Community_Bat_E_ACLoad_Desired=sum(House_Bat_E_ACLoad_Desired(:,1,:),3);
Community_Bat_E_TotalLoad_Desired=Community_Bat_E_ACLoad_Desired+Community_Bat_E_OtherLoad_Desired;

Community_Bat_E_OtherLoad_Actual=sum(X_k_Plant_History(:,12,:),3);
Community_Bat_E_CriticalLoad_Actual=sum(X_k_Plant_History(:,13,:),3);

Community_Bat_E_ACLoad_Actual=sum(X_k_Plant_History(:,11,:),3);
Community_Bat_E_TotalLoad_Actual=Community_Bat_E_OtherLoad_Actual+Community_Bat_E_ACLoad_Actual;

% House Controller Quantities - Individual Houses - All Houses (Addup)
Community_Bat_Controller_Charging_Desired=sum(U_k_History(:,1,:),3);
Community_Bat_Controller_Discharging_Desired=sum(U_k_History(:,2,:),3);

Community_AC_Controller_TurnOn_Desired=sum(U_k_History(:,3,:),3);
Community_AC_Controller_TurnOn_Actual=sum(X_k_Plant_History(:,21,:),3);

% Computing House and Community Battery SoC
House_Bat_SoC=(((House_Bat_E_State)-Battery_Energy_Min)/(Battery_Energy_Max-Battery_Energy_Min))*100;
Community_Bat_SoC=(((Community_Bat_E_State)-((N1+N2)*Battery_Energy_Min))/(((N1+N2)*Battery_Energy_Max)-((N1+N2)*Battery_Energy_Min)))*100;

% Computing House and Community Generation and Demand
House_E_Generation=House_PV_E_Used+House_Bat_E_Discharging;
House_E_Demand=House_Bat_E_Charging+House_Bat_E_TotalLoad_Actual;

Community_E_Generation=Community_PV_E_Used+Community_Bat_E_Discharging;
Community_E_Demand=Community_Bat_E_Charging+Community_Bat_E_TotalLoad_Actual;

% House/Community Level Battery Charging_Dispatchable/Discharging_Dispatchable
House_Bat_E_Charging_Dispatchable=zeros(length(GHI),1,N_House); % Initialization
House_Bat_E_Discharging_Dispatchable=zeros(length(GHI),1,N_House); % Initialization
for ii=1:length(GHI)
    if (Community_PV_E_Available(ii,1,1)>=Community_Bat_E_TotalLoad_Desired(ii,1,1))

        for jj=1:(N_PV_Bat+N_Bat)
            
            House_Bat_E_Charging_Dispatchable(ii,1,jj)=min(MaxRate_Charging*Simulation_StepSize,(Battery_Energy_Max-(X_k_Plant_History(ii,4,jj)))/Eff_Charging_Battery);
            House_Bat_E_Discharging_Dispatchable(ii,1,jj)=0;
            
        end

    else

        for jj=1:(N_PV_Bat+N_Bat)
            
            House_Bat_E_Charging_Dispatchable(ii,1,jj)=0;
            House_Bat_E_Discharging_Dispatchable(ii,1,jj)=min(MaxRate_Discharging*Simulation_StepSize,(X_k_Plant_History(ii,4,jj)-Battery_Energy_Min)*Eff_Discharging_Battery);
            
        end

    end
    
end

Community_Bat_E_Charging_Dispatchable=sum(House_Bat_E_Charging_Dispatchable(:,1,:),3);%***
Community_Bat_E_Discharging_Dispatchable=sum(House_Bat_E_Discharging_Dispatchable(:,1,:),3);%***

% House AC Startup Power Quantities
Community_AC_P_StartUp_Available=(Community_PV_E_Available/Simulation_StepSize)+(Community_Bat_Controller_Discharging_Desired*MaxRate_Discharging_StartUp);

House_AC_StartUp_Desired=House_AC_Controller_TurnOn_Desired(:,1,:)-X_k_Plant_History(:,30,:);
House_AC_StartUp_Desired = (abs(House_AC_StartUp_Desired)+House_AC_StartUp_Desired)/2;
Community_AC_StartUp_Desired = sum(House_AC_StartUp_Desired(:,1,:),3);
Community_AC_P_StartUp_Required=Community_AC_StartUp_Desired*ACLoad_StartUp_Power;

House_AC_StartUp_Actual=X_k_Plant_History(:,21,:)-X_k_Plant_History(:,30,:);
House_AC_StartUp_Actual = (abs(House_AC_StartUp_Actual)+House_AC_StartUp_Actual)/2;
Community_AC_StartUp_Actual = sum(House_AC_StartUp_Actual(:,1,:),3);
Community_AC_P_StartUp_Used=Community_AC_StartUp_Actual*ACLoad_StartUp_Power;

% Creating Grouping Indices
N_All_Indices=1:N_House;
N_PV_Bat_Only_Indices=1:N1;
N_Bat_Only_Indices=N1+1:N2;
N_PV_Only_Indices=N2+1:N3;
N_None_Only_Indices=N3+1:N4;

%% DateTime Vector to Hours

D=DateTimeVector(2)-DateTimeVector(1);

M=minutes(D);

H=M/60;

L=length(DateTimeVector);

HoursVector=zeros(L,1);
HoursVector=zeros(L,1);

for ii=2:L
    HoursVector(ii,1)=HoursVector(ii-1,1)+H;
end

Len_Hours_Vector=length(HoursVector);

%% Plotting the Figures - Individual Houses and Community
% Fridge Temperature , House Temperature , Battery SOC - Baseline    
h1=figure(1);
hold on
box on

yyaxis left
P2 = plot(HoursVector(1:1008),Community_Temprature(1:1008,1),'-b','LineWidth',2); % temp variable
plot(HoursVector(1:1008),T_AC_max*ones(1008,1),'--k','LineWidth',1);
plot(HoursVector(1:1008),T_AC_min*ones(1008,1),'--k','LineWidth',1);

xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([22 35]); 
xlim([0 170]);
%title('Temperature Outside/House/Refrigerator');
xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ax1 = ancestor(P2, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;
yrule_1(1).Color='b';
ylabel('$T_h \; (^{\circ}C)$','Interpreter','latex','FontSize', 16);



yyaxis right
P3 = plot(HoursVector(1:1008),Community_Bat_SoC(1:1008,1),'LineStyle','-','Color',[1,0.5729,0],'LineWidth',2); % SOC variable
P4 = plot(HoursVector(1:1008),100*ones(1008,1),'--r','LineWidth',1);
P5 = plot(HoursVector(1:1008),0*ones(1008,1),'--r','LineWidth',1);
ylim([-5 125]);
xlim([0 170]);
ax1 = ancestor(P3, 'axes');
yrule_2 = ax1.YAxis;
yrule_2(2).FontSize=14;  
yrule_2(2).Color=[1,0.5729,0];
ylabel('$SoC \; (\%)$','Interpreter','latex','FontSize', 16);

legend1=legend([P2,P3],'House - Temp.','Battery - SoC');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;  

% Desired Vs. Serviced Non-Critical Loads - Baseline
h2=figure(2);
hold on 
box on


P2=plot(HoursVector(1:1008),EToP_Converter*(Community_Bat_E_OtherLoad_Actual(1:1008)),'-b','LineWidth',2);  % serviced other loads
P1=plot(HoursVector(1:1008),EToP_Converter*(Community_Bat_E_OtherLoad_Desired(1:1008)),'--r','LineWidth',1.5); % desired other loads
%P3=plot(HoursVector(1:1008),EToP_Converter*(E_LoadData(1:1008)),'--k','LineWidth',2);  % critical loads desired


xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([0 14]);
xlim([0 170]);
ax1 = ancestor(P1, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;    

xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ylabel('$kW$','Interpreter','latex','FontSize', 16);

%legend1=legend([P2,P1],'Serviced - Other Loads ($E_l$)','Desired - Other Loads ($\bar E_l$)','Desired - Critical Loads ($\bar E_{cri}$)');
legend1=legend([P2,P1],'Serviced - Other Loads ($E_l$)','Desired - Other Loads ($\bar E_l$)');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;  


% Desired Vs. Serviced Critical Loads - Baseline
h3=figure(3);
hold on 
box on


P7=plot(HoursVector(1:1008),EToP_Converter*(Community_Bat_E_CriticalLoad_Actual(1:1008)),'-b','LineWidth',2);  % serviced other loads
P6=plot(HoursVector(1:1008),EToP_Converter*(E_LoadData(1:1008)),'--r','LineWidth',1.5);  % critical loads desired


xticks([0 24 48 72 96 120 144 168])
xticklabels({'0','24','48','72','96','120','144','168'})
ylim([0 5]);
xlim([0 170]);
ax1 = ancestor(P1, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;    

xlabel('Time ($hours$)','Interpreter','latex','FontSize', 14);
ylabel('$kW$','Interpreter','latex','FontSize', 16);

%legend1=legend([P2,P1],'Serviced - Other Loads ($E_l$)','Desired - Other Loads ($\bar E_l$)','Desired - Critical Loads ($\bar E_{cri}$)');
legend1=legend([P7,P6],'Serviced - Critical Loads ($E_{cri}$)','Desired - Critical Loads ($\bar E_{cri}$)');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;  

%% Printing Figures to PDF

Figures={h1,h2,h3};

FigureName={strcat(controller_type,'_temperature.pdf'), strcat(controller_type,'other_load.pdf'), strcat(controller_type,'critical_load.pdf')};

for ii=1:3
   
    F_prep_fig4printing(Figures{ii}); % Preparing Figure
    
    print(Figures{ii},'-dpdf', FigureName{ii}); % Printing figure in PDF
    
end


end

