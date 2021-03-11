from abaqus import *
from abaqusConstants import *
import __main__
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
from odbAccess import *
from odbMaterial import *
from odbSection import *
from abaqusConstants import *
import shutil
import numpy as np
import datetime
from functions.constitutive_law import Constitutive_law

# This program was adapted from work by Patryk Jedrasiak, Engineering Department, University of Cambridge
# If you want to use it in your work please include a reference to the origional paper. 

# Function definition to write output 
def write_output(variable,variable_name):
    with open(filepath  + 'deformation_step/deformation_output/' + variable_name + 
              Temp_nominal + 'C_' + Strain_rate_nominal + 
              's-1_output.txt', "a") as myfile:
        myfile.write(variable)
        
#def Constitutive_law(Q,A,n,SigmaP,SigmaR,Temp,Rate):
#    R = 8.31
#    Temp = Temp + 273 # convert to Kelvin
#    z = Rate*np.exp(Q/(R*Temp))
#    yield_stress = 1e6*(SigmaR*np.arcsinh((z/A)**(1.0/n)) + SigmaP)
#    return yield_stress

def generate_platic_data(constitutive_inputs,min_T,max_T,min_rate,max_rate):
 
    # set ranges of temp and rate
    Temp = np.arange(min_T-100,max_T+100.0,5.0)
    Temp_step_no = Temp.size;
    
    # Model is meant to work between 10000 and 0.001
    log_rate = np.arange(np.log10(min_rate)-2,np.log10(max_rate)+2,0.2)
    log_rate_step_number = log_rate.size;
    
    # Initalise data table
    Material_data = np.zeros((Temp_step_no*log_rate_step_number+Temp_step_no,4))
    count = 0
    
    # estimate the static stress for each temp
    for i in range(Temp_step_no):
        # Abaqus requires a set for a rate of zero, for this set the values to 
        # be the same as whenthe rate is at some minimum in this case 10^(-5)
        # fit a linear function to two values and extrapolate from rate = 0.01
        # and 0.02 so as to have values for zero strain rate
        min_rate = 10**-5
        Material_data[count,0] = Constitutive_law(constitutive_inputs,Temp[i],min_rate) # yield stress, Pa
        Material_data[count,1] = 0  # % strain
        Material_data[count,2] = 0 # strain rate, s-1
        Material_data[count,3] = Temp[i] #% temp, K
        count = count + 1;  
        
    for j in range(log_rate_step_number):
        for i in range(Temp_step_no):
            Material_data[count,0] = Constitutive_law(constitutive_inputs,Temp[i],10**(log_rate[j])) # yield stress, Pa
            Material_data[count,1] = 0 # strain
            Material_data[count,2] = 10**(log_rate[j]) # strain rate, s-1
            Material_data[count,3] = Temp[i] # temp, K
            count = count + 1;
            
    return Material_data
        
# Program definitions
cae_filename        = 'dilatometer_model.cae'
Target_error        = 0.5 # In degrees C
sample_length       = 10*10**(-3) # in m

# If running this code from the Abaqus PDE this must be set explicitly
filepath = os.path.dirname(os.path.abspath('run_deformation.py')) + '/'
#filepath = 'C:/temp/full_pipeline/'

# Find the final heatup odb which will be used as the temperature field input in the first step
heatup_odb_location = filepath+'heat_up_step/final_heatup_odb/'

# Read in inputs from the parent code
with open (filepath+'deformation_step/deformation_input/conductance.txt', 'r') as myfile:
    data=myfile.readlines()
conductance = float(data[0])

with open (filepath+'deformation_step/deformation_input/temps_values.txt', 'r') as myfile:
    data=myfile.readlines()
Temps_nominal = [x.strip() for x in data] 
    
with open (filepath+'deformation_step/deformation_input/strains_values.txt', 'r') as myfile:
    data=myfile.readlines()
Strain_rates_nominal = [x.strip() for x in data] 
    
