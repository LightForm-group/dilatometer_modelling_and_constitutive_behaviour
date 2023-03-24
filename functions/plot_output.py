import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from math import pi
import pickle
from functions.extract_model_output import extract_model_output

def plot_output(filepath,nominal_temps,nominal_strain_rates,strain_step,max_strain,sample_length,sample_radius):
        
    # Set plot characteristics
    sns.set(style="white",font_scale=1.2)
    sns.set_palette('Accent')
    
    # Load in experimental output
    # in both cases they have the following stucture stress, strain, strain rate, temp, nominal temp
    interpolated_exp_dataset = np.loadtxt(filepath+'experimental_data/experimental_ouput/experimental_output_interp_stack_temp.txt')
    full_exp_dataset         = np.loadtxt(filepath+'experimental_data/experimental_ouput/experimental_output_all_data.txt')
    
    # Handle the case where it is just one condition
    if len(nominal_strain_rates) == 1 or len(nominal_temps) == 1:
        one_condition = True
    else:
        one_condition = False
    
    a4_dims = (5*len(nominal_strain_rates), 6*len(nominal_temps))
    fig3, ax3 = plt.subplots(len(nominal_strain_rates),len(nominal_temps),figsize=a4_dims)
    fig3.subplots_adjust(wspace=0.4, hspace=0.4)
    sub_plot_x_axis = -1
    
    # Turn the lists into floats
    nominal_strain_rates_float = [float(x) for x in nominal_strain_rates]
    nominal_temps_float        = [float(x) for x in nominal_temps]
    
    rate_count = 0 # count through to name some variables
    for rate in nominal_strain_rates_float:
        
        rate_name = str(nominal_strain_rates[rate_count])
        rate_count = rate_count + 1
        
        # Plotting setup
        sns.set(style="white",font_scale=1.2)
        sns.set_palette('Accent')
        fig1, ax1 = plt.subplots()
        fig2, ax2 = plt.subplots()
        
        # for the power plots
        sub_plot_y_axis = 0
        sub_plot_x_axis = sub_plot_x_axis + 1
        
        temp_count = 0
        for temp in nominal_temps_float:
            
            temp_name = str(nominal_temps[temp_count])
            temp_count = temp_count + 1
            
            # extract model data
            model_data = extract_model_output(filepath,temp_name,rate_name)
            
            ## select the experimental data
            # filter by temp
            interpolated_exp_data = interpolated_exp_dataset[abs(interpolated_exp_dataset[:,3] - temp)<10**(-3),:] 
            full_exp_data         = full_exp_dataset[abs(full_exp_dataset[:,4] - temp)<10**(-3),:]
            
            #filter by strain
            interpolated_exp_data = interpolated_exp_data[abs(interpolated_exp_data[:,2] - rate)<10**(-3),:]
            full_exp_data = full_exp_data[abs(full_exp_data[:,2] - rate)<10**(-3),:]
                
            # Turn strains into times
            model_times = model_data[:,6]/rate
            max_time = (strain_step+max_strain)/rate
            
            ############### plotting stress strain curves
            
            # Filter out the data so it's above 0.02 strain
            data_selected = full_exp_data[full_exp_data[:,1]>0.02]
            
            # Turn strains into times
            exp_times = data_selected[:,1]/rate
            
            # Experimental
            sns.lineplot(x=data_selected[:,1],y=data_selected[:,0]*10**(-6),ax=ax1,
                                 label = temp_name + '$^\circ$C, ' + rate_name + 's$^{-1}$ Experiment',linewidth = 2,zorder=2)
            # Add error bands
            lower_bound = (data_selected[:,0] - data_selected[:,5])*10**(-6)
            upper_bound = (data_selected[:,0] + data_selected[:,5])*10**(-6)
            ax1.fill_between(data_selected[:,1], lower_bound, upper_bound, alpha=.9, color = [230/256,230/256,230/256],zorder=1)
            
            # Model
            sns.scatterplot(x=model_data[:,6],y=model_data[:,7]*10**(-6),ax=ax1,
                                    label = temp_name + '$^\circ$C, ' + rate_name + 's$^{-1}$ Model',zorder=10)
            
            ax1.set(xlabel='$\epsilon$', ylabel='$\sigma_{Notional\;True}$ / MPa')
            ax1.set(xlim=(0, strain_step+max_strain))
            ax1.set(ylim=(0, np.around(max(full_exp_dataset[:,0]*10**(-6))+20,-1)))
            
            # Put a legend to the right side
            ax1.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.,frameon=False)
            
            ######## plotting temp time curves
            
            # Turn strains into times
            exp_times = full_exp_data[:,1]/rate
            
            # Experimental
            sns.lineplot(x=exp_times,y=full_exp_data[:,3],ax=ax2,
                                 label = temp_name + '$^\circ$C, ' + rate_name + 's$^{-1}$ Experiment',linewidth = 2,zorder=2)
            
            # Add error bands
            lower_bound = full_exp_data[:,3] - full_exp_data[:,8]
            upper_bound = full_exp_data[:,3] + full_exp_data[:,8]
            ax2.fill_between(exp_times, lower_bound, upper_bound, alpha=.9, color = [230/256,230/256,230/256],zorder=1)
             
            # Model
            sns.scatterplot(x=model_times,y=model_data[:,2],ax=ax2,
                                    label = temp_name + '$^\circ$C, ' + rate_name + 's$^{-1}$ Model',zorder=10)
            
            ax2.set(xlabel='t / s', ylabel='T (Centre) / $^\circ$C')
            ax2.set(xlim=(0, max_time))
            ax2.set(ylim=(np.around(min(full_exp_dataset[:,3])-20,-1), np.around(max(full_exp_dataset[:,3])+20,-1)))
            
            # Put a legend to the right side
            ax2.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.,frameon=False)
            
            ######### Plotting power
            # Adiabatic heating
            adiabatic_heating = np.zeros(len(model_data[:,5]))
            adiabatic_heating[0] = (model_data[0,5])/(model_times[1])
            for i in range(1,len(adiabatic_heating)):
                adiabatic_heating[i] = (model_data[i,5]-model_data[i-1,5])/model_times[1]
            
            if one_condition:
                sns.lineplot(x=model_times ,y=adiabatic_heating ,ax=ax3[sub_plot_x_axis],
                              linewidth = 2,color = 'r') 
            else:
                sns.lineplot(x=model_times ,y=adiabatic_heating ,ax=ax3[sub_plot_y_axis,sub_plot_x_axis],
                              linewidth = 2,color = 'r') 
            
            # induction Heating
            volume = pi*(sample_radius)**2*sample_length
            induction_heating = model_data[:,4]*volume
            induction_times = model_times
            induction_times[1:] = model_times[1:] - model_times[1]/2
            
            if one_condition:
                plot3 = sns.lineplot(x=induction_times,y=induction_heating ,ax=ax3[sub_plot_x_axis] ,drawstyle='steps-pre',
                             linewidth = 2,color = 'b')
                ax3[sub_plot_x_axis].set_title(temp_name + '$^\circ$C, ' + rate_name + 's$^{-1}$')
            else:
                plot3 = sns.lineplot(x=induction_times,y=induction_heating ,ax=ax3[sub_plot_y_axis,sub_plot_x_axis] ,drawstyle='steps-pre',
                             linewidth = 2,color = 'b')
                ax3[sub_plot_y_axis,sub_plot_x_axis].set_title(temp_name + '$^\circ$C, ' + rate_name + 's$^{-1}$')
            
            plot3.set(xlim=(0, max(model_times)+model_times[1]))
            plot3.set(ylim=(0,250))
            plot3.set(xlabel='Time / s', ylabel='Power / W')
            sub_plot_y_axis = sub_plot_y_axis + 1
            
        # Save figures to the figure output folder as pngs
        figure_save_location = filepath + 'plots/'
        fig1.savefig(figure_save_location+'deformation_stress_strain_'+rate_name+'s-1.png', bbox_inches='tight', format="png")
        fig2.savefig(figure_save_location+'deformation_T0_'+rate_name+'s-1.png', bbox_inches='tight', format="png")
        
        
        # Save figures as pickles so they can be quickly reloaded and edited
        pickle.dump(fig1, open(figure_save_location+'deformation_stress_strain_'+rate_name+'s-1'+'.fig.pickle', 'wb'))
        pickle.dump(fig2, open(figure_save_location+'deformation_T0_'+rate_name+'s-1'+'.fig.pickle', 'wb'))
        
    labels = ['Adiabatic Power', 'Induction Power']
    adiabatic_patch = mpatches.Patch(facecolor='r')
    induction_patch = mpatches.Patch(facecolor='b')
    fig3.legend(handles = [adiabatic_patch,induction_patch],labels=labels,loc=1,
                borderaxespad=0.05,bbox_to_anchor=(0.85, 0.85),frameon=False)
    fig3.savefig(figure_save_location+'deformation_powers.png', bbox_inches='tight', format="png")
    pickle.dump(fig3, open(figure_save_location+'deformation_powers.png'+'.fig.pickle', 'wb'))
        
    #Close all figures
    plt.close('all') 