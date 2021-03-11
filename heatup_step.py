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
        
# To run this file in the command line use
# call abaqus cae nogui=heatup_step.py

# Function definition to write output 
def write_output(variable,variable_name):
    with open(filepath  + 'heat_up_step/heatup_output/' + variable_name + 
              Temp + 'C_' +'output.txt', "a") as myfile:
        myfile.write(variable)

filepath = os.path.dirname(os.path.abspath('heatup_step.py')) + '/'
cae_filename = 'dilatometer_model.cae'

# Minmimum allowable difference in temperature in degrees
target_error = 0.5

with open (filepath+'heat_up_step/heatup_input/conductance.txt', 'r') as myfile:
    data=myfile.readlines()
conductance = float(data[0])


with open (filepath+'heat_up_step/heatup_input/temps_values.txt', 'r') as myfile:
    data=myfile.readlines()
Temps_nominal = [x.strip() for x in data] 

for Temp in Temps_nominal:
    
    # Remove existing diagnostic file which contains information on the output at each increment
    try:
        os.remove('Diagnostic_' + Temp + 'C.txt') #### Diagnostic
    except OSError:
        pass
    
    # Remove old output files 
    outputs = ['P_','T0_','T4_']
    for word in outputs:
        try:
            os.remove(filepath + 'heat_up_step/heatup_output/' + word + 
              Temp + 'C_' +'output.txt')
        except OSError:
            pass
    
    
    # This reads in power values
    Power = []
    with open (filepath+'heat_up_step/heatup_input/P_heatup_' + Temp + 'C.txt', 'r') as myfile:
        data=myfile.readlines()
    data = map(lambda s: s.strip(), data)
    for k in range(0,len(data)):
        Power.append(float(data[k]))
        
    # This reads in time values
    time = []
    with open (filepath+'heat_up_step/heatup_input/time_heatup_' + Temp + 'C.txt', 'r') as myfile:
        data=myfile.readlines()
    data = map(lambda s: s.strip(), data)
    for k in range(0,len(data)):
        time.append(float(data[k]))
        
    P_hist = np.array(tuple((time[i], Power[i]) for i in range(len(time))))
    
    # Thermocouple temperatures - arrays
    T0 = []
    T0.append(0) # might be 20 - check this. Look in the cae file and look at how the inital distribution is defined
    Power_history = []
    Power_history.append(0)
        
    for J in range(1,len(P_hist)): 
        
        with open(filepath+'Diagnostic_' + Temp + 'C.txt', "a") as myfile: #### Diagnostic
            myfile.write('\nJ: ' + str(J) +"\n") 
        
        # 
        SimTime = P_hist[J][0] - P_hist[J-1][0]
        Error = 10
        Power_J = 1000
        
        #Read experimental temperature
        with open (filepath+'heat_up_step/heatup_input/Temp_heatup_' + Temp + 'C.txt', 'r') as myfile:
            data=myfile.readlines()
        data = map(lambda s: s.strip(), data)
        T_exp = float(data[J])
        
        #Initial power scaling
        T_model = T_exp
        
        # Take the power value in the step
        P_start = P_hist[J][1]  
        
        # Each error run will run two jobs before taking a step in the gradient to change the power
        # P_iter_min1 is the output from the second step and P_iter_min2 is the output from the first step
        # Initially they are set to be equal to the value read in.
        P_iter_min2 = P_start
        P_iter_min1 = P_start
        
        # Power_J is the power value that will be updated during the error analysis initially set to
        # the read in value
        Power_J = P_start
        
        # Do the same with the temperature values as is done with the power. 
        T_start = T_model  
        T_iter_min2 = T_start
        T_iter_min1 = T_start
        
        # Initialise values before runinng error minimisation
        Last_iteration = 0 
        iteration = 0
        
        while (Error > target_error and Last_iteration == 0):
            
            # Calculate new power -  in this case each step in the power profile is modelled seperatly, 
            # this is unlike the deformation model in which the model is run up to each step being changed. 
            #Power_J = float(P_hist[J][1])*(T_exp-20)/(T_model-20)
            #P_hist[J][1] = Power_J
            
            iteration = iteration + 1
                        
            # After running the first iteration update the power values for the 
            # gradient descent 
            P_iter_min2 = P_iter_min1
            P_iter_min1 = Power_J
    					
    		# For the first three iterations before gradient descent is possible assume that temp
            # is linerarly dependant on power and update it accordingly
            if iteration < 3:
                dP = 0
                dT = 0
                Power_J = float(P_hist[J][1])*(T_exp-20.0)/(T_model-20.0)
                
            # For later iterations use the recorded values to preform gradient descent
            else:
                dP = P_iter_min1 - P_iter_min2
                dT = T_model - T_iter_min1
                Power_J = P_iter_min1 + (dP-0.001)/(dT-0.001)*(T_exp - T_model)
    					
            # Check that power is not dropping below zero before updating power_hist
            # as negative values are not allowed. If values are negative then set power to zero
            # and end the error minimisation. 
            if Power_J >= 0:
                P_hist[J][1] = Power_J
            else:
                Power_J = 0.0 
                Last_iteration = 1 
                P_hist[J][1] = 0
    		
            # Open odb
            openMdb(
                 pathName=filepath+cae_filename)
            a = mdb.models['Model-1'].rootAssembly
            
            # Set conductance
            mdb.models['Model-1'].interactionProperties['sample_platen_conductance'].thermalConductance.setValues(
    	    definition=TABULAR, clearanceDependency=ON, pressureDependency=OFF,
    	    temperatureDependencyC=OFF, massFlowRateDependencyC=OFF,
    	    dependenciesC=0, clearanceDepTable=((conductance, 0.0), (0.0, 0.000000001))) # conductance to the platens - this is just an order orf magnitude
            
            # Set air cooling cooling - currently off
            mdb.models['Model-1'].interactions['air_conductance'].setValues(
                definition=EMBEDDED_COEFF, filmCoeff=0, filmCoeffAmplitude='',
                sinkTemperature=25.0, sinkAmplitude='')  
        
            # Set amplitude
            mdb.models['Model-1'].amplitudes['power'].setValues(timeSpan=STEP,
                 smooth=SOLVER_DEFAULT, data=((0.0, P_hist[J][1] ), (SimTime, P_hist[J][1] )))
            
            # Update thermal field
            Directory = filepath + Temp+'C_heatup' + str(J-1) + '.odb'
            if J > 1:
                del mdb.models['Model-1'].predefinedFields['temperature_field']
                mdb.models['Model-1'].Temperature(name='temperature_field',
                    createStepName='Initial', distributionType=FROM_FILE,
                    fileName=Directory, beginStep=1, beginIncrement=1,
                    endStep=None, endIncrement=None, interpolate=OFF, 
                    absoluteExteriorTolerance=0.0, exteriorTolerance=0.05)                     
            else:
                pass
            
            
            # Update step time
            mdb.models['Model-1'].steps['deform'].setValues(timePeriod=SimTime, 
                initialInc=SimTime, minInc=SimTime/1000, maxInc=SimTime)
            
            # Create job
            if J == len(P_hist):
                Job_name_up = Temp+'C_heatup_final'
            else:
                Job_name_up = Temp+'C_heatup' + str(J)
                
            Job_name_up_odb = Job_name_up + '.odb'
                                                                                           
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
            
            odb = session.openOdb(name=Job_name_up_odb)
             
            xy_result = session.XYDataFromHistory(name='T0', odb=odb, 
						outputVariableName='Nodal temperature: NT11 PI: SAMPLE Node 231 in NSET CENTRAL_THERMOCOUPLE', 
						)
            x1 = session.xyDataObjects['T0']
					
            xy_result = session.XYDataFromHistory(name='T4', odb=odb, 
						 outputVariableName='Nodal temperature: NT11 PI: SAMPLE Node 407 in NSET OFF_CENTRE_THERMOCOUPLE', 
						 )
            x2 = session.xyDataObjects['T4']
    
            # Calculate error
            T_iter_min2 = T_iter_min1
            T_iter_min1 = T_model
            T_model = x1[1][1]
            Error = abs(T_exp - T_model)
            
            with open(filepath+'Diagnostic_' + Temp + 'C.txt', "a") as myfile: #### Diagnostic
                myfile.write('\nIter no: ' + str(iteration) +"\n") 
                myfile.write('Power_J: ' + str(Power_J)+ "\n")
                myfile.write('P_iter_min1: ' + str(P_iter_min1)+ "\n")
                myfile.write('P_iter_min2: ' + str(P_iter_min2)+ "\n")
                myfile.write('T_exp: ' + str(T_exp)+ "\n")
                myfile.write('T_model: ' + str(T_model)+ "\n")
                myfile.write('T_iter_min1: ' + str(T_iter_min1)+ "\n")
                myfile.write('Error: ' + str(Error)+ "\n")
            
            # Only allow 20 itterations, this tops the code getting stuck in cycles
            if iteration > 20:
                break
             
        # Append temperatures
        T0 = str(x1[1][1]) + "\n"
        T4 = str(x2[1][1]) + "\n"
        Power_history = str(P_hist[J][1]) + "\n"
        
        # Save outputs to files
        write_output(T0,'T0_')
        write_output(T4,'T4_')
        write_output(Power_history,'P_')
        
    # Remove additional files that are not needed for steps before the final one
    filetypes = ['prt','txt','sim','inp','odb','msg','log','dat','com','sta']
    for filetype in filetypes:
        for J in range(1,len(P_hist)-1): 
            try:
                os.remove(filepath+Temp+'C_heatup' + str(J) + '.' + filetype)
            except OSError:
                pass
        
    filetypes = ['prt','txt','sim','msg','log','dat','com','sta','inp']
    try:
        os.remove(filepath+Temp+'C_heatup_final' + '.' + filetype)
    except OSError:
        pass