constitutive_inputs = []
with open (filepath+'deformation_step/deformation_input/constitutive_inputs.txt', 'r') as myfile:
    data=myfile.readlines()
data = map(lambda s: s.strip(), data)
for k in range(0,len(data)):
    constitutive_inputs.append(float(data[k]))

# Generate float versions of the condition inputs
temps_numeric = map(float, Temps_nominal)
rates_numeric = map(float, Strain_rates_nominal)

# Generate the plasticity data from the Sellars Tegart 
plasticity_values = generate_platic_data(constitutive_inputs,min(temps_numeric),
                                         max(temps_numeric),min(rates_numeric),
                                         max(rates_numeric))


for Strain_rate_nominal in Strain_rates_nominal:
    for Temp_nominal in Temps_nominal:
        
        # Remove existing diagnostic file which contains information on the output at each increment
        try:
            os.remove('Diagnostic_' + Temp_nominal + 'C_' + Strain_rate_nominal + 's-1.txt') #### Diagnostic
        except OSError:
            pass

        # Read in the power input from the output from the coarse fit
        P_guess = []
        with open (filepath + 'deformation_step/deformation_input/' + 'P_' + Temp_nominal + 'C_' + 
                   Strain_rate_nominal + 's-1.txt', 'r') as myfile:
            data=myfile.readlines()
        data = map(lambda s: s.strip(), data)
        for k in range(0,len(data)):
            P_guess.append(float(data[k]))
        
        # Take the averages from power at three points to smooth the power values 
        P_smooth = []
        P_smooth.append(0.5*P_guess[0]+0.5*P_guess[1])
        for I in range(1,len(P_guess)-1):
            P_smooth.append(0.25*P_guess[I+1]+0.5*P_guess[I]+0.25*P_guess[I-1])
        P_smooth.append(0.5*P_guess[I]+0.5*P_guess[I+1])

        # Remove old output files 
        outputs = ['P_','T0_','T4_','ALLPD_','F_','d_']
        for word in outputs:
            try:
                os.remove(filepath + 'deformation_step/deformation_output/' + word + Temp_nominal + 'C_' + Strain_rate_nominal + 's-1_output.txt')
            except OSError:
                pass

        # This reads time points at which displacments are specified, fixed displacment increment, time changes in a non-linear fashion
        time = []
        with open (filepath + 'deformation_step/deformation_input/' + 't_' + Temp_nominal + 'C_' + Strain_rate_nominal +'s-1.txt', 'r') as myfile:
            data=myfile.readlines()
        data = map(lambda s: s.strip(), data)
        for k in range(0,len(data)):
            time.append(float(data[k]))

        # Create varibale with time points and the values for powers 
        P_hist = np.zeros([2*len(time)-1,2])
        for i in range(len(time)-1):
            P_hist[2*i    ] =  (time[i],	P_smooth[i])
            P_hist[2*i + 1] =  (time[i]+(time[i+1]-time[i])/5,	P_smooth[i+1])
        P_hist[-1] =  (time[-1],	P_smooth[-1])
        
        # Create the displacment history input for Abaqus
        Disp_hist = np.array(tuple((t, -sample_length*(exp(-float(Strain_rate_nominal)*t)-1)) for t in time))
        
        with open('Diagnostic_' + Temp_nominal + 'C_' + Strain_rate_nominal + 's-1.txt', "a") as myfile: #### Diagnostic
            myfile.write('P_guess:'+"\n")
            myfile.write(str(P_guess))
            myfile.write("\n\n")    
            myfile.write('P_smooth:'+"\n")
            myfile.write(str(P_smooth))
            myfile.write("\n\n")    
            myfile.write('P_hist:' +"\n")
            myfile.write(str(P_hist))
            myfile.write("\n\n")    
            myfile.write('Disp_hist:'+"\n")
            myfile.write(str(Disp_hist))
            myfile.write("\n\n")

		# Thermocouple temperatures - arrays
        T0 = []
        T0.append(0)
        Power_history = []
        Power_history.append(0)
        
        # J is the Jth step along the displacment history 
        # For each step in the power profile 
        for J in range(1,3):#len(Disp_hist)):
            
            # Set the time increment to define the rectangular profile between two time points
            time_increment = (time[J+1]-time[J])/5
            
            # use 2J to jump between steps as P_hist includes two rows for each time step 
            # in order to define the square profile 
            SimTime = P_hist[2*J][0] - P_hist[0][0]
            
            # Set inital values for Error and Power_J, these values are rough orders of magnitude
            Error = 10.0
            Power_J = 1000.0

			# Read experimental temperature
            with open (filepath + 'deformation_step/deformation_input/Temp_' + Temp_nominal + 'C_' + Strain_rate_nominal +'s-1.txt', 'r') as myfile:
                data=myfile.readlines()
            data = map(lambda s: s.strip(), data)
            T_exp = float(data[J])
				
            with open('Diagnostic_' + Temp_nominal + 'C_' + Strain_rate_nominal + 's-1.txt', "a") as myfile: #### Diagnostic
                myfile.write('***********************************************************************\n')
                myfile.write('***********************************************************************\n')
                myfile.write('%s.\n' % (datetime.datetime.now()))
                myfile.write('Time increment: ' + str(J)+ "\n\n")
                myfile.write('Simtime: ' + str(SimTime)+ "\n")    
                myfile.write('T_exp: '+str(T_exp) +"\n\n")
				
			#Initial power scaling
            T_model = T_exp
            
            # Take the power value in the step
            P_start = P_hist[2*J][1]  
            
            # Each error run will run two jobs before taking a step in the gradient to change the power
            # P_iter_min1 is the output from the second step and P_iter_min2 is the output from the first step
            # Initially they are set to be equal to the value read in.
            P_iter_min2 = P_start
            P_iter_min1 = P_start
            
            # Power_J is the power value that will be updated during the error analysis initially set to
            # the read in value
            Power_J = P_start
            
            # Do the same with the temperature values as is done with the power. 
            T_iter_min1 = T_model
				
            # Initialise values before runinng error minimisation
            Last_iteration = 0 # This sets the breakpoint for the model
            iteration = 0 
            
            while (Error > Target_error and Last_iteration == 0): # prev target_error = 0.005
                
                iteration = iteration + 1
                
                # After running the first iteration update the power values for the 
                # gradient descent 
                P_iter_min2 = P_iter_min1 # This is assigned the power used in the step before the step that has just run
                P_iter_min1 = Power_J # This is assigned the power used in the step that has just run
                
				# For the first two iterations before gradient descent is possible assume that temp
                # is linerarly dependant on power and update it accordingly
                if iteration < 3:
                    dP = 0
                    dT = 0
                    Power_J = float(P_hist[2*J][1])*(T_exp-20.0)/(T_model-20.0)
                    
                # For later iterations use the recorded values to preform gradient descent
                else:
                    dP = P_iter_min1 - P_iter_min2 # Power_J - Power_J_Previous
                    dT = T_model - T_iter_min1
                    Power_J = P_iter_min1 + (dP-0.001)/(dT-0.001)*(T_exp - T_model)
					
                # Check that power is not dropping below zero before updating power_hist
                # as negative values are not allowed. If values are negative then set power to zero
                # and end the error minimisation. 
                if Power_J >= 0:
                    P_hist[2*J-1][1] = Power_J
                    P_hist[2*J][1] = Power_J
                else:
                    Power_J = 0.0 
                    Last_iteration = 1 
						
                    P_hist[2*J-1][1] = 0
                    P_hist[2*J][1] = 0
                    
							
                with open('Diagnostic_' + Temp_nominal + 'C_' + Strain_rate_nominal + 's-1.txt', "a") as myfile: #### Diagnostic
                    myfile.write('----------------------------------------'"\n")
                    myfile.write('P adjustment iteration: ' + str(iteration)+ "\n")
                    myfile.write('P_iter_min1: ' + str(P_iter_min1)+ "\n")
                    myfile.write('P_iter_min2: ' + str(P_iter_min2)+ "\n")
                    myfile.write('dP: ' + str(dP)+ "\n")
                    myfile.write('T_iter_min1 (T_model in eq. for Power_J): ' + str(T_model)+ "\n")
                    myfile.write('T_iter_min2 (T_iter_min1 in equiation fr Power_J): ' + str(T_iter_min1)+ "\n")
                    myfile.write('dT: ' + str(dT)+ "\n\n")
                    myfile.write('P_hist: ' + str(P_hist[2*J][1])+ "\n")
                    myfile.write('Power_J: ' + str(Power_J)+ "\n\n")
                    myfile.write('Last_iteration: ' + str(Last_iteration)+ "\n\n")

				# Open odb
                openMdb(
                    pathName=filepath+cae_filename)
                a = mdb.models['Model-1'].rootAssembly
			
    			# set thermal conductance
                mdb.models['Model-1'].interactionProperties['sample_platen_conductance'].thermalConductance.setValues(
						definition=TABULAR, clearanceDependency=ON, pressureDependency=OFF,
						temperatureDependencyC=OFF, massFlowRateDependencyC=OFF,
						dependenciesC=0, clearanceDepTable=((conductance, 0.0), (0.0, 0.001)))
			 
                mdb.models['Model-1'].interactions['air_conductance'].setValues(
						definition=EMBEDDED_COEFF, filmCoeff=0, filmCoeffAmplitude='', 
						sinkTemperature=25.0, sinkAmplitude='')  # Set filmCoeff=0 if in vacuum
			 
				# Set amplitude
                mdb.models['Model-1'].amplitudes['power'].setValues(timeSpan=STEP,
						 smooth=SOLVER_DEFAULT, data=(P_hist))
						 
				# Set amplitude
                mdb.models['Model-1'].amplitudes['displacment'].setValues(timeSpan=STEP,
						 smooth=SOLVER_DEFAULT, data=(Disp_hist))
						 
				# Set initial temperature field     
                mdb.models['Model-1'].predefinedFields['temperature_field'].setValues(
                fileName= heatup_odb_location + Temp_nominal + 'C_heatup_final.odb')
					
				# set time increments
                mdb.models['Model-1'].steps['deform'].setValues(timePeriod=SimTime, 
                    initialInc=time_increment, minInc=time_increment/1000.0, maxInc=time_increment)
                
                # Set timepoints to the Abaqus format
                time_points = np.transpose(np.atleast_2d(time))
                time_points = tuple(map(tuple, time_points))
						
                #set values for history readout
                mdb.models['Model-1'].timePoints['readout_times'].setValues(points=time_points)
                
                # Change plasticity values
                mdb.models['Model-1'].materials['material'].plastic.setValues(table=plasticity_values)
								   
				# Create job
                Job_name_up = Temp_nominal + 'C_' + "".join(Strain_rate_nominal.split(".")) + 's-1_step_' + str(J)
																								   
                mdb.Job(name=Job_name_up, model='Model-1', description='', type=ANALYSIS, 
						atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
						memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
						explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
						modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
						scratch='', multiprocessingMode=DEFAULT, numCpus=8, numDomains=8)
                Job = mdb.jobs[Job_name_up]
                Job.submit(consistencyChecking=OFF)
                Job.waitForCompletion()
					
                Job_name_up_odb = Job_name_up + '.odb'
					
                T_iter_min2 = T_iter_min1
                T_iter_min1 = T_model
			
                o1 = session.openOdb(name=Job_name_up_odb)
                session.viewports['Viewport: 1'].setValues(displayedObject=o1)
                odb = session.odbs[Job_name_up_odb]
                xy_result = session.XYDataFromHistory(name='T0', odb=odb, 
						outputVariableName='Nodal temperature: NT11 PI: SAMPLE Node 231 in NSET CENTRAL_THERMOCOUPLE', 
						)
                x1 = session.xyDataObjects['T0']
					
                xy_result = session.XYDataFromHistory(name='T4', odb=odb, 
						 outputVariableName='Nodal temperature: NT11 PI: SAMPLE Node 407 in NSET OFF_CENTRE_THERMOCOUPLE', 
						 )
                x2 = session.xyDataObjects['T4']
					
                xy_result = session.XYDataFromHistory(name='ALLPD Whole Model-1', odb=odb, 
						 outputVariableName='Plastic dissipation: ALLPD for Whole Model',)
                x3 = session.xyDataObjects['ALLPD Whole Model-1']
					
                xy_result = session.XYDataFromHistory(
					    name='F1', odb=odb, 
					    outputVariableName='CFN2: CFN2     ASSEMBLY__PICKEDSURF36/ASSEMBLY_PART-4-2_RIGIDSURFACE_ in NSET SAMPLE_TOP',)
                x4 = session.xyDataObjects['F1']
					
                xy_result = session.XYDataFromHistory(
					    name='F2', odb=odb, 
					    outputVariableName='CFN2: CFN2     ASSEMBLY__PICKEDSURF79/ASSEMBLY__PICKEDSURF78 in NSET SAMPLE_TOP',)
                x5 = session.xyDataObjects['F2']
					
                xy_result = session.XYDataFromHistory(
					    name='d', odb=odb,
					    outputVariableName='Spatial displacement: U2 PI: PART-4-2 Node 1 in NSET PLATEN_REFERENCE_POINT',)
                x6 = session.xyDataObjects['d']
			
                # Calculate error
                T_model = x1[J][1]
                Error = abs(T_exp - T_model)
					
                with open('Diagnostic_' + Temp_nominal + 'C_' + Strain_rate_nominal + 's-1.txt', "a") as myfile: #### Diagnostic
                    myfile.write('\nJ: ' + str(J) +"\n")
                    myfile.write('\nlength=' + str(len(x1)) +"\n")    
                    myfile.write('T_model: ' + str(T_model)+ "\n")
                    myfile.write('Error: ' + str(Error)+ "\n\n")
							             							      					
            T0 = str(x1[len(x1)-1][1]) + "\n"
            T4 = str(x2[len(x1)-1][1]) + "\n"
            ALLPD = str(x3[len(x1)-1][1]) + "\n"
            F = str(x4[len(x1)-1][1]+x5[len(x1)-1][1]) + "\n"
            d = str(-x6[len(x1)-1][1]) + "\n"
            Power_history = str(P_hist[2*(len(x1)-1)][1]) + "\n"
				
				# Save output to files
            write_output(T0,'_T0_')
            write_output(T4,'_T4_')
            write_output(Power_history,'_P_')
            write_output(ALLPD,'_ALLPD_')
            write_output(F,'_F_')
            write_output(d,'_d_')
        
        # Remove additional files that are not needed for steps before the final one
        filetypes = ['prt','txt','sim','inp','odb','msg','log','dat','com','sta']
        for filetype in filetypes:
            for J in range(1,len(Disp_hist)-1):
                try:
                    os.remove(filepath+Temp_nominal + 'C_' + "".join(Strain_rate_nominal.split(".")) + 's-1_step_' + str(J)+'.' + filetype)
                except OSError:
                    pass
        
        filetypes = ['prt','txt','sim','msg','log','dat','com','sta']
        try:
            os.remove(filepath+Temp_nominal + 'C_' + "".join(Strain_rate_nominal.split(".")) + 's-1_step_' + str(len(Disp_hist))+'.' + filetype)
        except OSError:
            pass
        
            
