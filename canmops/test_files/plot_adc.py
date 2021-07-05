import pandas as pd
import matplotlib as mpl
import numpy as np
import csv
import tables as tb
from matplotlib import style
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as p
import seaborn as sns 
import matplotlib.pyplot as plt 
#plt.style.use('ggplot')
import scipy
import os
import numpy as np
rootdir = os.path.dirname(os.path.abspath(__file__))
data = pd.read_csv(rootdir[:-11] + "/output_data/adc_data.csv", delimiter=",", header=0)
# I am defining two arrays for all the possible tests and operations
operations = ['TimeStamp', 'Channel', "Id", "DLC", "ADCChannel", "ADCData" , "ADCDataConverted"]

pdf_file = rootdir[:-11] + "/output_data/adc_data.pdf"
Pdf = PdfPages(pdf_file)
# Filter the data according to a specific  operation (Which ADC channel)
fig, ax = plt.subplots()
target = 20 # we have 32 ADC channels from 0-31
condition = (data["ADCChannel"] == target)
respondant = data[condition]
ax.plot(respondant["ADCDataConverted"], label="ADC channel No.%i"%target) 
ax.ticklabel_format(useOffset=False)
ax.legend(loc="upper left", prop={'size': 8})
ax.autoscale(enable=True, axis='x', tight=None)
ax.grid(True)
ax.set_ylabel(r'ADC value [V]')
ax.set_xlabel("time [ms]")
plt.tight_layout()    
Pdf.savefig()
plt.close(fig)
Pdf.close()