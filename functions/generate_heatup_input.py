import numpy as np

def generate_heatup_input(filepath,nominal_temps,conductance):
         
    # For each condition generate the input txt files for deformation
    # Time 
    input_folder_location = filepath+'heat_up_step/heatup_input/'
    
    with open(input_folder_location+ 'conductance.txt', 'w') as f:
        f.write("%f" % conductance)
    
    with open(input_folder_location+'temps_values.txt', 'w') as f:
        for temp in nominal_temps:
            f.write("%s\n" % temp)
    
    return
