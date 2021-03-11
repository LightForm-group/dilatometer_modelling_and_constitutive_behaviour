def generate_setup(constitutive_inputs,nominal_temps,nominal_strain_rates,conductance):
    
    with open('deformation_step/deformation_input/conductance.txt', 'w') as f:
        f.write("%f" % conductance)
    
    with open('deformation_step/deformation_input/constitutive_inputs.txt', 'w') as f:
        for value in constitutive_inputs:
            f.write("%f\n" % value)
            
    with open('deformation_step/deformation_input/temps_values.txt', 'w') as f:
        for temp in nominal_temps:
            f.write("%s\n" % temp)
    
    with open('deformation_step/deformation_input/strains_values.txt', 'w') as f:
        for rate in nominal_strain_rates:
            f.write("%s\n" % rate)
    return