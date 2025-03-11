performance_metric_name = '$LRM_{E_l}$'; % TRM_{T_h}, LRM_{E_l}, LRM_{E_{cri}}
performance_metric_name_1 = 'SRM_All'; % PRM, SRM_All, SRM_C
%F_prep_fig4printing_Starter;

% Resiliency Performance Metric Figure

% System Size Vs. Resiliency Performance
SystemSize_Vector=[1,2,3,4,5,6];
%ResiliencyPerformance_Vector1_B=[7.125,6.020,4.750,2.375,0.230,0.0416]
ResiliencyPerformance_Vector1_MPC=[0.74,0.7,0.54,0.47,0.57,0.64];
ResiliencyPerformance_Vector1_Smart=[0.74,0.74,0.74,0.74,0.74,0.74];
ResiliencyPerformance_Vector1_Dumb=[0.74,0.71,0.56,0.21,0.17,0.15];

h1=figure(1);
hold on
box on

% P1=plot(SystemSize_Vector,ResiliencyPerformance_Vector_B,'or','LineWidth',2);
% P2=plot(SystemSize_Vector(1),ResiliencyPerformance_Vector_O(1),'*b','LineWidth',2);

P3=plot(SystemSize_Vector,ResiliencyPerformance_Vector1_MPC,'d-k','LineWidth',2);
P2=plot(SystemSize_Vector,ResiliencyPerformance_Vector1_Dumb,'v-b','LineWidth',2);
P1=plot(SystemSize_Vector,ResiliencyPerformance_Vector1_Smart,'o-r','LineWidth',2);

xticks([1 2 3 4 5 6])
xticklabels({'3','4','5','6','7','8'})
% ylim([0 150]);
ylim([0 1.5]);
%xlim([3 8]);
ax1 = ancestor(P1, 'axes');
xrule_1 = ax1.XAxis;
xrule_1.FontSize=14;
yrule_1 = ax1.YAxis;
yrule_1(1).FontSize=14;  

xlabel('AC Startup Factor ($\alpha_{I}$)','Interpreter','latex','FontSize', 14);
% ylabel('Resiliency Performance $(\%)$','Interpreter','latex','FontSize', 14);

%\begin{tabular}{c} Critical load not served \\ $(hours/day)$ \end{tabular}
ylabel(performance_metric_name,'Interpreter','latex','FontSize', 14);
%ylabel('Critical load not served $(hours/day)$','Interpreter','latex','FontSize', 14);

legend1=legend('MPC Controller','Baseline Controller','Rule-based Smart Controller');
legend boxoff
set(legend1,'Interpreter','latex','FontSize', 14);

box off
hold off;



%% Printing Figures to PDF

Figures={h1};

FigureName={strcat(performance_metric_name_1,'.pdf')};

for ii=1:1
   
    F_prep_fig4printing(Figures{ii}); % Preparing Figure
    
    print(Figures{ii},'-dpdf', FigureName{ii}); % Printing figure in PDF
    
end

 % print h2 -dpdf SoC_Baseline_Optimal.pdf


