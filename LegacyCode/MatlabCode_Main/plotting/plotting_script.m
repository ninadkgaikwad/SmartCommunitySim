%F_prep_fig4printing_Starter;
controller_type = 'MPC';
simulation_data_file_name = "FigurePlotterData_MPC_AC8.mat";
%simulation_data_file_name = "FigurePlotterData_DC_AC3.mat";
simulation_data = load(simulation_data_file_name);
HEMS_Plant_FigurePlotter(simulation_data,controller_type);