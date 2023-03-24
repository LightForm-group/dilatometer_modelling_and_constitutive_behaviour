def generate_setup(nominal_temps,nominal_strain_rates,conductance):
    
    # Convert the files to strings
    nominal_temps        = map(str, nominal_temps)
    nominal_strain_rates = map(str, nominal_strain_rates)
    
    with open('deformation_step/deformation_input/conductance.txt', 'w') as f:
        f.write("%f" % conductance)
            
    with open('deformation_step/deformation_input/temps_values.txt', 'w') as f:
        for temp in nominal_temps:
            f.write("%s\n" % temp)
    
    with open('deformation_step/deformation_input/strains_values.txt', 'w') as f:
        for rate in nominal_strain_rates:
            f.write("%s\n" % rate)
    return