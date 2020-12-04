
#### Coil Specifications ####

coil_length = 0.08  # 8 cm half-length
coil_radius = 0.023  # 2.3 cm outer turn radius
wire_radius = 0.000125  # 32 AWG radius, can be changed to accomodate a different wire radius
windings = 50  # total number of windings along coil axis (half on either side)
turns = 2  # total number of turns on each winding, additional turns (> 1) are wound BENEATH the outermost turn with radius 'coil_radius'
groove_width = 0.001  # minimum seperation between wires, set to 1mm but can be changed to accomodate different 3d printers
d_min = 2*wire_radius + groove_width  # minimum separation distance relative to centers of two adjacent wires


#### Algorithm Constants ####

optimization_length = 0.075  # optimize the magnetic field homogeneity over this length
calculation_number = 200  # number of magnetic field calculation points
maximum_iterations = 10000  # maximum number of iterations
optimization_threshold = 0.000000001 # minimum allowed value of dl in algorithm
