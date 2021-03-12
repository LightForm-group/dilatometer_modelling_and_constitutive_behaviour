# dilatometer_modelling_and_constitutive_behaviour

This program contains a method of testing various constitutive models and extracting the constitutive behaviour of dilatometer sample correcting for inhomogeneities (i.e. sample barrelling and friction). The model is currently configured to a dilatometer run under vacuum with no active cooling during the deformation. For both heatup and deformation the temperature is fitted to the recorded central themocoupole temperature for any general temperature profile. The output then allows the dilatometer behaviour to be corrected to compensate for the inhomogeneities via the method set out in the following paper that can be found [here](https://www.sciencedirect.com/science/article/pii/S1005030220309257). If you have any issues or questions please feel free to contact me via email at [ih345@cam.ac.uk](ih345@cam.ac.uk).

## Intallation
**IMPORTANT**: Due to the 80 character limit in abaqus this must be executed from temp directory.<br/>
**Requiments**: `ABAQUS`, `numpy`, `seaborn`, `pickle`, `matplotlib`, and `math`.<br/>

## Testing
The full model with a high true strain step resolution can take some time to run, on a normal laptop each condition takes approximatly 30 minutes. To test the deformation model run `run_deformaion` with the provided data and settings.

## Running

To model a dilatometer run with a different material There are a number of steps to go through. Some of these steps can be skipped depending on the material used and the set up of the dilatometer. 

1. **Organising dilatometer data**:
    1. The .ASC dilatometer data files need to be in the following format with 3 header lines:  No., Time, Tem.1, DL, Force, Strain, kf (Def.), Phi  (D), Phi* (D), Tem.2, Tem.3, Poti, HF. 
    2. Organise the data by nominal deformation strain rate and temperature seperating the .ASC deformation files from the files with the full profile. Put the files into the sturture shown in the filestructure section below. The naming convention of the .ACS files is not relevant here and does not need to be consistent. The code will average the behaviour of repeats which may produce some unrepresentitive behaviour so check which files you include. 

2. **Adding material behaviour to the CAE ABAQUS model:**
    1. For a material that is not 6082.50 Aluminum editing will be required to the `dilatometer_model.cae` file. For a new material the material `material` must be edited to have the correct properties, these should be temperature dependent:
        1. Density
        2. Elastic modulus, Possions ratio
        3. Specific heat
        4. Thermal conductivity

3. **Changing dilatometer parameters in the model:**
    1. This will be required if any of the conditions used differ from the following: Al2O3 platens, He cooling turned off during deformation, test conducted in a vacuum, non-standard size sample.
        1.  Non-Al2O3 platens: Navigate to the materials in the `dilatometer_model.cae` file and edit the material `Al2O3` to have the properties that match the platens used.
        2.  He cooling used during deformation: This section has not been added to the code yet but is present in the ABAQUS model. You can add He cooling by editing the cool amplitude. A future version will include an option to have this fitted similar to the induction power. 
        3.  Test not conducted in a vacuum: This will require going to the `heatup_step.py` and `deformation_step.py` files and editing the film_coeff parameter in the program definitions, this may require optimisation. 
        4.  Non-standard size sample: The model is not currently set up to have non standard (10mmx5mm) samples. A future version may include this.

4. **Seting up the program inputs:**
    1. Naviagte to the `run_heatup.py` and `run_deformation.py` files and edit the nominal conditions matrix and change the filepath to the filepath you are using, change the max strain to the max true strain during deformation, choose a strain step at which values will be fitted and read out (a small value will really slow down your code). 
    2. If during deformation you do not wish to use the automatically generated input files from the dilatometer data set `use_custom_inputs` in `run_deformation.py` to 1. This will require you to generate the input txt files for deformation yourself. 
    3. For the heatup step the input files must be manually created. The following files must be created and placed in the `heatup_step/heatup_input` folder:
        1. Power - This is a list of numbers that will be adjusted by the model and can be any non zero value (commonly arounf 1e8) in the format P_heatup_(nominal_temp)C.txt
        2. Temp  - A list of the target temperatures for each time in degrees C in the format Temp_heatup_(nominal_temp)C.txt
        3. times - A list of the times at which the power will be fitted to match the desired temperatures in the format t_heatup_(nominal_temp)C.txt

5. **Changing the consitiutive law**:
    1. The constitutive law can be changed to take in any number of inputs, the form of the law can be changed by navigating to `functions/constitutive_law.py`. The law is currently set up such that it cannot be strain dependent. 

6. **Sensitivity studies and parameter optimisation:**
    1. There are a number of parameters in the model that may require optimisation, one **important** factor is the conductance which dictates the conductance between the sample and the platens. Literature values of this parameter are scarce so this may require some testing and optimising. The value may also vary between heatup and deformation. It's magnitude will dictate the temperature gradient across the sample. If the model is not capturing the temperature field or is unable to cool fast enough the conductance value can be edited in the `run_heatup.py` and `run_deformation.py` files. It is best to run this optimisation on just a few conditions in order to save time. 
    2. Other parameters that may require optimisation include the `film_coeff` parameter founf in the run files and the friction coefficent between the sample and platens found in the CAE file. 

7. **Executing the model:**
    1. Once the previous steps have been completed the model should be ready to run. The program has the following steps:
        1. Initially the starting temperature field for the deformation is generated via running the `run_heatup.py` file. This has no post-processing.
        2. Running the deformation model for a matrix of conditions with `run_deformation.py`. This has three steps:
            1. Setting up and running the ABAQUS deformation model to generate ouputs.
            2. Generating plots.
            3. Generating the corrected consitiutive data.

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
* Plots: Plots will be created in the `plots` folder. There are two versions. one is in the .png format and can't be edited and one is in the pickle format. the pickle format can be loaded back into anoher script as a fig which can then beedited with further python scripting.
* Data: These are placed in the `deformation_step/deformation_output` folder. The values have the following meaning:
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
├── heatup_step<br/>
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
