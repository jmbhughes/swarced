from __future__ import division, print_function
from matplotlib import rcParams
rcParams["savefig.dpi"] = 100
rcParams["font.size"] = 10
import numpy as np
import matplotlib.pyplot as pl
from matplotlib.ticker import MaxNLocator
import ketu, urllib2, sys, pickle, transit, h5py
from astropy.io import fits
import remove_EB as remEB

def build_query(epicID, campaign, time_spacing=0.02, durations=[0.05,0.1,0.2]\
 ,min_period = 0.5,max_period=70.0,npeaks=3,path="DEFAULT",fn="DEFAULT", initial_time = 1975.):
    '''Allows the construction of a customized query
        Key-words:
            epicID--the designation for your object
            campaign--which K2 campaign the object is in
            time_spacing--the grid resolution in days
            durations--the tranist durations in days to test
            min_period--the minimum period in days to test
            max_period--the maximum period in days to test
            npeaks--the number of peaks to determine
            path--the path to the lightcurve, if default use /k2_data
            fn--the filename of the lightcurve, if default us /k2_data
    '''
    epicID, campaign = str(epicID), str(campaign)
    #This is just a lazy method to format the default directory for my tests
    if path == "DEFAULT":
        path = "/k2_data/lightcurves/" + "c" + campaign + "/"
        path = path + epicID[0:4] + "00000/" + epicID[4:6] + "000/"
    else:
        path = path
    if fn == "DEFAULT":
        fn = "ktwo" + epicID + "-c0" + campaign + "_lpd-lc.fits"
    else:
        fn = fn
    #Construct the dictionary query
	q = dict(
        light_curve_file=path+fn,
        basis_file = "/k2_data/elcs/c" + campaign + ".h5",
        nbasis = 150,
        initial_time = initial_time,
        catalog_file = "/k2_data/catalogs/epic.h5", 
        time_spacing = time_spacing,
        durations = durations,
        min_period = min_period,
        max_period = max_period, 
        npeaks = npeaks,
    )
    return q

