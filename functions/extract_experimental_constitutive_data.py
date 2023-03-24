import numpy as np
from functions.constitutive_law import Constitutive_law
from functions.extract_model_output import extract_model_output
import seaborn as sns
import matplotlib.pyplot as plt

# Function to return predicted log(stress) for a give condition
def log_stress_eqn(temp,rate,surface_fit_strain):
    log_stress = (surface_fit_strain[0,1] + 
                     surface_fit_strain[0,2]*temp +
                     surface_fit_strain[0,3]*np.log10(rate) + 
                     surface_fit_strain[0,4]*np.log10(rate)*temp +
                     surface_fit_strain[0,5]*temp**2 + 
                     surface_fit_strain[0,6]*np.log10(rate)**2)
    return log_stress

def return_surface_fit(dataset):
    # Initialise
    surface_fit_values = np.zeros([1,6])
    
    # Set up y 
    y = np.zeros([len(dataset),1])
    y = np.log10(dataset[:,0])
    
    # Set up X
    X = np.zeros([len(dataset),6])
    X[:,0] = np.ones([1,len(dataset)])
    X[:,1] = dataset[:,2]
    X[:,2] = np.log10(dataset[:,3])
    X[:,3] = np.log10(dataset[:,3])*dataset[:,2]
    X[:,4] = dataset[:,2]**2
    X[:,5] = np.log10(dataset[:,3])**2
    
    # Solve the normal equation for this matrix to give c0-5
    Ɵ = np.linalg.inv(np.transpose(X).dot(X)).dot(np.transpose(X).dot(y))
    surface_fit_values = Ɵ
    
    return surface_fit_values

def surface_fit(strain,rate,temp,surface_fit_values):
    
    # Extract the fit for the specified strain
    surface_fit_strain = surface_fit_values[abs(surface_fit_values[:,0]-strain)<10**(-6)]
    
    # The stress is set to be constant at values larger than the greatest temp 
    # and strain rate experimentally found.
    log_stress = log_stress_eqn(temp,rate,surface_fit_strain)
    return log_stress

