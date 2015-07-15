from __future__ import division, print_function
import numpy as np
import matplotlib.pyplot as pl
from matplotlib.ticker import MaxNLocator
import ketu, urllib2, sys, pickle, transit, h5py, shutil
from astropy.io import fits
import remove_EB as remEB
import data

def get_lc_path(epicID, campaign, directory, tail=""):
    '''This function navigates the gnarly subdirectory structure of the k2 lightcurve directories
    epicID--integer indicating the K2 object ID associated with the file
    campaign--integer indicated which campaign the lightcurve is from
    directory--this is the path to where the lightcurves folder is: on linux '/k2_data/'; on macs '/Volumes/k2_data/'
    tail--if you want a clipped or other type of version of the lightcurve tail can be added at the end of the filename before .fits
    '''
    if directory[-1] != "/":
        directory += "/"
    epicIDstr, campaignstr= str(epicID), str(campaign)
    path = directory + "lightcurves/c" + campaignstr + "/"  + epicIDstr[0:4] + "00000/" + epicIDstr[4:6] + "000/"
    path += "ktwo" + epicID + "-c0" + campaignstr + "_lpd-lc" + tail + ".fits"
    return path