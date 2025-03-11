###############################################################################################################
## Import Desired Packages
###############################################################################################################

import matlab.engine
import os

###############################################################################################################
## Custom Function - NSRDB Weather Data Preprocessing
###############################################################################################################
def NSRDB_WeatherdatProcessing_CityWise_Func(DataFolder_Path, ResultsFolder_Path, Original_Res, NewRes_List):
    """
    Reads and resamples weather data files in a folder to specified resolutions.

    Parameters:
        DataFolder_Path (str): Path to the folder containing the weather data files.
        ResultsFolder_Path (str): Path to save the resampled data.
        Original_Res (float): Original resolution of the dataset (in minutes).
        NewRes_List (list:float): List of new resolutions for resampling.

    Example:
        NSRDB_WeatherdatProcessing_CityWise_Func(
            "/path/to/data", "/path/to/results", 30.0, [5.0, 10.0, 15.0, 30.0]
        )
    """
    ## Starting Matlab Engine
    eng = matlab.engine.start_matlab()

    ## Getting relevant paths for Legacy Code
    WeatherData_Preprocessor_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "WeatherData_Preprocessor")

    CodeFromSWEEFA_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "CodeFromSWEEFA")
    
    ## Adding Paths to MATLAB Session
    eng.addpath(WeatherData_Preprocessor_FolderPath, nargout=0)

    eng.addpath(CodeFromSWEEFA_FolderPath, nargout=0)

    ## Converting to Correct MATLAB Datatypes
    NewRes_List = matlab.double(NewRes_List)

    ## Calling The Matlab Legacy Function
    eng.NSRDB_WeatherdatProcessing_CityWise_Func(DataFolder_Path, ResultsFolder_Path, Original_Res, NewRes_List, nargout=0)

    ## Closing Matlab Engine
    eng.quit()

    return None