def get_query(epicID, campaign):
    '''Format a default query for the ketu pipeline
    key-words:
        epicID---the EPIC designation for your target
        campaign---the K2 campaign of that EPIC designation
    '''
    epicID, campaign = str(epicID), str(campaign)
    #Default path to lightcurve
    path = "/k2_data/lightcurves/" + "c" + campaign + "/" 
    path += epicID[0:4] + "00000/" + epicID[4:6] + "000/" 
    #Construct the dictionary query object
    q = dict(
        light_curve_file = path + "ktwo" + epicID + "-c0" + campaign + "_lpd-lc.fits",
        initial_time=1940.,
        basis_file= "/k2_data/elcs/c1.h5",
        nbasis=150,
        catalog_file= "/k2_data/catalogs/epic.h5",
        time_spacing=0.1,
        durations=[0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        min_period=0.5,
        max_period=70.0,
    )
    if campaign == "0":
        q['basis_file'] = "/k2_data/elcs/c0.h5"
    elif campaign == "2":
        q['basis_file'] = "/k2_data/elcs/c2-norm.h5"
    else:
        q['basis_file'] = "/k2_data/elcs/c?-norm.h5"
    return q

def save_query(query, f):
    '''Saves a query in a pickled format with name f'''
    pickle.dump(query, f)

def analyze(query,cache=False):
    '''Pass a target through the ketu pipeline
    Key Terms:
    query-- a dictionary with query terms from either build_query or get_query
    cache-- if False does not cache, otherwise designate directory to cache at
    Return:
    A pipeline result object for examination
    '''
    if cache == False:
        pipe = ketu.k2.Data(cache=False)
        pipe = ketu.k2.Likelihood(pipe,cache=False)
        pipe = ketu.OneDSearch(pipe,cache=False)
        pipe = ketu.TwoDSearch(pipe,cache=False)
        pipe = ketu.PeakDetect(pipe,cache=False)
    else:#do cache!
        pipe = ketu.k2.Data(basepath=cache)
        pipe = ketu.k2.Likelihood(pipe)
        pipe = ketu.OneDSearch(pipe)
        pipe = ketu.TwoDSearch(pipe)
        pipe = ketu.PeakDetect(pipe)
    #print(query)
    result = pipe.query(**query)
    return result

def retrieve(epicID, campaign, inpath="/k2_data/lightcurves/"):
    '''Provides access to the time and flux data from a light curve given the EPIC ID and campaign'''
    campaign = str(campaign)
    epicID = str(epicID)
    #if it's in the default path
    if inpath == "/k2_data/lightcurves/":
        path = inpath + "c" + campaign + "/" +  epicID[0:4] + "00000/" + epicID[4:6] + "000/" 
    else:#designate the full path
        path = inpath
    #construct the filename
    fn = path + "ktwo" + epicID + "-c0" + campaign + "_lpd-lc.fits"
    f = fits.open(fn)
    aperture = np.argmin(f[2].data['cdpp6'])
    time, flux = f[1].data['time'] + f[1].header['BJDREFI'], f[1].data['flux'][:,aperture]
    quality = f[1].data['quality']
    m = np.isfinite(time) * np.isfinite(flux) * (quality==0)
    return time[m], flux[m]

def edit(mask, epicID, campaign, inpath="/k2_data/lightcurves/", outpath="/k2_data/eb_removed/"):
    '''Allows direct alteration of a lightcurve by applying a mask to a K2 lightcurve'''
    epicID, campaign = str(epicID),str(campaign)
    if inpath == "/k2_data/lightcurves/":
        path = inpath + "c" + campaign + "/" +  epicID[0:4] + "00000/" + epicID[4:6] + "000/" 
    else:
        path = inpath
    fn = "ktwo" + epicID + "-c0" + campaign + "_lpd-lc.fits"
    f = fits.open(path + fn)
    #apply the mask to all the columns
    f[1].data = f[1].data[mask]
    f.writeto(outpath + fn, clobber=True)
    return

def plot_periodogram(result):
    '''Given a peak_detect result object will plot the phic periodgram'''
    #This plots the more reliable phic periodogram as calculated in the full 2-d search
    fig = pl.figure(figsize=(10, 4))
    ax = fig.add_subplot(111)
    parent_response = result.response
    peaks = parent_response['peaks']
    x = parent_response['periods']
    y = parent_response['phic_scale']/100
    m = np.isfinite(y)
    ax.plot(x[m], y[m], "k")
    pl.xticks(np.arange(2,30,2))
    pl.xlim([0,30])
    for i, peak in enumerate(peaks):
        x0, y0 = peak["period"], peak["phic_norm"]/100
        ax.plot(x0, y0, ".r")
        ax.annotate("{0:.2f}".format(x0), xy=(x0, y0), ha="center",fontsize=10,
                    xytext=(10, 5), textcoords="offset points")
    pl.show()
    
def plot_phase(epicID,campaign,period, t0):
    epicID,campaign = str(epicID),str(campaign)
    time, flux = retrieve(epicID,campaign)
    fig = pl.figure(figsize=(5 * 1.61803398875,5))
    pl.title("EPIC " + epicID)
    phase = remEB.find_phase(time, period, t0)
    pl.plot((phase + 0.25) % 1 - 0.25,flux,'k.',ms=10)
    pl.xlabel("Phase")
    pl.ylabel("FM15 Flux")
    pl.show()
    
def plot_lc(epicID, campaign):
    epicID,campaign = str(epicID),str(campaign)
    time, flux = retrieve(epicID,campaign)
    fig = pl.figure(figsize=(5 * 1.61803398875,5))
    pl.title("EPIC " + epicID)
    pl.plot(time,flux,'k.',ms=10)
    pl.xlabel("Time (BJD)")
    pl.ylabel("FM15 Flux")
    pl.show()