import numpy as np
from math import pi
import warnings

def extract_model_output(filepath,temp,rate):
    try:
        # Extract temps for time = 0 
        heatup_files_location = filepath+'heat_up_step/heatup_ouput/'
        heatup_model_T0 = np.loadtxt(heatup_files_location+'T0_'+temp+'C_final.txt')
        heatup_model_T4 = np.loadtxt(heatup_files_location+'T4_'+temp+'C_final.txt')
    except OSError:
        heatup_model_T0 = [0]
        heatup_model_T4 = [0]
    
    try:
        # output in F, d, T0, T4, P, ALLPD, stress, strain
        deformation_output_location = filepath+'deformation_step/deformation_output/'
        model_data_out = np.transpose(np.atleast_2d(np.loadtxt(deformation_output_location+'F_'+temp+'C_'+rate+'s-1_output.txt')))
        outputs = ['d','T0','T4','P','ALLPD']
        for output in outputs:
            model_data_out= np.append(model_data_out,np.transpose(np.atleast_2d((np.loadtxt(deformation_output_location+output+'_'+temp+'C_'+
                                                                                            rate+'s-1_output.txt')))), axis=1)
        # Combine heatup and deformation model outputs
        header = np.zeros([1,np.shape(model_data_out)[1]])
        header[0,2] = heatup_model_T0[-1]
        header[0,3] = heatup_model_T4[-1]
        
        model_data_out= np.append(header,model_data_out, axis=0)
        
        # create coloums for stress and strain
        strain = -np.transpose(np.atleast_2d(np.log(1-(model_data_out[:,1])/0.01))) #length = 10mm
        stress = np.transpose(np.atleast_2d(model_data_out[:,0]/(np.exp(strain[:,0])*pi*(2.5*10**(-3))**(2))))
        
        # combine
        model_data_out = np.append(model_data_out,strain, axis=1)
        model_data_out = np.append(model_data_out,stress, axis=1)
        return model_data_out
    except OSError:
        warnings.warn("WARNING: The ouput data for " + temp+'C_'+rate+'s-1 could not be located')
        model_data_out = np.zeros([14,9])
        return model_data_out
