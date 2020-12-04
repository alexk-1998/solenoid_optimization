import numpy as np
import pandas as pd
from datetime import datetime
from time import time
from pathlib import Path
from my_constants import *


def homogeneity(z_pts: np.ndarray, wire_locs: np.ndarray, p: np.ndarray) -> float:

    """
    z_pts: an array consisting of points along the z-axis (0, 0, z) for magnetic field calculations
    wire_locs: an array consisting of the z-position of individual coil windings
    p: an array consisting of the radius of wire turns within a single groove
    Return the result of calculating Eq. B2 in the literature
    """

    B_c = np.sum(1/(p**2 + wire_locs**2)**1.5, axis=(1, 2))
    B_z = np.sum(1/(p**2 + (z_pts - wire_locs)**2)**1.5, axis=(1, 2))
    area = np.trapz(np.absolute((B_z - B_c)/B_c))
    return area


def check_locs(wire_locs: np.ndarray, wire_radius: float, d_min: float, windings: int) -> bool:

    """
    wire_locs: an array consisting of the z-position of individual coil windings
    wire_radius: radius of a single wire, 32 AWG, etc...
    d_min: minimum seperation distance between non-'bundled' wires. allows sufficient space for 3d printed plastic between grooves
    windings: number of total windings along coil z-axis
    Return a boolean indicating whether the coil design is valid according to specifications
    """
    
    upper_lim = 1.001*2*wire_radius  # upper limit on bundle seperation
    lower_lim = 0.999*2*wire_radius  # lower limit on bundle seperation, prevents overlapping wires in bundle
    space_lim = 0.999*d_min  # lower limit on non-bundled seperation, allows sufficient space for 3d printed plastic between grooves
    sep = np.diff(wire_locs[0, :, 0])  # array of seperation distances between all adjacent wires
    
    # checks if a wire originally on the +z side of the coil has been pushed to the -z side
    if wire_locs[0, int(windings/2 - 1), 0] > 0:
        return False
        
    # checks if a wire originally on the -z side of the coil has been pushed to the +z side
    if wire_locs[0, int(windings/2), 0] < 0:
        return False
        
    # checks if any seperations are below the minimum threshold (equivalent to overlapping wires)
    if np.amin(sep) < lower_lim:
        return False
        
    # checks if any non-bundled wires are within the minimum seperation distance
    if np.any((sep < space_lim) & (sep > upper_lim)):
        return False
        
    return True


