import numpy as np

# Sellars Tegart - this can be modified
def Constitutive_law(constitutive_inputs,Temp,Rate):
    
    Q      = constitutive_inputs[0]
    A      = constitutive_inputs[1]
    n      = constitutive_inputs[2]
    R      = 8.31
    SigmaR = constitutive_inputs[3]
    SigmaP = constitutive_inputs[4]
    
    Temp = Temp + 273 # convert to Kelvin
    z = Rate*np.exp(Q/(R*Temp))
    yield_stress = 1e6*(SigmaR*np.arcsinh((z/A)**(1.0/n)) + SigmaP)
    return yield_stress