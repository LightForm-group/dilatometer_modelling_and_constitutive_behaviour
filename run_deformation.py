from functions.generate_deformation_input import generate_deformation_input
from functions.generate_setup import generate_setup
from functions.plot_output import plot_output
from functions.extract_experimental_constitutive_data import extract_experimental_constitutive_data
import os

# This must be adjusted to the filepath that is used
# This has a CHAR lmit due to ABAQUS
filepath = 'C:/temp/full_pipeline/'

### Set the conditions and some parameters
# Conditions matrix
nominal_strain_rates  = [0.1]   # per second
nominal_temps         = [490]   # degrees C

# These are for the output of the model, refine the strain step for a higher
# resolution iutput for the model.
max_strain  = 0.65
strain_step = 0.05

# Conductance, This is a key parameter and may need adjusting to fit the 
# temperature field, this value was correct for Al6082.50
conductance = 10000.0

# Sample information - The model mesh is currently set up with these parameters
# so these cannot be changed. 
sample_length = 10*10**(-3) # m
sample_radius = 2.5*10**(-3) # m

# Modified Sellars Tegart parameters for the equation in the form
# sigma = sigmaR*(arcsinh(strain_rate*exp(Q/(R*T))/A)) + sigmaP
# To modify the constitutive law edit the constitutive_law.py file the number of 
# inputs can be varied however the equation is currenty set up to be strain 
# independant. 
Q       = 1.65e5
A       = 7.00e8
n       = 5.0
sigma_R = 20
sigma_P = 5
constitutive_inputs = [Q,A,n,sigma_R,sigma_P]

# Produce the input files with the experimental data
use_custom_inputs = 0 # Set to 1 to use custom inputs
generate_deformation_input(filepath,nominal_strain_rates,nominal_temps,
                           sample_length,sample_radius,max_strain,strain_step,
                           use_custom_inputs)

# Write the values to a text file to be excecuted when running the code in Abaqus
nominal_temps_str        = map(str, nominal_temps)
nominal_strain_rates_str = map(str, nominal_strain_rates)
generate_setup(constitutive_inputs,nominal_temps_str,
               nominal_strain_rates_str,conductance)

# Run the deformation model 
os.system('call abaqus cae nogui=deformation_step.py')
    
# Plot the output
# This will generate plots from the experiment and the output of the model to compare to of:
# The central thermocouple temperature vs time
# The secondary thermocouple temperature vs time
# The stress-strain curve
plot_output(filepath,nominal_temps,nominal_strain_rates,strain_step,
            max_strain,sample_length,sample_radius)

# Extract Constitutive data
# It is assumed that for the experimental data the effects of assumptions about 
# homogenous conditions in the sample, friction and other assumptions made 
# during the calculation of the stress are an addition to the true behaviour.
# i.e. Measured flow stress = True flow stress + other effects
#
# By finding how the measured flow stress in the modeldiffers from the true for 
# the Sellars-Tegart input in the previour steps the magnitude of the other effects can 
# be extracted at each condition in (strain,rate and temp). This can then be 
# subtracted from the experimentally measured flow stress to find the true 
# experimental constitutive data. As this is done in strain increments the 
# outputs will be retutrned at the output strains of the model. This data is then 
# fitted to a statistical fit with the form:
# log10(stress) = c0 + c1*T + c2*log10(rate) + c3*T*log10(rate) + c4*T^2 + c5*(log10(rate))^2
# This is then used to return the constitutive data. 
# This will then be written to a text file in plots comparisons between this equation
# and the points used to fit the equation are also plotted.
extract_experimental_constitutive_data(filepath,nominal_temps,nominal_strain_rates,constitutive_inputs)

