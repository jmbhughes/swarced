from __future__ import division, print_function
from matplotlib import rcParams
rcParams["savefig.dpi"] = 100
rcParams["font.size"] = 20
import h5py
import transit
import numpy as np
import matplotlib.pyplot as pl
from matplotlib.ticker import MaxNLocator
import ketu
import urllib2
import sys
from astropy.io import fits
from eliminate_eclipses import *

def getQuery(epicID, campaign):
    '''Format a default query for the ketu pipeline'''
    campaign = str(campaign)
    path = "/k2_data/lightcurves/" + "c" + campaign + "/" +  epicID[0:4] + "00000/" + epicID[4:6] + "000/"  
    q = dict(
        folder = "/k2_data",
        light_curve_file = path + "ktwo" + epicID + "-c0" + campaign + "_lpd-lc.fits",
        #target_pixel_file="fm15_ag/dat/ktwo" + epicID + "-c0" + campaign + "_lpd-targ.fits.gz",
        #initial_time=1975.,
        basis_file= "/k2_data/elcs/c1.h5",
        nbasis=150,
        catalog_file= "/k2_data/catalogs/epic.h5",
        #time_spacing=0.02,
        time_spacing=0.1,
        durations=[0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        min_period=4.0,
        max_period=70.0,
        npeaks=3,
        summary_file="test",
    )
    if campaign == "0":
        q['basis_file'] = "/k2_data/elcs/c0.h5"
    elif campaign == "2":
        q['basis_file'] = "/k2_data/elcs/c2-norm.h5"
    else:
        q['basis_file'] = "/k2_data/elcs/c?-norm.h5"
    return q

def getEBQuery(epicID, campaign):
    '''Format a default query for the ketu pipeline'''
    campaign = str(campaign)
    folder = "/k2_data/eb_removed/"
    q = dict(
        light_curve_file = folder + "ktwo" + epicID + "-c0" + campaign + "_lpd-lc.fits",
        #target_pixel_file="fm15_ag/dat/ktwo" + epicID + "-c0" + campaign + "_lpd-targ.fits.gz",
       #initial_time=1975.,
        basis_file= "/k2_data/elcs/c0.h5",
        nbasis=150,
        catalog_file= "/k2_data/catalogs/epic.h5",
        time_spacing=0.1,
        durations=[0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        min_period= 4.0,
        max_period=70.0,
        npeaks=3,
    )
    #if campaign == "0":
    #    q['basis_file'] = folder + "c0.h5"
    #elif campaign == "2":
    #    q['basis_file'] = folder + "c2-norm.h5"
    #else:
    #    q['basis_file'] = folder + "c?-norm.h5"
    return q


def analyze(query):
    '''Pass a target through the ketu pipeline
    Key Terms:
    epicID--a string indicating the EPIC ID of the chosen target
    campaign--a string indicating which campaign of K2 data this target is in
    
    Return:
    A pipeline result object for examination
    '''
    #query = getQuery(epicID,campaign)
    pipe = ketu.k2.Data(basepath="/k2_data/eb_removed/cache/")
    pipe = ketu.k2.Likelihood(pipe)
    pipe = ketu.OneDSearch(pipe)
    pipe = ketu.IterativeTwoDSearch(pipe)
    #pipe = ketu.TwoDSearch(pipe)
    result = pipe.query(**query)
    return result

def retrieve(epicID, campaign, inpath="/k2_data/lightcurves/"):
    '''Provides access to the time and flux data from a light curve given the EPIC ID and campaign'''
    campaign = str(campaign)
    epicID = str(epicID)
    if inpath == "/k2_data/lightcurves/":
        path = inpath + "c" + campaign + "/" +  epicID[0:4] + "00000/" + epicID[4:6] + "000/" 
    else:
        path = inpath
    fn = path + "ktwo" + epicID + "-c0" + campaign + "_lpd-lc.fits"
    f = fits.open(fn)
    return f[1].data['time'] + f[1].header['BJDREFI'],f[1].data['flux']

def edit(mask, epicID, campaign, inpath="/k2_data/lightcurves/", outpath="/k2_data/eb_removed/"):
    '''Allows one to directly alter a lightcurve by applying a mask to a K2 lightcurve'''
    epicID, campaign = str(epicID),str(campaign)
    if inpath == "/k2_data/lightcurves/":
        path = inpath + "c" + campaign + "/" +  epicID[0:4] + "00000/" + epicID[4:6] + "000/" 
    else:
        path = inpath
    fn = "ktwo" + epicID + "-c0" + campaign + "_lpd-lc.fits"
    f = fits.open(path + fn)
    f[1].data = f[1].data[mask]
    f.writeto(outpath + fn, clobber=True)
    return
