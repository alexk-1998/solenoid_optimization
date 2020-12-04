import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
from matplotlib import gridspec


def field_norm(z_pts: np.ndarray, wire_locations: np.ndarray, p: np.ndarray) -> tuple:

    """
    z_pts: an array consisting of points along the z-axis (0, 0, z) for magnetic field calculations
    wire_locations: an array consisting of the z-position of individual coil windings
    p: an array consisting of the radius of wire turns within a single groove
    Return the normalized magnetic field and the non-normalized central magnetic field
    """
    
    mu0 = 4*np.pi*10**(-7)  # permeability of free space
    B_c = np.sum(mu0*p**2/(p**2 + wire_locations**2)**1.5, axis=(1, 2))/2
    B_z = np.sum(mu0*p**2/(p**2 + (z_pts - wire_locations)**2)**1.5, axis=(1, 2))/2
    return B_z/B_c, float(B_c)


def main(path):

    wire_locations = pd.read_csv('{}/wire_locations.csv'.format(path), header=0)

    p = np.array(wire_locations.iloc[0, :-2])  # radii of wire turns in a single groove
    p_avg = np.average(p)  # average radius for comparison with alternative coil designs
    loops = len(p)
    p = p.reshape((1, 1, loops))

    ng_wire_locations = np.array(wire_locations['z'])
    windings = len(ng_wire_locations)
    ng_wire_locations = ng_wire_locations.reshape((1, len(ng_wire_locations), 1))
    end_point = ng_wire_locations[0, -1, 0]

    # solenoid with equal length and radius to ng coil
    sol_wire_locations = np.linspace(-end_point, end_point, windings)
    sol_wire_locations = sol_wire_locations.reshape((1, windings, 1))
    
    # helmholtz coil with equal length to ng coil
    helm1_wire_locations = np.array([end_point, -end_point])
    helm1_wire_locations = helm1_wire_locations.reshape((1, 2, 1))
    
    # helmholtz coil with equal radius to ng coil
    helm2_wire_locations = np.array([p_avg/2, -p_avg/2])
    helm2_wire_locations = helm2_wire_locations.reshape((1, 2, 1))
    
    # lee-whiting coil with equal length to ng coil
    lw1_outer_wire = np.full(9, end_point)
    lw1_inner_wire = np.full(4, 2432*end_point/9408)
    lw1_wire_locations = np.concatenate((lw1_outer_wire, lw1_inner_wire, -lw1_inner_wire, -lw1_outer_wire))
    lw1_wire_locations = lw1_wire_locations.reshape((1, 26, 1))
   
    # lee-whiting coil with equal radius to ng coil 
    lw2_outer_wire = np.full(9, 0.9408*p_avg)
    lw2_inner_wire = np.full(4, 0.2432*p_avg)
    lw2_wire_locations = np.concatenate((lw2_outer_wire, lw2_inner_wire, -lw2_inner_wire, -lw2_outer_wire))
    lw2_wire_locations = lw2_wire_locations.reshape((1, 26, 1))

    calculation_number = 1000  # number of magnetic field calculation points
    z_calc = np.linspace(-end_point, end_point, calculation_number).reshape((calculation_number, 1, 1))  # array of calculation points

    field_ng, center_ng = field_norm(z_calc, ng_wire_locations, p)
    field_sol, center_sol = field_norm(z_calc, sol_wire_locations, p_avg)
    field_helm1, center_helm1 = field_norm(z_calc, helm1_wire_locations, end_point*2)
    field_helm2, center_helm2 = field_norm(z_calc, helm2_wire_locations, p_avg)
    field_lw1, center_lw1 = field_norm(z_calc, lw1_wire_locations, end_point/0.9408)
    field_lw2, center_lw2 = field_norm(z_calc, lw2_wire_locations, p_avg)

    print('\n Coil | B(0) (\u03BCT/A*turns) | R (cm) | L (cm)')
    print('--------------------------------------------')
    print(' NG   | {:>9.6f}         | {:>6.3f} | {:>6.3f}'.format(np.round(center_ng*10**6/(windings*loops), 6), np.round(100*p_avg, 2), np.round(100*end_point, 2)))
    print(' Sol  | {:>9.6f}         | {:>6.3f} | {:>6.3f}'.format(np.round(center_sol*10**6/windings, 6), np.round(100*p_avg, 2), np.round(100*end_point, 2)))
    print(' H 1  | {:>9.6f}         | {:>6.3f} | {:>6.3f}'.format(np.round(center_helm1*10**6/2, 6), np.round(200*end_point, 2), np.round(100*end_point, 2)))
    print(' H 2  | {:>9.6f}         | {:>6.3f} | {:>6.3f}'.format(np.round(center_helm2*10**6/2, 6), np.round(100*p_avg, 2), np.round(50*p_avg, 2)))
    print(' LW 1 | {:>9.6f}         | {:>6.3f} | {:>6.3f}'.format(np.round(center_lw1*10**6/26, 6), np.round(end_point/0.009408, 2), np.round(100*end_point, 2)))
    print(' LW 2 | {:>9.6f}         | {:>6.3f} | {:>6.3f}\n'.format(np.round(center_lw2*10**6/26, 6), np.round(100*p_avg, 2), np.round(94.08*p_avg, 2)))

    fig = plt.figure(figsize=(6, 12))
    gs = gridspec.GridSpec(2, 1, hspace=0.025)
    ax = fig.add_subplot(111)
    ax2 = fig.add_subplot(gs[0])
    ax3 = fig.add_subplot(gs[1])

    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.tick_params(labelcolor='w', top=False, bottom=False,
                   left=False, right=False)
    ax.set_ylabel('Normalized Magnetic Field', fontsize=13, labelpad=13)

    ax2.plot(100*z_calc[:, 0, 0], field_ng, label='NG')
    ax2.plot(100*z_calc[:, 0, 0], field_sol, label='Sol', ls='--')
    ax2.plot(100*z_calc[:, 0, 0], field_lw1, label='LW #1', ls=':')
    ax2.plot(100*z_calc[:, 0, 0], field_helm1, label='Helm #1', ls='-.')
    ax2.tick_params(labelsize=13, top=True, right=True,
                    direction='in', which='both')
    ax2.xaxis.set_major_formatter(tk.NullFormatter())
    ax2.legend(loc=8, fontsize=13, handlelength=1)

    ax3.plot(100*z_calc[:, 0, 0], field_ng, label='NG')
    ax3.plot(100*z_calc[:, 0, 0], field_sol, label='Sol', ls='--')
    ax3.plot(100*z_calc[:, 0, 0], field_lw2, label='LW #2', ls=':')
    ax3.plot(100*z_calc[:, 0, 0], field_helm2, label='Helm #2', ls='-.')
    ax3.set_xlabel('z-position (cm)', fontsize=13)
    ax3.tick_params(labelsize=13, top=True, right=True,
                    direction='in', which='both')
    ax3.legend(loc=8, fontsize=13, handlelength=1)
    plt.savefig('{}/field_profile.eps'.format(path), bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(6, 2))
    plt.vlines(100*ng_wire_locations, 0, 1, color='C0')
    plt.xlabel('Wire Positions (cm)', fontsize=13)
    plt.yticks([], [])
    plt.tick_params(labelsize=13, top=True, direction='in', which='both')
    plt.savefig('{}/wire_locations.eps'.format(path), bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    main(sys.argv[1])
