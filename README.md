# dilatometer_modelling_and_constitutive_behaviour

This program contains a method of testing various constitutive models and extracting the constitutive behaviour of dilatometer sample correcting for inhomogeneities (i.e. sample barrelling and friction). The model is currently configured to a dilatometer run under vacuum with no active cooling during the deformation. For both heatup and deformation the temperature is fitted to the recorded central themocoupole temperature for any general temperature profile. The output then allows the dilatometer behaviour to be corrected to compensate for the inhomogeneities via the method set out in the following paper that can be found [here](https://www.sciencedirect.com/science/article/pii/S1005030220309257). If you have any issues or questions please feel free to contact me via email at [ih345@cam.ac.uk](ih345@cam.ac.uk).

## Intallation
**IMPORTANT**: Due to the 80 character limit in abaqus this must be executed from temp directory.<br/>
**Requiments**: `ABAQUS`, `numpy`, `seaborn`, `pickle`, `matplotlib`, and `math`.<br/>
**Using your data**: To use your own data you must place the outputted .ACS files from the dilatometer into the filestructure shown below. further changes you may need to make are outlined in the running the model section. 

## Testing
The full model with a high resolution in the steps can take some time to run, on a normal laptop each condition takes approximatly 30 minutes. To test the deformation model run 'run_deformaion' with the provided data and settings. 

## Running

### Adding experimental data
* Add the dilatometer .ACS files to the folder with the structure shown in the filestructure section. The naming convention of the .ACS files is not relevant here and does not need to be consistent. 

### Changes to the code
* Change the filepath in the `run_heatup` and `run_deformation` to the current path.
* All variables can currently be changed except the sample dimensions in the `run_deformation` and `run_heatup` functions. One **important** factor is the conductance which dictates the conductance between the sample and the platens. Literature values of this parameter are scarce so this may require some testing and optimising. 
* The consitiutive law is currently set up to be the Sellars-Tegart law, this can be changed by editing the 'constitutive_law.py' file in the functions folder. The model is currently set up such that the consitiutive law is strain independent. 

### Changes to the CAE file
For a material that is not 6082.50 Aluminum editing will be required to the `dilatometer_model.cae` file. For a new material the following changes will have to be made:
* Density
* Elastic modulus, Possions ratio
* Specific heat
* Thermal conductivity

### Executing the model
The model is run in two steps. 
1. Initially the starting temperature field for the deformation is generated via running the `run_heatup.py` file. This has no post-processing.
1. Running the deformation model for a matrix of conditions with `run_deformation.py`. This has three steps:
 1. Set up and run the ABAQUS deformation model to get ouputs.
 1. Generating plots.
 1. Generating the corrected consitiutive data.

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

## Functions and definitions
### Main functions
* `run_deformation.py`
* `run_heatup.py`
* `deformation_step.py`
* `heatup_step.py`
### Subfunctions
* `constitutive_law.py`
* `extract_experimental_constitutive_data.py`
* `extract_model_output.py`
* `generate_deformation_input.py`
* `generate_heatup_input.py`
* `generate_setup.py`
* `plot_output.py`

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
│   ├── deformation #(Folder containing the .ACS files from the dilatometer for the deformation region)<br/>
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
│   └── full #(Folder containing the .ACS files from the dilatometer for the full region)<br/>
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
