'''This is the overhead init module for the Swarced package. The initial times given below are the Julian dates for the lightcurves 
in the appropriate campaigns where all data after should be usable (assuming it was marked as good quality)'''

from __future__ import division, print_function
import matplotlib.pyplot as pl
import sys, pickle, h5py, shutil
from astropy.io import fits
import data, query, plot
from astropy.table import Table
from astropy.coordinates import Angle

C0INITIALTIME = 2456773 #campaign 0
C1INITIALTIME = 2456810 #campaign 1
C2INITIALTIME = 2456900 #campaign 2
C3INITIALTIME = 2456978 #campaign 3

def get_coords(EPIC):
    '''Given an epic ID queries MAST for the period
    Arguments:
    EPIC--a string or integer for the Ecliptic Plane Input Catalog IDD
    '''
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
