import numpy as np
#import h5py
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
import tables as tb
filename = "/home/silab62/git/XrayMachine_Bonn/Calibration_Curves/without_Al_Filter/beamspot/60cm/beamspot_60cm.h5"

# get data
# f = h5py.File(filename, 'r')
# data = np.array(f["beamspot"])
with tb.open_file(filename, 'r') as in_file:
    data = in_file.root.beamspot[:]
                
# Calibration Factor
Factor = 9.81  # diode B
#  Factor = 9.76 # diode A
Background = 5.7*10**(-9)  # 5 nA
data = (data-Background)*Factor*10**9

# OF module
mod_length = 84.975/10.0
mod_width = 15.4/10.0

# DHP
dhp_length = 4.2/10.0
dhp_width = 3.28/10.0

# DCD
dcd_length = 5.13/10.0
dcd_width = 3.41/10.0

# Switcher
sw_length = 3.6/10.0
sw_width = 1.89/10.0
sw_locs = [8.96, 9.92, 10.88, 10.88, 10.88, 9.235, 19.338]

# module collection
mod_color = "black"
# module outline
mod_patches = [Rectangle((0, 0), mod_length, mod_width, fill=False, color=mod_color, linewidth=2)]
# dhps
for i in range(4):
    mod_patches.append(Rectangle((mod_length-1.3494-dhp_length/2, mod_width-0.2759-dhp_width/2-0.35*i), dhp_length, dhp_width, fill=False, color=mod_color, linewidth=1.5))
# dcds
for i in range(4):
    mod_patches.append(
        Rectangle((mod_length - 1.9338 - sw_length / 2, mod_width - 0.2759 - dcd_width / 2 - 0.35 * i), dcd_length,
                  dcd_width, fill=False, color=mod_color, linewidth=1.5))
# switchers
for i in range(6):
    mod_patches.append(
        Rectangle((mod_length - sum(sw_locs[:-i-3:-1])/10.0 - sw_length / 2, mod_width - 0.1278 - sw_width / 2), sw_length,
                  sw_width, fill=False, color=mod_color, linewidth=1.5))
a_x1 = -mod_length/2 - 1.0 +1.3494-dhp_length/2
a_x2 = +mod_length/2 - 1.0
a_y1 = -mod_width/2 # - 1.0
a_y2 = +mod_width/2 # - 1.0
mod_trans_a = mpl.transforms.Affine2D().translate(-mod_length/2, -mod_width/2) + mpl.transforms.Affine2D().rotate_deg(180) + mpl.transforms.Affine2D().translate(-1.0,0)
p_mod = PatchCollection(mod_patches, match_original=True)

nullfmt = NullFormatter()         # no labels

# definitions for the axes
left, width = 0.1, 0.60
bottom, height = 0.1, 0.60
bottom_p = bottom + height + 0.02
left_p = left + width + 0.02

rect_spot = [left, bottom, width, height]
rect_projx = [left, bottom_p, width, 0.2]
rect_projy = [left_p, bottom, 0.2, height]

# start with a rectangular Figure
plt.figure() # 1, figsize=(8, 8))

axSpot = plt.axes(rect_spot)
axProjx = plt.axes(rect_projx)
axProjy = plt.axes(rect_projy)

# no labels
axProjx.xaxis.set_major_formatter(nullfmt)
axProjy.yaxis.set_major_formatter(nullfmt)

# the scatter plot:
im_spot = axSpot.imshow(data, origin="upper", interpolation="None", aspect="auto", extent=(-6.5, +6.5, +6.5, -6.5))

axSpot.plot((-6.5, +6.5), (0, 0), color="white", lw=1)
axSpot.plot((0, 0), (-6.5, +6.5), color="white", lw=1)
"""
mod_left_edge = -mod_length/2-1.0
mod_top_edge = -mod_width/2-1.0
mod_rect = Rectangle((mod_left_edge, mod_top_edge), mod_length, mod_width, fill=False, color="red", linewidth=2)
dhp1_rect = Rectangle((mod_left_edge+1.3494-dhp_length/2, mod_top_edge+0.2759-dhp_width/2), dhp_length, dhp_width, fill=False, color="red", linewidth=1.5)
dhp2_rect = Rectangle((mod_left_edge+1.3494-dhp_length/2, mod_top_edge+0.2759-dhp_width/2+0.35), dhp_length, dhp_width, fill=False, color="red", linewidth=1.5)
dhp3_rect = Rectangle((mod_left_edge+1.3494-dhp_length/2, mod_top_edge+0.2759-dhp_width/2+0.35*2), dhp_length, dhp_width, fill=False, color="red", linewidth=1.5)
dhp4_rect = Rectangle((mod_left_edge+1.3494-dhp_length/2, mod_top_edge+0.2759-dhp_width/2+0.35*3), dhp_length, dhp_width, fill=False, color="red", linewidth=1.5)
patches = [mod_rect, dhp1_rect, dhp2_rect, dhp3_rect, dhp4_rect]
p = PatchCollection(patches, match_original=True)
"""

# t1 = mpl.transforms.Affine2D().rotate_deg(-90) + mpl.transforms.Affine2D().translate(0, -1) + axSpot.transData
# p.set_transform(t1)
# axSpot.add_collection(p)
p_mod.set_transform(mod_trans_a+axSpot.transData)
axSpot.add_collection(p_mod)
"""
axSpot.add_patch(mod_rect)
axSpot.add_patch(dhp1_rect)
axSpot.add_patch(dhp2_rect)
axSpot.add_patch(dhp3_rect)
axSpot.add_patch(dhp4_rect)
"""
axSpot.set_xlabel("x [cm]")
axSpot.set_ylabel("z [cm]")

axrange=np.arange(-6, +6.5, 0.5)
print axrange
print data
print data[:, 12]
print data[12, :]

axProjx.bar(x=axrange, height=data[12, :].astype(np.float), width=0.3)
axProjx.set_ylabel("dose rate [krad/h]")
axProjx.axvline(a_x1, color=mod_color)
axProjx.axvline(a_x2, color=mod_color)

axProjy.barh(y=axrange, width=data[:, 12].astype(np.float), height=0.3)
axProjy.axhline(a_y1, color=mod_color)
axProjy.axhline(a_y2, color=mod_color)
axProjy.set_xlabel("dose rate [krad/h]")

axProjx.set_xlim(axSpot.get_xlim())
axProjy.set_ylim(axSpot.get_ylim())

axProjy.set_xlim(axProjx.get_ylim())

textleft = 'PXD outer forward module'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
axSpot.text(0.05, 0.95, textleft, transform=axSpot.transAxes, fontsize=8, verticalalignment='top', bbox=props)

cbar = plt.colorbar(im_spot)
cbar.set_label("dose rate [krad/h]")

plt.suptitle("beamspot at distance 60 cm, tube parameter: 40 kV, 50 mA, no filter")

plt.savefig(filename[:-3]+".png")
plt.savefig(filename[:-3]+".pdf")
plt.show()