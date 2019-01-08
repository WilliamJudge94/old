import unittest
import sys
sys.path.append('/home/will/Research/UIC/SXDM/')
from SXDM import *
#%matplotlib notebook This will make the plots interactive but also ruin some of the scripts
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from tqdm import tqdm
from os import walk
from PIL import Image
import numpy as np
import scipy.misc
from scipy.misc import imsave
import cv2
import matplotlib.pyplot as plt1
from scipy.ndimage import median_filter
import imageio
import os
import math
from math import *
import scipy as sp
from scipy import signal
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.io import loadmat
import time
import random
import logging
import warnings
import shutil
import psutil
import matplotlib.patches as patches
from matplotlib.patches import Circle

def mem_logger(num):
    mems=psutil.virtual_memory()
    available=str(round(mems[1]/1000000000,4))
    used=str(round(mems[3]/1000000000,4))
    percent=str(round(mems[2],1))
    log.info(str(num)+'    RAM  - Available: '+available+' - Used: '+used+' - Percent: '+percent+' -')
log=logging.getLogger(__name__)



class SXDMTest(unittest.TestCase):


 
    def setUp(self):
        self.li0_5=SXDM(fov=1,
                   scanlist=['247','254','261'],
                   sample='sample2',
                   folder_path='/home/will/Desktop/Processed_Data/SXDM_FePO4_Master/')

    def tearDown(self):
        pass
        
    def test_summeddif_cal(self):
        self.assertEqual(np.array_equal(li0_5.s_arr,testthing),True)








