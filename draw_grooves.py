import numpy as np
import pandas as pd
import drawSvg as draw
import sys


def groove(drawing: draw.Drawing, group: np.ndarray, former_radius: float, inner_radius: float, wire_radius: float, style='normal') -> None:

    """
    drawing: a drawSVG drawing object
    group: array representing wires in a single bundle
    former_radius: radius of coil former
    inner_radius: turn radius of innermost wire
    wire_radius: radius of a single wire, 32 AWG, etc...
    style: style of which to draw the grooves
    'normal' denotes a square groove with rounding where the wires meet the coil former
    'chamfer' denotes the same groove with a 60 degree chamfer on the upper edge for ease of 3d modeling 
    Append a groove drawing to the canvas
    """

    first_wire = group[0]  # first wire in bundle
    r_ex = 0.05  # extra groove spacing
    n = len(group)

    p = draw.Path(stroke_width=0.01, stroke='black', fill='none')

    p.m(former_radius + r_ex, first_wire - wire_radius - r_ex)  # starting point
    p.h(inner_radius - former_radius - r_ex)  # horizontal line from starting point to lower-left of first wire
    
    if style == 'normal':
        if n == 1:
            p.arc(inner_radius, first_wire, wire_radius + r_ex, 270, 90, cw=True, includeM=False)  # 180 degree arc around first wire
        else:
            p.arc(inner_radius, first_wire, wire_radius + r_ex, 270, 180, cw=True, includeM=False)  # 90 degree arc around first wire
            p.v(2*(n-1)*wire_radius)  # vertical line between wires of group
            p.arc(inner_radius, first_wire+2*(n-1)*wire_radius, wire_radius + r_ex, 180, 90, cw=True, includeM=False)  # 90 degree arc around last wire
        p.h(former_radius + r_ex - inner_radius)  # horizontal line from top-left of last wire to coil former
    
    if style == 'chamfer':
        if n == 1:
            p.arc(inner_radius, first_wire, wire_radius + r_ex, 270, 120, cw=True, includeM=False)
            p.l(former_radius + r_ex - inner_radius - (wire_radius + r_ex)*np.cos(2*np.pi/3),
                (former_radius + r_ex - inner_radius - (wire_radius + r_ex)*np.cos(2*np.pi/3))*np.tan(np.pi/6))
        else:
            p.arc(inner_radius, first_wire, wire_radius + r_ex, 270, 180, cw=True, includeM=False)
            p.v(2*(n-1)*wire_radius)
            p.arc(inner_radius, first_wire+2*(n-1)*wire_radius, wire_radius + r_ex, 180, 120, cw=True, includeM=False)
            p.l(former_radius + r_ex - inner_radius - (wire_radius + r_ex)*np.cos(2*np.pi/3),
                (former_radius + r_ex - inner_radius - (wire_radius + r_ex)*np.cos(2*np.pi/3))*np.tan(np.pi/6))

    p.Z()  # connect last point to starting point, should always be a vertical line
    drawing.append(p)


def main(path):

    df = pd.read_csv('{}/wire_locations.csv'.format(path), header=0)
    df *= 1000  # converting to mm
    
    wire_locations = np.array(df['z'])   
    wire_radius = df.iloc[0, -1]  # wire radius converted to mm 
    former_radius = df.iloc[0, 0] + wire_radius  # radius of coil former
    inner_radius = df.iloc[0, -3]  # center of inner wire position
    
    drawing = draw.Drawing(2.1*former_radius, 2.1*wire_locations[-1], origin='center')

    #  draws wire grooves
    wire_groups = np.split(wire_locations, np.where(np.diff(wire_locations) > 2.5*wire_radius)[0]+1)  # finds bundled wire groups
    for group in wire_groups:
        groove(drawing, group, former_radius, inner_radius, wire_radius)

    drawing.setRenderSize(w=5000)
    drawing.saveSvg('{}/grooves.svg'.format(path))

    #  draws wires on previous drawing
    for wire in wire_locations:
        for turn in df.iloc[0, :-1]:
            drawing.append(draw.Circle(turn, wire, wire_radius,
                           fill='none', stroke_width=0.01, stroke='black'))

    drawing.setRenderSize(w=5000)
    drawing.saveSvg('{}/grooves_and_wires.svg'.format(path))


if __name__ == '__main__':
    main(sys.argv[1])
