# dilatometer_modelling_and_constitutive_behaviour

This program contains a method of testing various constitutive models and extracting the constitutive behaviour of dilatometer sample correcting for inhomogeneities (i.e. sample barrelling and friction). 

## Intallation
**IMPORTANT**: Due to the 80 character limit in abaqus this must be executed from temp directory. 
**Requiments**: 'ABAQUS', 'numpy', 'seaborn', 'pickle', 'matplotlib', and 'math'  
**Using your data**: To use your own data you must place the outputted .ACS files from the dilatometer into the filestructure shown below. further changes you may need to make are outlined in the running the model section. 

## Testing
The full model with a high resolution in the steps can take some time to run, on a normal laptop each condition takes approximatly 30 minutes. To test the deformation model run 'run_deformaion' with the provided data and settings. 

## Running

### Changes to the code
* Change the filepath in the 'run_heatup' and 'run_deformation' to the current path with the folder name

### Changes to the CAE file
For a material that is not 6082.50 Aluminum editing will be required to the 'dilatometer_model.cae' file. For a new material the following changes will have to be made:
* Density
* Elastic modulus, Possions ratio
* Specific heat
* Thermal conductivity

## Ouputs

### Experimental ouput: 
The code will combine repeated experiments to find an
average behaviour. This is done via a binning method in strain  which combines all values within a 0.01 strain increment. The errors are the errors that occour due to the averaging during the binning and averaging of the data at each condition. The three outputs that are generated from the experimental data are:

* experimental_output_all_data.txt - This uses the bining method then stacks all the conditions. It has the following format:
  * stress, strain, strain rate, real temp, nom temp, err(stress), err(stress), err(strain), err(strain rate), err(real temp), err(nom temp)    
* experimental_output_interp_stack_temp.txt - This performes interpolation onthe experimental_output_all_data dataset at each condition to return outputsat the specified strains for temps. It has the following format:
  * Real Temp, Strains, strain rate, nominal temp, err(Real Temp), err(Strains), err(strain rate), err(nominal temp)
* experimental_output_interp_stack_stress.txt - This performes interpolation onthe experimental_output_all_data dataset at each condition to return outputsat the specified strains for stresses. It has the following format:
  * Stress, Strains, strain rate, nominal temp, err(Stress), err(Strains), err(strain rate), err(nominal temp)

### Model ouputs:
* Plots: Plots will be created in the plots folder. There are two versions. one is in the .png format and can't be edited and one is in the pickle format. the pickle format can be loaded back into anoher script as a fig which can then beedited with further python scripting.
* Data: These are placed in the deformation_step/deformation_output folder. The values have the following meaning:
  * ALLPD - The power per unit volume for the plastic disipation 
  * d     - The displacment of the platens / (m)
  * F     - The force required to deform the material / (N)
  * P     - The power needed from the induction heating 
  * T0    - The temperature at the middle thermocouple / Degrees C
  * T4    - The temperature at the off centre thermocouple at 4 mm from the centre / degrees C

## Filestructure
├── deformation_step<br/>
│   ├── deformation_input #(input .txt files to transfer data to the ABAQUS deformation model)<br/>
│   └── deformation_output #(outputted .txt files from the ABAQUS deformation model)<br/>
│ <br/>
├── heatup_step
│   ├── heatup_input #(input .txt files to transfer data to the ABAQUS heatup model)<br/>
│   ├── heatup_output #(outputted .txt files from the ABAQUS heatup model)<br/>
│   └── final_heatup_odb #(Location of the final temperature distribution in the ABAQUS heatup model)<br/>
│ <br/>
├── experimental_data<br/>
│   ├── deformation #(Folder containing the .ACS files from the dilatometer for the deformation region, the naming convention of the .ACS files is not relevant here)<br/>
│   │   ├── Nominal strain rate 1<br/>
│   │   │   ├── Nominal temperature 1<br/>
│   │   │   ├── Nominal temperature 2<br/>
│   │   │   ├── ...<br/>
│   │   ├── Nominal strain rate 2<br/>
│   │   │   ├── Nominal temperature 1<br/>
│   │   │   ├── Nominal temperature 2<br/>
│   │   │   ├── ...<br/>
│   │   │   <br/>
│   │   ├── ... <br/>
│   │ <br/>
│   └── full #(Folder containing the .ACS files from the dilatometer for the full region, the naming convention of the .ACS files is not relevant here)<br/>
│   │   ├── Nominal strain rate 1<br/>
│   │   │   ├── Nominal temperature 1<br/>
│   │   │   ├── Nominal temperature 2<br/>
│   │   │   ├── ...<br/>
│   │   │   <br/>
│   │   ├── Nominal strain rate 2<br/>
│   │   │   ├── Nominal temperature 1<br/>
│   │   │   ├── Nominal temperature 2<br/>
│   │   │   ├── ...<br/>
│   │   │   <br/>
│   │   ├── ... <br/>
│   │ <br/>
│   ├── experimental_output #(.txt files conataining the processed data from the deformation step)<br/>
│ <br/>
├── functions #(Various .py functions used in the program)<br/>
│ <br/>
└── plots #(Outputted plots in both .png and pickle format)<br/>
