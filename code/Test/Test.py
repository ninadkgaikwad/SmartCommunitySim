import matlab.engine
import os
import numpy as np

# Start MATLAB engine
eng = matlab.engine.start_matlab()

# Change MATLAB working directory to the current Python script directory

# Get the absolute directory of the current file
current_file_dir = os.path.dirname(os.path.abspath(__file__))
eng.cd(current_file_dir, nargout=0)

# Call the MATLAB function with two numbers
a = [1,2,3]
b = [1,2,3]

a = matlab.double(a)
b = matlab.double(b)

result, z = eng.Test_Mat(a, b,nargout=2)

result_a = eng.Test1_Mat(a, b)

# Print result
print("The sum is:", result)

print("The Z is:", z)

# Close the MATLAB engine
eng.quit()