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

np.warnings.filterwarnings('ignore')

class Analysis(object):

    def __enter__(self):
        return self

if __name__ == "__main__":
    pass
