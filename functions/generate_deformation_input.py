import numpy as np
import os
from math import pi

def groupedAvg_by_strain_step(myArray, strain_step, strain_col):
    # averages
    max_strain = np.max(myArray[:,strain_col])
    strain_bands = np.arange(0, max_strain, strain_step).tolist()
    
    result = np.zeros([len(strain_bands)-1,np.shape(myArray)[1]])
    errors = np.zeros(np.shape(result))
    for i in range(1,len(strain_bands)):
        # Array section
        section = myArray[myArray[:,strain_col] > strain_bands[i-1],:]
        section = section[section[:,strain_col] < strain_bands[i],:]
        
        # Average
        mean = np.mean(section,axis=0,keepdims=True)
        # Standard dev
        std = np.std(section,axis=0,keepdims=True)
        
        result[i-1,:] = mean
        errors[i-1,:] = std
        
    return result, errors

def generate_deformation_input(filepath,nominal_strain_rates,nominal_temps,
                               sample_length,sample_radius,max_strain,strain_step,
                               use_custom_inputs):
      
    initial = 1
    for rate in nominal_strain_rates :
        for temp in nominal_temps:
            
            first = 1
            
            directory = filepath + 'experimental_data/deformation/'+ str(rate) + '/'+ str(temp)+ '/'
            files = os.listdir(directory)
            
            for file in files:
                if first == 1:
                    all_data = np.loadtxt(directory + file, skiprows=3)
                    first = 0
                else:
                    all_data= np.append(all_data,np.loadtxt(directory + file, skiprows=3), axis=0)
                        
            #remove unneeded data
            all_data_processed = np.delete(all_data,[0,7,8,9,10,11,12], 1)            
            
            # find the true strain
            strain = np.log(1-sample_length*(all_data_processed[:,4])) #length = 10mm
            
            # stress
            # assume no barelling to account for how the radius changes
            stress = all_data_processed[:,3]/(np.exp(-strain)*pi*(sample_radius)**(2))
            
            # rate
            strain_rate = np.ones([len(stress)])*rate
            
            # Make a col for the nominal rate
            nom_temp = np.ones([len(stress)])*temp
            
            # combine
            combined = np.stack([stress, -strain, strain_rate, all_data_processed[:,1],nom_temp],axis=1)
            
            # remove negative stress values which are due to errors
            combined = combined[combined[:,0]>0]
            
            if initial == 1:
                output = combined
                initial = 0
            else:
                output= np.append(output,combined, axis=0)
            
    
    first = 1
    for temp in nominal_temps:
        for rate in nominal_strain_rates:
            # group by condition
            group = output[abs(output[:,2] - rate)<10**(-7)]
            group = group[abs(group[:,4] - temp)<10**(-7)]
            
            # sort by strain
            ind   = np.argsort(group[:,1])
            group = group[ind]
            
            # set the number of strain incriments that will be averaged over
            # This will generate 100 evenly spaced points in strain
            group, error = groupedAvg_by_strain_step(group, strain_step/5, 1)
            
            if first == 1:
                all_groups = group
                all_errors = error
                first = 0
            else:
                all_groups= np.append(all_groups,group, axis=0)
                all_errors= np.append(all_errors,error, axis=0)
    
    # Interpolation values in strain
    interp_values = np.arange(0,max_strain+strain_step,strain_step)
    
    # add the error dataset onto the full data
    all_groups= np.append(all_groups,all_errors, axis=1)
    
    first = 1
    for temp in nominal_temps:
        for rate in nominal_strain_rates:
            
            # Extract
            group = all_groups[abs(all_groups[:,4] - temp)<10**(-7)]
            group = group[abs(group[:,2] - rate)<10**(-7)]
            
            
            # Interpolation of temp
            sorted_group = group[np.argsort(group[:, 1])] # sort by strain value
            interp_temp = np.interp(interp_values, sorted_group[:,1] , sorted_group[:,3])
            interp_temp_errors = np.interp(interp_values, sorted_group[:,1] , sorted_group[:,8])
            interp_temp = np.stack([interp_temp, interp_values, np.ones([len(interp_temp)])*rate,
                                    np.ones([len(interp_temp)])*temp,interp_temp_errors],axis=1)
            
            # Interpolation of stress
            interp_stress = np.interp(interp_values, sorted_group[:,1] , sorted_group[:,0])
            interp_stress_errors = np.interp(interp_values, sorted_group[:,1] , sorted_group[:,5])
            interp_stress = np.stack([interp_stress, interp_values, np.ones([len(interp_stress)])*rate,
                                    np.ones([len(interp_stress)])*temp,interp_temp_errors],axis=1)
            
            if first == 1:
                interp_stack_temp = interp_temp
                interp_stack_stress = interp_stress
                first = 0
            else:
                interp_stack_temp= np.append(interp_stack_temp,interp_temp, axis=0)
                interp_stack_stress= np.append(interp_stack_stress,interp_stress, axis=0)
                
            # For each condition generate the input txt files for deformation
            # Time 
            input_folder_location = filepath + 'deformation_step/deformation_input/'
            
            if use_custom_inputs != 1:
                time_steps = np.arange(0,(max_strain+strain_step)/rate,strain_step/rate)
                with open(input_folder_location+'t_'+str(temp)+'C_'
                          +str(rate)+'s-1.txt', 'w') as f:
                    f.write('\n'.join(['{}'.format(x) for x in time_steps]))
                
                # Temp - This is th most important value
                temp_steps = interp_temp[:,0]
                with open(input_folder_location+'Temp_'+str(temp)+'C_'
                          +str(rate)+'s-1.txt', 'w') as f:
                    f.write('\n'.join(['{}'.format(x) for x in temp_steps]))
                        
                # Power - this is arbitary and will change as the model runs
                power_steps = np.ones(len(time_steps))*5*10**(8)
                with open(input_folder_location+'P_'+str(temp)+'C_'
                          +str(rate)+'s-1.txt', 'w') as f:
                    f.write('\n'.join(['{}'.format(x) for x in power_steps]))
        
    
    # Save the interpolated data as a txt file in the ouput folder
    save_location = 'experimental_data/experimental_ouput/'
    np.savetxt(save_location+'experimental_output_interp_stack_temp.txt',interp_stack_temp)
    np.savetxt(save_location+'experimental_output_interp_stack_stress.txt',interp_stack_stress)
    np.savetxt(save_location+'experimental_output_all_data.txt',all_groups)
    
    return

