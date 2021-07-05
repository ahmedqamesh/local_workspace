from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.animation as animation
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime, Qt, QTimer, pyqtSlot
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import random
from random import randint
import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph import *
import time
from IPython import display
import matplotlib as mpl
from matplotlib.figure import Figure
from analysis import analysis_utils
from graphics_utils import mainWindow , dataMonitoring
from PyQt5 import QtWidgets, QtCore, uic
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
#app = QtWidgets.QApplication(sys.argv)
#MessageWindow = QMainWindow()
#mainWindow.MainWindow().adcChannelChildWindow(MessageWindow)
#dataMonitoring.ADCMonitoringData(MessageWindow)
#MessageWindow.show()
#app.exit(app.exec_())
