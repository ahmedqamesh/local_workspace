from __future__ import division
import os.path
import numpy as np
import logging
import yaml
import numba
import tables as tb
from tqdm import tqdm
from scipy.optimize import curve_fit
loglevel = logging.getLogger('Analysis').getEffectiveLevel()
from analysis import logger
np.warnings.filterwarnings('ignore')

class Analysis(object):
    
    def __init__(self):
        self.log = logger.setup_derived_logger('Analysis')
        self.log.info('Analysis initialized')
        
    # Fit functions
    def linear(self, x, m, c):
        return m * x + c

    def quadratic(self, x, a, b, c):
        return a * x**2 + b * x + c

    def red_chisquare(self, observed, expected, observed_error, popt):
        return np.sum(((observed - expected) / observed_error)**2 / (len(observed_error) - len(popt) - 1))

    def ln(self, x, a, b, c):
        return a * np.log(x + b) - c

    def exp(self, x, a, b, c):
        return a * np.exp(-b * x) + c

    def Inverse_square(self, x, a, b, c):
        return a / (x + b)**2 - c
    
 
if __name__ == "__main__":
        pass
