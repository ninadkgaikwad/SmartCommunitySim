%% NSRDB - Weather Data Processing Script - City Wise

% Author: Ninad Kiran Gaikwad
% Date: Jan/31/2020
% Description: NSRDB - Weather Data Processing Script - City Wise

function NSRDB_WeatherdatProcessing_CityWise_Func(DataFolder_Path, ResultsFolder_Path, Original_Res, NewRes_List)
    % process_weather_data - Reads and resamples weather data from the specified folder.
    %
    % Inputs:
    %   DataFolder_Path (string)  - Path to the folder containing weather data files.
    %   ResultsFolder_Path (string) - Path to save resampled data.
    %   Original_Res (int) - Original resolution of the dataset (in minutes).
    %   NewRes_List (vector) - List of new resolutions for resampling.
    %
    % Example:
    %   process_weather_data('/path/to/data', '/path/to/results', 30, [5, 10, 15, 30]);
 
    %% Step 1 - Getting List of all Sub-Folders

    DataFolderStructure1=dir(DataFolder_Path);

    FileNames_Cell1=extractfield(DataFolderStructure1,'name');

    FolderPath1=DataFolderStructure1.folder;

    % Initialization
    FolderCounter=0;

    %% Step 2 - Starting the Main Folder Loop for Weather File Processing

    for i=1:length(FileNames_Cell1) % For each folder in the Folder
        
        FileName1=FileNames_Cell1{i};
        
        startIndex1 = regexp(FileName1,'\<[^a-zA-Z_0-9]\w*'); % To check for temporary files
        
    if (length(startIndex1)==0) % If actual File
        
            % Incrementing FileCounter
            FolderCounter=FolderCounter+1         
        
        % Getting CityStateName
        CityStateName=FileName1;
        
        % Subfolder Path
        FolderPath2=fullfile(FolderPath1,FileName1);
        
        % Getting Files inside the CityState Folder
            DataFolderStructure2=dir(FolderPath2);

            FileNames_Cell2=extractfield(DataFolderStructure2,'name');

            FolderPath2=DataFolderStructure2.folder; 
            
            % Initialization
            FileCounter=0;
            
            %% Step 3 - Starting the Main Subfolder Loop for Weather File Processing
            
            for i=1:length(FileNames_Cell2) % For each file in the Subfolder
                
                FileName3=FileNames_Cell2{i};

                startIndex2 = regexp(FileName3,'\<[^a-zA-Z_0-9]\w*'); % To check for temporary files

                if (length(startIndex2)==0) % If actual File
                    
                    % Incrementing FileCounter
                    FileCounter=FileCounter+1               

                    % Getting Real File Name
                    FileName4=FileName3;
                    
                    % Getting Information from the File Name
                    FileName4_Contents=split(FileName4,'_');
                    Lat=FileName4_Contents{2};
                    Long=FileName4_Contents{3};
                    Year=FileName4_Contents{4};

                    % Subfolder Path
                    WeatherFilePath=fullfile(FolderPath2,FileName4);               
                    
                    % Reading the Weather File
                    ActualFile= csvread(WeatherFilePath,3);
                    
                    %% Step 4: Changing Date-Time Stamp Columns for Utility

                    DateTimeStamp=zeros(1,4); % Initialization

                    for i=1:length(ActualFile) % For each row in ActualFile

                        Hour=ActualFile(i,4);

                        Min=ActualFile(i,5);

                        [ TimeDeci ] = HMToDeci( Hour,Min,0 );

                        DateTimeStamp(i,1:4)=[ActualFile(i,3),ActualFile(i,2),ActualFile(i,1),TimeDeci];

                    end

                    ActualFile=ActualFile(:,6:end); % Removing older Date-Time Stamp

                    ActualFile=horzcat(DateTimeStamp,ActualFile); % Adding New Date-Time Stamp               
                    
                    %% Step 5 - Preprocessing Time Resolution of the Files

                    for ii = 1:len(NewRes_List)
                    
                        % Resolution Change
                        [NewResFile_Res30] = NSRDB_Low2HighRes(Original_Res,NewRes_List(ii),1,ActualFile);
                        
                        %% Step 6 - Creating New Directories and Sub-Directories
                        CurrentPath=pwd;
                        
                        cd(ResultsFolder_Path);
                        
                        mkdir(CityStateName);
                        
                        cd(fullfile(ResultsFolder_Path,CityStateName));

                        Res_FolderName = strcat('Res_', num2str(NewRes_List(ii)));
                        
                        mkdir(Res_FolderName);
                        
                        cd(CurrentPath);
                        
                        %% Step 7 - Saving Processed Weather Data Files 
                        % Getting the Correct File Names              
                        NewResWeatherDataFileName_Res=[CityStateName,'_Lat-',num2str(Lat),'_Long-','_',num2str(Long),num2str(Year),'_To_',num2str(Year),'_WeatherData_NSRDB_', num2str(Original_Res),'minTo', num2str(NewRes_List(ii)) ,'minRes.csv'];
                        
                        % Getting Correct Folder Paths
                        ResultsFolder_Path_Res=fullfile(ResultsFolder_Path, CityStateName, Res_FolderName);                    
                        
                        % Writing the Processed Weather Data to appropriate Files
                        csvwrite(fullfile(ResultsFolder_Path_Res,NewResWeatherDataFileName_Res),NewResFile_Res);
                        
                    end

                end
            
            end  
            
    end
        
    end

end

