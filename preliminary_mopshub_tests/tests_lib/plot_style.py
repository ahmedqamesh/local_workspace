########################################################
"""
    This file is part of the MOPS-Hub project.
    Author: Ahmed Qamesh (University of Wuppertal)
    email: ahmed.qamesh@cern.ch  
    Date: 29.01.2022
"""
########################################################
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as style
from cycler import cycler
from matplotlib import cm

# Define the data from the table

plot_h, plot_w = 6,4

plt.rcParams.update({
    'lines.markersize': 3,
    'lines.linewidth': 1.5,
    'figure.figsize': (plot_h, plot_w),  # Adjust the width and height as needed
    'axes.labelsize': 8,
    'axes.titlesize': 8,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'font.size': 8,
    'xtick.direction': 'in',  # Ticks inside
    'xtick.top': True,  # Ticks on top
    'xtick.major.size': 4,  # Larger tick size for major ticks
    'xtick.major.width': 0.8,  # Larger tick width for major ticks
    'xtick.minor.size': 2,  # Tick size for minor ticks
    'xtick.minor.width': 0.8,  # Tick width for minor ticks
    'axes.formatter.useoffset': False,  # Disable offset for tick labels
})

#style.use('tableau-colorblind10')
# Define the colormap
cmap = cm.get_cmap('tab20', 10)  # Get 20 distinct colors from tab20b
# Create a list of colors from the colormap
cmap_colors = cmap.colors

col_row =  ["#3a3487", "#f7e5b2", "b", "g", "r", "y", "c", "m", "lime", "#943ca6", "#df529e", "#f49cae", "tab:blue",
            "tab:orange", "tab:purple", "tab:pink", "#332d58", "#3b337a", "#365a9b", "#2c4172", "#2f3f60", "#3f5d92","lavender", 
            "#4e7a80", "#60b37e", "darkgoldenrod", "darksalmon", "darkgreen", "#904a5d", "#5d375a", "#4c428d", "#31222c", "#b3daa3","#f4ce9f", "#ecaf83"]
matplotlib.rcParams["axes.prop_cycle"] = cycler(color=cmap_colors)
