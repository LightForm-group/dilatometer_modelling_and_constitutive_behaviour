# dilatometer_modelling_and_constitutive_behaviour

This program contains a method of testing various constitutive models and extracting the constitutive behaviour of dilatometer sample correcting for inhomogeneities (i.e. sample barrelling and friction). 

## Intallation
**IMPORTANT**: Due to the 80 character limit in abaqus this must be executed from temp directory. 
**Requiments**: 'ABAQUS', 'numpy', 'seaborn', 'pickle', 'matplotlib', and 'math'  
**Using your data**: To use your own data you must place the outputted .ACS files from the dilatometer into the filestructure shown below. further changes you may need to make are outlined in the running the model section. 

## Testing
The full model with a high resolution in the steps can take some time to run, on a normal laptop each condition takes approximatly 30 minutes. To test the deformation model run 'run_deformaion' with the provided data and settings. 

## Filestructure
├── deformation_step
│   ├── deformation_input # input .txt files to transfer data to the ABAQUS deformation model
│   └── deformation_output # outputted .txt files from the ABAQUS deformation model
│ 
├── heatup_step
│   ├── heatup_input # input .txt files to transfer data to the ABAQUS heatup model
│   ├── heatup_output # outputted .txt files from the ABAQUS heatup model
│   └── final_heatup_odb # Location of the final temperature distribution in the ABAQUS heatup model
│ 
├── experimental_data
│   ├── deformation # Folder containing the .ACS files from the dilatometer for the deformation region, the naming convention of the .ACS files is not relevant here
│   │   ├── Nominal strain rate 1
│   │   │   ├── Nominal temperature 1
│   │   │   ├── Nominal temperature 2
│   │   │   ├── ...
│   │   ├── Nominal strain rate 2
│   │   │   ├── Nominal temperature 1
│   │   │   ├── Nominal temperature 2
│   │   │   ├── ...
│   │   ├── ... 
│   │ 
│   └── full # Folder containing the .ACS files from the dilatometer for the full region, the naming convention of the .ACS files is not relevant here
│   │   ├── Nominal strain rate 1
│   │   │   ├── Nominal temperature 1
│   │   │   ├── Nominal temperature 2
│   │   │   ├── ...
│   │   ├── Nominal strain rate 2
│   │   │   ├── Nominal temperature 1
│   │   │   ├── Nominal temperature 2
│   │   │   ├── ...
│   │   ├── ... 
│   │ 
│   ├── experimental_output # .txt files conataining the processed data from the deformation step
│ 
├── functions # Various .py functions used in the program
│ 
├── plots # Outputted plots in both .png and pickle format 
