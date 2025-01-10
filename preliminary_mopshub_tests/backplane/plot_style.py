import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as style
from cycler import cycler
from matplotlib import cm

# Define the data from the table

plot_h, plot_w = 6,4

matplotlib.rcParams['lines.markersize'] = 2.5
matplotlib.rcParams['lines.linewidth'] = 1.5
# Set plot dimensions 
matplotlib.rcParams['figure.figsize'] = (plot_h, plot_w)  # Adjust the width and height as needed
# Set label font size
matplotlib.rcParams['axes.labelsize'] = 8
matplotlib.rcParams['axes.titlesize'] = 8
matplotlib.rcParams['xtick.labelsize'] = 8 
matplotlib.rcParams['ytick.labelsize'] = 8 
# Set legend font size
matplotlib.rcParams['legend.fontsize'] = 8
# Set text font size
matplotlib.rcParams['font.size'] = 8  # You can adjust the size as needed




#style.use('tableau-colorblind10')
# Define the colormap
cmap = cm.get_cmap('tab20b', 10)  # Get 20 distinct colors from tab20b
# Create a list of colors from the colormap
cmap_colors = cmap.colors

col_row =  ["lavender", "#3a3487", "#f7e5b2", "b", "g", "r", "y", "c", "m", "lime", "#943ca6", "#df529e", "#f49cae", "tab:blue",
            "tab:orange", "tab:purple", "tab:pink", "#332d58", "#3b337a", "#365a9b", "#2c4172", "#2f3f60", "#3f5d92",
            "#4e7a80", "#60b37e", "darkgoldenrod", "darksalmon", "darkgreen", "#904a5d", "#5d375a", "#4c428d", "#31222c", "#b3daa3","#f4ce9f", "#ecaf83"]
matplotlib.rcParams["axes.prop_cycle"] = cycler(color=cmap_colors)
