from __future__ import division, print_function
import numpy as snp
import matplotlib.pyplot as pl
from matplotlib.ticker import MaxNLocator
import sys, pickle, h5py, shutil
from astropy.io import fits
import data, query, plot
from astropy.table import Table
from astropy.coordinates import Angle

C0INITIALTIME = 2456773
C1INITIALTIME = 2456810 
C2INITIALTIME = 2456900


def get_coords(EPIC):
    # Construct a MAST URL to retrieve info for this target:
    base_url = "http://archive.stsci.edu/k2/data_search/search.php?action=Search&outputformat=CSV&ktc_k2_id="
    url = base_url + str(EPIC)
    data = Table.read(url, format='ascii.csv')
    ra = data[1]['RA (J2000)']
    dec = data[1]['Dec (J2000)']
    #print ra, dec
    #return ra,dec
    radeg = Angle(ra + ' hours').deg
    decdeg = Angle(dec + ' degrees').deg
    return [radeg, decdeg]
