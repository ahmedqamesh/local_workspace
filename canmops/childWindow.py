from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5.QtCore    import *
from PyQt5.QtGui     import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui

from graphicsUtils import dataMonitoring , logWindow
import numpy as np
import os
import binascii
import yaml
import logging
rootdir = os.path.dirname(os.path.abspath(__file__)) 

class ChildWindow(QWidget):  

    def __init__(self, parent=None):
       super(ChildWindow, self).__init__(parent)
    
    def outputChildWindow(self, ChildWindow, comunication_object="Normal"):
        ChildWindow.setObjectName("OutputWindow")
        ChildWindow.setWindowTitle("Output Window")
        ChildWindow.resize(600, 600)  # w*h
        logframe = QFrame(ChildWindow)
        logframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(logframe)
        self.WindowGroupBox = QGroupBox("")
        logTextBox = logWindow.QTextEditLogger(ChildWindow, comunication_object=comunication_object)
        logLayout = QVBoxLayout()
        logLayout.addWidget(logTextBox.text_edit_widget)
        self.WindowGroupBox.setLayout(logLayout)
        logframe.setLayout(logLayout) 
        
    def trendChildWindow(self, ChildWindow):
        ChildWindow.setObjectName("TrendingWindow")
        ChildWindow.setWindowTitle("Trending Window")
        ChildWindow.resize(900, 500)  # w*h
        logframe = QFrame(ChildWindow)
        logframe.setLineWidth(0.6)
        ChildWindow.setCentralWidget(logframe)
        
        trendLayout = QHBoxLayout()
        self.WindowGroupBox = QGroupBox("")
        self.Fig = dataMonitoring.LiveMonitoringData()
        self.Fig.setStyleSheet("background-color: black;"
                                        "color: black;"
                                        "border-width: 1.5px;"
                                        "border-color: black;"
                                        "margin:0.0px;"
                                        #"border: 1px "
                                        "solid black;")

        self.distribution = dataMonitoring.LiveMonitoringDistribution()
        VBox = QVBoxLayout()
        #VBox.addStretch(1)
        VBox.addWidget(self.distribution)
        
        HBox = QHBoxLayout()
        indexLabel = QLabel("Period[s]", self)
        indexLabel.setText("Period [s]:")
        
        self.timeTextBox = QLineEdit("200", self)
               
        start_button = QPushButton("")
        start_button.setIcon(QIcon('graphicsUtils/icons/icon_start.png' ))
        start_button.clicked.connect(self.start_timer)
        
        
        pause_button = QPushButton("")
        pause_button.setIcon(QIcon('graphicsUtils/icons/icon_pause.png' ))
        pause_button.clicked.connect(self.Fig.stop_timer)
        pause_button.clicked.connect(self.distribution.stop_timer)
        
        stop_button = QPushButton("")
        stop_button.setIcon(QIcon('graphicsUtils/icons/icon_close.png' ))
        stop_button.clicked.connect(self.Fig.stop_timer)
        stop_button.clicked.connect(self.distribution.stop_timer)
        stop_button.clicked.connect(ChildWindow.close)        
        
        HBox.addWidget(self.timeTextBox) 
        HBox.addWidget(start_button)
        HBox.addWidget(pause_button)
        HBox.addWidget(stop_button)

        VBox.addLayout(HBox)
        
        trendLayout.addLayout(VBox)
        trendLayout.addWidget(self.Fig)
        
        self.WindowGroupBox.setLayout(trendLayout)
        logframe.setLayout(trendLayout) 
        ChildWindow.show()
    def clicked(self, q):
        print("is clicked")
    
    def start_timer(self):
        period = int(self.timeTextBox.text())
        self.Fig.initiate_timer(period = period)
        self.distribution.initiate_timer(period = period)
        
    # setter method
    def open(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File')
        with open(filename[0], 'r') as ymlfile:
            cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
        return cfg
                 
if __name__ == "__main__":
    pass

