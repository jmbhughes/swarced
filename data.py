from astropy.io import fits
import numpy as np
import shutil

def retrieve(epicID, campaign, directory="/k2_data/", tail="", injected=False,fn='',raw=False):
    '''Provides access to the time and flux data from a light curve given the EPIC ID and campaign
    epicID--the K2 object identification number
    campaign--which campaign this object belongs to
    directory--this is the path to where the lightcurves folder is: on linux '/k2_data/'; on macs '/Volumes/k2_data/'
    tail--if any identifiers have been added onto the tail
    injected--if true it also retrieves when the transits were
    fn--if it's anything other than fn it will not look in the normal directory path
    '''
    campaign = str(campaign)
    epicID = str(epicID)
    #if it's in the default path
    if fn == '':
        fn = get_lc_path(epicID, campaign, directory)
    f = fits.open(fn)
    if campaign != "3" and campaign != 3: #assert campaign == 0, 1, or 2
        aperture = np.argmin(f[2].data['cdpp6'])
        time, flux = f[1].data['time'] + f[1].header['BJDREFI'], f[1].data['flux'][:,aperture]
        quality = f[1].data['quality']
        m = np.isfinite(time) * np.isfinite(flux) * (quality==0)
        if injected:
            transits = list(f[3].data['center'] + f[1].header['BJDREFI'])
        f.close()
        if raw==True:
            print np.array(time), np.array(flux)
            return np.array(time), np.array(flux)
        if not injected:
            if raw==True:
                return np.array(time), np.array(flux)
            else:
                return np.array(time[m]), np.array(flux[m])
        else: #was injected
            if raw == True:
                return np.array(time), np.array(flux), transits
            else:
                return time[m], flux[m], transits
    else: #CAMPAIGN 3!
        time, flux = f[1].data['TIME'] + f[1].header['BJDREFI'], f[1].data['PDCSAP_FLUX']
        quality = f[1].data['SAP_QUALITY']
        m = np.isfinite(time) * np.isfinite(flux) * (quality==0)
        time, flux = time[m], flux[m]
        f.close()
        return time, flux
    
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
    path += "ktwo" + epicIDstr + "-c0" + campaignstr + "_lpd-lc" + tail + ".fits"
    if campaign == 3 or campaign == "3":
        def find_c3(epic):
            if os.path.isfile(directory + "c3/k2c3_1/ktwo" + str(epic) + "-c03_llc.fits") == True:
                return directory + "c3/k2c3_1/ktwo" + str(epic) + "-c03_llc.fits"
            elif os.path.isfile(directory + "c3/k2c3_2/ktwo" + str(epic) + "-c03_llc.fits") == True:
                return directory + "c3/k2c3_2/ktwo" + str(epic) + "-c03_llc.fits"
            else: #is in third set os.path.isfile(directory + "c3/k2c3_3/ktwo" + str(epic) + "-c03_llc.fits") == True:
                return directory + "c3/k2c3_3/ktwo" + str(epic) + "-c03_llc.fits"
        path = find_c3(epicID)
    return path

def clip(epicID, campaign, period, center, separation, pwidth, swidth, initial_time, outpath, directory="/k2_data/",fn=''):
    '''Makes a new fits file for a lightcurve with EB eclipses removed
    epicID--the K2 object identification number
    campaign--which campaign this object belongs to
    period--the period of the EB in days
    center--the center of one of the primary eclipses in BJD
    separation--the phase distance between primary and secondary eclipses
    pwidth--how wide the primary eclipses are
    swidth--how wide the secondary eclipses are
    initial_time--if you want to remove data before some time you can clip that too
    outpath--the directory the clipped lightcurve should be stored in
    directory--this is the path to where the lightcurves folder is: on linux '/k2_data/'; on macs '/Volumes/k2_data/'
    fn--if fn is designated it will ignore the normal lightcurves folder and look at that specific file
    '''
    if fn == '':
        fn = get_lc_path(epicID, campaign, directory)
    newfn = outpath + fn.split('/')[-1].split(".")[0] + "_clip.fits"
    shutil.copy(fn, newfn)
    clip_work(newfn, period, center, separation, pwidth, swidth, initial_time)
    
def clip_work(fn, period, center, separation, pwidth, swidth, initial_time):
    '''the main work function for clip, see clip'''
    f = fits.open(fn, mode='update')
    time = f[1].data['time']+f[1].header['BJDREFI']
    phase = find_phase(time, period, center )
    mask = eclipse_mask(phase, period, separation, pwidth, swidth)
    #mask = np.logical_not(eclipse_mask(phase, period, separation, pwidth, swidth))
    mask = mask * (time > initial_time)
    f[1].data['quality'][np.logical_not(mask)]= 16384
    m = (f[1].data['quality'] == 0 )
    f[1].data = f[1].data[m]
    f[1].header['EBPERIOD'] = period
    f[1].header['EBT0'] = center
    f[1].header['EBSEP'] = separation
    f[1].header['EBPWIDTH'] = pwidth
    f[1].header['EBSWIDTH'] = swidth
    f.flush()
    f.close()
    
def clip_by_median(epicID, campaign, period, center, outpath, initial_time, directory="/k2_data/", fn="")
    if fn == '':
            fn = get_lc_path(epicID, campaign, directory)
        newfn = outpath + fn.split('/')[-1].split(".")[0] + "_clip.fits"
        shutil.copy(fn, newfn)
        
def find_phase(time, period, center):
    '''Returns an array of phases corresponding to the input time array
    time--an array of BJD times
    period--the period of the EB (or planet)
    center--the BJD time of the primary eclipse (what you want at phase 0)
    '''
    return (time  - center) % period / period

def eclipse_mask(phase, period, separation, pwidth, swidth,cushion=0.01):
    '''Determines which phase times are not in the eclipse
    phase--an array of phases (can be gotten from find_phase)
    period--the period of the EB in days
    center--the center of one of the primary eclipses in BJD
    separation--the phase distance between primary and secondary eclipses
    pwidth--how wide the primary eclipses are
    swidth--how wide the secondary eclipses are
    cushion--since masking parameters are sometimes not sufficient you can add a small amount to make sure they fully mask the eclipse
    
    returns a Boolean array indicating True where the eclipse is NOT and False for times IN the eclipse
    '''
    phalf, shalf = 0.5*(pwidth + cushion), 0.5*(swidth+cushion)
    mask = (phase > phalf)  * (phase < 1-phalf) * ((phase < separation - shalf) | (phase > separation + shalf))
    return mask
