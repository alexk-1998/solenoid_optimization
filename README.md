# Solenoid Optimization
Using a standard, evenly-spaced electromagnetic solenoid, wire positions along the coil axis are numerically shifted and optimized in order to produce a numerically generated coil with improved linear magnetic field homogeneity along the coil axis.

# How To Run The Program:
The program can be executed by running `main.py`

```$ python3 main.py```

Once the program has started, the user will prompted to press the enter key to begin the optimization process. After this point, no user input is required.

# Program Output:
Successful termination of the program will produce a results folder, uniquely described by a timestamp in datetime format. The results folder will contain wire positions of the newly optimized coil design as well as magnetic field plots with comparisons to alternative coil designs of similar dimensions. SVG drawings of the groove and wire positions necessary to the construct the coil are also generated.

The output SVG file is intended for importation into 3d modeling software, such as AutoCAD Fusion 360. Imported drawings can be easily used to create wire grooves in a 3d model. Two groove styles (`normal` or `chamfer`) are available for the design and are shown below. The `chamfer` style simply adds a 60 degree chamfer to the upperedge of the groove to avoid issues with sagging during 3d printing. The Style used when drawing the grooves defaults to `normal` but can be changed in the file `draw_grooves.py` by changing the string argument of the function call 


```groove(drawing, group, former_radius, inner_radius, wire_radius)```

to

```groove(drawing, group, former_radius, inner_radius, wire_radius, style='chamfer')```

<p align="center">
  <img src="https://github.com/alexk-1998/solenoid_optimization/blob/master/results_example/normal_example.png" title="Default Groove" width="100" style="margin: 1px 1px 1px 20px;" />
  <img src="https://github.com/alexk-1998/solenoid_optimization/blob/master/results_example/chamfer_example.png" title="Chamfered Groove" width="100" style="margin: 20px 1px 1px 1px;" /> 
</p>

# Notes:
The user has control over several parameters relevant to the design of the coil. These can all be accessed in the file `my_constants.py`.

The execution of `main.py` will automatically create magnetic field plots and SVG drawings prior to termination. If desired, the files `draw_grooves.py` and `plot_field.py` can be executed from command line as well. In this case, it is necessary to provide the programs with the results folder path that contains a valid CSV file with wire positions of a previously generated coil. Using the given example folder `results-example` that contains the file `results-example/wire_locations.csv` the files can be re-run as follows:

```$ python3 plot_field.py results-example```

```$ python3 draw_grooves.py results-example```
