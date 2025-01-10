########################################################
"""
    This file is part of the MOPS-Hub project.
    Author: Ahmed Qamesh (University of Wuppertal)
    email: ahmed.qamesh@cern.ch  
    Date: 29.08.2023
"""
########################################################

import numpy as np
import matplotlib.pyplot as plt
cmap = plt.cm.get_cmap('viridis')  
def analyze_magenteic_field():
    x = np.arange(-5, 5, 1)
    y = np.arange(-7, 7, 1)
    
    # Create a grid of coordinates
    coordinates = [(i, j) for i in x for j in y]
    
    B_field= [230, 260, 230,280,260,290,233,283,266,268,
               300, 299, 304,319,340,353,350,380,347,381,
               291, 300, 300,310,320,320,343,340,324,362,
               283,280,280,293,291,296,322,310,313,345,
               289,280,280,298,280,284,305,294,306,337,
               296,280,283,275,269,279,285,284,300,332,
               295,233,279,271,264,266,276,279,300,327,
               297,284,274,267,263,262,270,276,300,323,
               301,284,268,264,260,261,262,277,300,326,
               301,284,272,256,266,266,270,265,304,328,
               304,294,285,278,283,284,287,240,318,331,
               326,305,316,300,310,308,310,380,337,339,
               337,355,348,343,341,334,351,360,366,359,
               385,394,368,354,334,374,380,380,389,381]  # magnetic field strength at each point (mT)
    
    # Convert coordinates and B_field to NumPy arrays
    coordinates_arr = np.array(coordinates)
    B_field_arr = np.array(B_field)
    # Reshape B_field to fit the 2D grid
    B_field_grid = B_field_arr.reshape(len(y), len(x))
    # Extract unique x and y coordinates
    x_unique = np.unique(coordinates_arr[:, 1])
    y_unique = np.unique(coordinates_arr[:, 1])

    
    # Plotting using plt.streamplot
    plt.figure()
    #plt.scatter(x_points, y_points, c=B_field, cmap=cmap, s=100, edgecolors='k', label='Measurement Points')
    plt.imshow(B_field_grid, cmap=cmap, interpolation='nearest', aspect='auto',origin='lower')
               #extent=[x.min(), x.max(), y.min(), y.max()])
    plt.colorbar(label='Magnetic Field Strength (mT)')
    plt.title('Magnetic Field Map')
    plt.xlabel('X Coordinate [cm]')
    plt.ylabel('Y Coordinate [cm]')
    plt.grid(True)
    plt.savefig(f"{file_names[0][:-4]}_{column}.pdf", bbox_inches='tight')
    #plt.show()



analyze_magenteic_field()
