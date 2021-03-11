from functions.generate_heatup_input import generate_heatup_input
import os
import shutil

# For this Section you have to create three text files for the input
# Power - This is a list of numbers that will be adjusted by the model and can 
#         be any non zero value (commonly arounf 1e8)
# Temp  - A list of the target temperatures for each time in degrees C
# times - A list of the times at which the power will be fitted to match the 
#         desired temperatures
# These files have the following format for each nominal temperature:
# Power - P_heatup_(nominal_temp)C.txt
# time  - t_heatup_(nominal_temp)C.txt
# Temp  - Temp_heatup_(nominal_temp)C.txt
# These must be placed in the heat_up_step/heatup_input/ folder

# Find absolute filepaths
filepath = 'C:/temp/full_pipeline/'

# Conductance, This is a key parameter and may need adjusting to fit the 
# temperature field, this value was correct for Al6082.50
conductance = 1500.0

# Parameters
nom_temp_list = [520]

# Produce the input files with the experimental data
generate_heatup_input(filepath,nom_temp_list,conductance)

# Run the deformation model
os.system('call abaqus cae nogui=heatup_step.py')

# Move heatup odbs into the correct folder ready for the deformation step
new_location = filepath + 'heat_up_step/final_heatup_odb/'
for temp in nom_temp_list:
    try:
        os.rename(filepath + str(temp)+'C_heatup_final.odb', new_location + str(temp)+'C_heatup_final.odb')
        shutil.move(filepath + str(temp)+'C_heatup_final.odb', new_location+str(temp)+'C_heatup_final.odb')
        os.replace(filepath + str(temp)+'C_heatup_final.odb', new_location+str(temp)+'C_heatup_final.odb')
    except OSError:
        pass