def main():

    inner_wire = coil_radius - 2*(turns - 1)*wire_radius  # turn radius of innermost wire
    radius = np.linspace(coil_radius, inner_wire, turns)  # radius of all turns
    radius = radius.reshape((1, 1, turns))

    z_calc = np.linspace(0, optimization_length, calculation_number).reshape((calculation_number, 1, 1))  # magnetic field calculation points ranging from z=[0, optimization_length]
    locs = np.linspace(-coil_length, coil_length, windings).reshape((1, windings, 1))  # wire locs, initial coil is an equal-spaced turn solenoid

    input('\nPress <ENTER> to begin optimization...')
    start_time = time()

    print('\n Iteration | FD Area')
    print('-'*21)

    area = homogeneity(z_calc, locs, radius)  # initial field homogeneity of solenoid

    a = np.arange(1, int(windings/2))  # numbers windings for shuffling and random selection
    iteration = 0
    wire_displacement = 0.25*coil_length/windings  # initial test displacement distance, should have first factor < 0.5 to prevent wire overlap
    locs1 = np.copy(locs)
    locs2 = np.copy(locs)
    

    while (wire_displacement > optimization_threshold) & (iteration <= maximum_iterations):
        np.random.shuffle(a)
        for i in a:
            print(' {:>9d} | {:>7.4f}'.format(iteration, area))  # comment out for some increase to algorithm speed

            iteration += 1
            if iteration > maximum_iterations:
                break

            # shifts selected wires -wire_displacement relative to z=0
            locs1[0, i, 0] -= wire_displacement
            locs1[0, -1-i, 0] = -locs1[0, i, 0]
            
            # creates a bundle if displacement moved wire within tolerance relative to adjacent wire
            if not check_locs(locs1, wire_radius, d_min, windings):
                locs1[0, i, 0] = locs1[0, i-1, 0] + 2*wire_radius
                locs1[0, -1-i, 0] = -locs1[0, i, 0]

            # checks for coil validity and if true calculates the field homogeneity
            if check_locs(locs1, wire_radius, d_min, windings):
                area1 = homogeneity(z_calc, locs1, radius)
                
                # saves result if improvement to homogeneity is found
                if area1 < area:
                    locs = np.copy(locs1)
                    area = area1
                    break

            # seperates adjacent wires exactly by minimum seperation distance
            locs1[0, i, 0] += locs1[0, i-1, 0] + d_min
            locs1[0, -1-i, 0] = -locs1[0, i, 0]
            
            # checks for coil validity and if true calculates the field homogeneity
            if check_locs(locs1, wire_radius, d_min, windings):
                area1 = homogeneity(z_calc, locs1, radius)
                
                # saves result if improvement to homogeneity is found
                if area1 < area:
                    locs = np.copy(locs1)
                    area = area1
                    break

            # shifts selected wires +wire_displacement relative to z=0
            locs2[0, i, 0] += wire_displacement
            locs2[0, -1-i, 0] = -locs2[0, i, 0]
            
            # creates a bundle if displacement moved wire within tolerance relative to adjacent wire
            if not check_locs(locs2, wire_radius, d_min, windings):
                if i != np.amax(a):
                    locs2[0, i, 0] = locs2[0, i+1, 0] - 2*wire_radius
                    locs2[0, -1-i, 0] = -locs2[0, i, 0]

            # checks for coil validity and if true calculates the field homogeneity
            if check_locs(locs2, wire_radius, d_min, windings):
                area2 = homogeneity(z_calc, locs2, radius)
                
                # saves result if improvement to homogeneity is found
                if area2 < area:
                    locs = np.copy(locs2)
                    area = area2
                    break

            # seperates adjacent wires exactly by minimum seperation distance
            locs2[0, i, 0] = locs2[0, i+1, 0] - d_min
            locs2[0, -1-i, 0] = -locs2[0, i, 0]
            
            # checks for coil validity and if true calculates the field homogeneity
            if check_locs(locs2, wire_radius, d_min, windings):
                area2 = homogeneity(z_calc, locs2, radius)
                
                # saves result if improvement to homogeneity is found
                if area2 < area:
                    locs = np.copy(locs2)
                    area = area2
                    break

            # if no improvments are found the wires are returned to their position at the start of the iteration
            locs1 = np.copy(locs)
            locs2 = np.copy(locs)
            
            # if the final iteration shows no improvement the displacement distance is decreased
            # can change factor 2 to adjust the decrease, must be > 1
            if i == a[-1]:
                wire_displacement /= 2

    end_time = time()

    print("\nOptimization complete")
    print("Time elapsed: {:>5.2f}s".format(np.round(end_time-start_time, 2)))

    folder = 'Results-' + datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    Path(folder).mkdir(parents=True, exist_ok=True)

    # create a pandas dataframe that holds wire turn radii, wire positions, and wire radius
    df = pd.DataFrame()
    for i in range(0, turns):
        df['r{}'.format(i+1)] = np.full(windings, radius[0, 0, i])
    df['z'] = locs[0, :, 0]
    df['wire_radius'] = np.full(windings, wire_radius)
    df.to_csv('{}/wire_locations.csv'.format(folder), index=False)

    # draw the wire positions as an .svg file
    try:
        import draw_grooves
        print("\nDrawing the wire grooves...\n")
        draw_grooves.main(folder	)
    except ImportError:
        print("\nError importing module 'draw_grooves'. Check that the module is in the file path or that all dependencies have been installed.\n")

    try:
        import plot_field
        print("\nPlotting the axial magnetic field...\n")
        plot_field.main(folder)
    except ImportError:
        print("\nError importing module 'plot_field'. Check that the module is in the file path or that all dependencies have been installed.\n")


if __name__ == '__main__':
    main()
    