def extract_experimental_constitutive_data(filepath,nominal_temps,nominal_strain_rates,constitutive_inputs):
    
    # Stack the outputted data from the ABAQUS model
    first = 1  
    for temp in nominal_temps:
        for rate in nominal_strain_rates:
            # extract model data
            model_data = extract_model_output(filepath,str(temp),str(rate))
            
            if rate == '01':
                rate_value = 0.1
            else:
                rate_value = float(rate)
            
            if first == 1:
                first = 0
                model_data_full = np.append(model_data[1:,:],np.ones([len(model_data[1:,:]),1])*rate_value, axis=1)
                model_data_full = np.append(model_data_full,np.ones([len(model_data[1:,:]),1])*float(temp), axis=1)
            else:
                model_data_temp = np.append(model_data[1:,:],np.ones([len(model_data[1:,:]),1])*rate_value, axis=1)
                model_data_temp = np.append(model_data_temp,np.ones([len(model_data[1:,:]),1])*float(temp), axis=1)
                model_data_full = np.append(model_data_full,model_data_temp, axis=0)
    
    
    # This finds the difference between the outputted flow stress from the modek and the inputted flow stress
    del_sigma_output = np.zeros([len(model_data_full),7])
    for i in range(len(model_data_full)):
        del_sigma_output[i,0] = model_data_full[i,7]*10**(-6) # Model stress
        del_sigma_output[i,1] = Constitutive_law(constitutive_inputs,model_data_full[i,2],model_data_full[i,8])*10**(-6) # Input stress
        del_sigma_output[i,2] = model_data_full[i,2] # Real Temp
        del_sigma_output[i,3] = model_data_full[i,8] # Nominal Strain rate
        del_sigma_output[i,4] = model_data_full[i,9] # Nominal Temp
        del_sigma_output[i,5] = model_data_full[i,6] # Strain            
        del_sigma_output[i,6] = (model_data_full[i,7]-Constitutive_law(constitutive_inputs,model_data_full[i,2],model_data_full[i,8]))*10**(-6) # delT           
    
    # Extract the experimental nstress values interpolated to the model output locations 
    interpolated_stress = np.loadtxt(filepath + 'experimental_data/experimental_ouput/experimental_output_interp_stack_stress.txt')
    
    # Remove zero values
    interpolated_stress = np.delete(interpolated_stress, interpolated_stress[:,1]==0, axis=0)
    
    # Find the true constitutive data via removing the added stress due to inhomogeneity
    corrected_exp_data = np.zeros([len(model_data_full),5]) 
    corrected_exp_data[:,0] = interpolated_stress[:,0]*10**(-6) - del_sigma_output[:,5] #stress
    corrected_exp_data[:,1] = del_sigma_output[:,5] # strain
    corrected_exp_data[:,2] = del_sigma_output[:,2] # temp
    corrected_exp_data[:,3] = del_sigma_output[:,3] # nom rate
    corrected_exp_data[:,4] = del_sigma_output[:,4] # nom temp
        
    # Fit the surface using the normal equation for each strain
    strains = np.arange(0.05,0.7,0.05)
    surface_fit_values = np.zeros([len(strains),7])
    for i in range(len(strains)):
        surface_fit_values[i] = strains[i]
        # extract the dataset
        dataset = corrected_exp_data[abs(corrected_exp_data[:,1]-strains[i])<10**(-6)]
        
        # Find the surface fit
        surface_fit_values[i,1:7] = return_surface_fit(dataset)
        
    # Fit the surface for all strains and set this as the value for strain = 0
    surface_fit_values_all = np.zeros([1,7])
    surface_fit_values_all[0,1:7] = return_surface_fit(corrected_exp_data)
    surface_fit_values = np.append(surface_fit_values_all,surface_fit_values,axis=0)
    
    # Save the surface fit values to a text file
    np.savetxt(filepath + 'plots/statistical_fit.txt', surface_fit_values)
    
    # Extract the fit for the specified strain
    surface_fit_strain = surface_fit_values[abs(surface_fit_values[:,0]-0)<10**(-6)]
    
    # The stress is set to be constant at values larger than the greatest temp 
    # and strain rate experimentally found.
    #log_stress = log_stress_eqn(temp,rate,surface_fit_strain)

    fig, ax = plt.subplots(1,1,figsize=(5, 5))
    for rate in nominal_strain_rates:
        # Experiment
        exp_data = corrected_exp_data[abs(corrected_exp_data[:,3]-rate)<10**(-6)]
        plot = sns.scatterplot(x=exp_data[:,2],y=np.log10(exp_data[:,0]),ax=ax,label=str(rate)+'s$^{-1}$')
            
        # surface fit
        temp_range = np.arange(400,610,10)
        surface_fit_log_sigma_values = np.zeros(len(temp_range))
        for i in range(len(temp_range)):
            surface_fit_log_sigma_values[i] = surface_fit(0,rate,temp_range[i],surface_fit_values)
                               
        plot = sns.lineplot(x=temp_range,y=surface_fit_log_sigma_values,ax=ax,linestyle='dashed')
        
        plot.set(xlabel='T / $^\circ$C', ylabel='log($\sigma$ / MPa)')
        plot.set(xlim=(400, 600))
        plot.set(ylim=(0, 2))
        ax.legend(title='Nominal strain rate',frameon=False,loc=4)
    
    # Make a plot using all data
    fig.savefig(filepath+'plots/statistical_fit_vs_corrected_exp.png',bbox_inches='tight')
    
    # Close all the generated figures
    plt.close('all')
    
    ## Generate platisicty dataset
    strain_range = np.arange(0,0.7,0.05)
    temp_range = np.arange(min(nominal_temps)-50,max(nominal_temps)+50,5)
    log_rate_range = np.arange(min(np.log10(nominal_strain_rates))-1,max(np.log10(nominal_strain_rates))-1,0.4)
    log_rate_range = np.append([0],log_rate_range, axis=0)
    plasticity_data = np.zeros([len(strain_range)*len(temp_range)*len(log_rate_range)
                                ,4]) # stress, strain, rate, temp
    
    # Create dataframe
    count = 0
    for strain in strain_range:
        for temp in temp_range:
            rate_count = 0
            for log_rate in log_rate_range:
                if log_rate == 0:
                    log_rate = -4
                    zero = 1
                plasticity_data[count,0] = 10**(surface_fit(strain,10**(log_rate),temp,surface_fit_values))*10**6
                plasticity_data[count,1] = strain
                if zero == 1:
                    plasticity_data[count,2] = 0
                else:
                    plasticity_data[count,2] = 10**log_rate
                plasticity_data[count,3] = temp
                # Deal with maxima in the strain rate
                if rate_count > 0:
                    if plasticity_data[count-1,0] > plasticity_data[count,0]:
                        plasticity_data[count,0] = plasticity_data[count-1,0]
                        
                count = count + 1
                rate_count = rate_count + 1
                zero = 0
    
    np.savetxt(filepath + 'experimental_data/experimental_ouput/corrected_experimental_plasticity_data.txt', plasticity_data)