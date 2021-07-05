import sys
from typing import *
from PyQt5 import *
from PyQt5.QtWidgets import *
#from analysis import logger

import logging

class QTextEditLogger(logging.Handler):
    def __init__(self,
                 loglevel = logging.DEBUG, 
                 logformat="%(asctime)s - %(message)s",
                 comunication_object = None):
        super().__init__() 
        color = self.set_object_color(comunication_object)        
       
        self.text_edit_widget = QPlainTextEdit()
        self.text_edit_widget.setReadOnly(True)
        self.text_edit_widget.setStyleSheet(color)

        # create logger
        logger = logging.getLogger()
        logger.setLevel(loglevel) # Controlling the logging level

        # create formatter
        formatter = logging.Formatter(logformat)
        
        self.setFormatter(formatter)
        logger.addHandler(self)

    def emit(self, record):
        msg = self.format(record)
        self.text_edit_widget.appendPlainText(msg)
        
    def set_object_color(self, comunication_object):
        if comunication_object == "SDO_TX":
            color =  "color: #336600;"
        if comunication_object == "SDO_RX":
            color =  "color: #CC0066;"
            
        if comunication_object == "decoded":
            color =  "color: #E4DFA3;"
        else:
            color ="color: #000000;"
        return color

if __name__ == "__main__":
    pass


        