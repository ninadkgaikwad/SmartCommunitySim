###############################################################################################################
## Import Desired Packages
###############################################################################################################

import matlab.engine
import os

###############################################################################################################
## Custom Function - PecanStreet Load Data Preprocessing
###############################################################################################################
def PecanStreet_LoadData_Preprocessor_Func(DataFolderPath, FileName, OriginalResolution, NewResolution, ProcessingType, AveragingPoints, ResultFolderPath):
    """
    Reads and processes an Pecan Street Load File.

    Parameters:
        DataFolderPath (str): Path to the folder containing the data file.
        FileName (str): Name of the CSV file.
        OriginalResolution (float): Original time resolution (in minutes).
        NewResolution (float): Desired new time resolution (in minutes).
        ProcessingType (int): 1 (Full file), 2 (User-defined partial processing).
        AveragingPoints (int): Number of data points to average for resampling.
        ResultFolderPath (str, optional): Folder path to save results.

    Example:
        process_energy_data('C:/Data/', 'data.csv', 15, 10, 1, 2, 'C:/Results/')
    """
    ## Starting Matlab Engine
    eng = matlab.engine.start_matlab()

    ## Getting relevant paths for Legacy Code
    LoadData_Preprocessor_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "LoadData_Preprocessor")

    CodeFromSWEEFA_FolderPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Matlab", "CodeFromSWEEFA")
    
    ## Adding Paths to MATLAB Session
    eng.addpath(LoadData_Preprocessor_FolderPath, nargout=0)

    eng.addpath(CodeFromSWEEFA_FolderPath, nargout=0)

    ## Calling The Matlab Legacy Function
    eng.PecanStreetData_Preprocessing_Func(DataFolderPath, FileName, OriginalResolution, NewResolution, ProcessingType, AveragingPoints, ResultFolderPath, nargout=0)

    ## Closing Matlab Engine
    eng.quit()

    return None