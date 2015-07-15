def retrieve(epicID, campaign, inpath="/k2_data/lightcurves/", tail="", injected=False):
    '''Provides access to the time and flux data from a light curve given the EPIC ID and campaign'''
    campaign = str(campaign)
    epicID = str(epicID)
    #if it's in the default path
    if inpath == "/k2_data/lightcurves/":
        path = inpath + "c" + campaign + "/" +  epicID[0:4] + "00000/" + epicID[4:6] + "000/" 
    else:#designate the full path
        path = inpath
    #construct the filename
    fn = path + "ktwo" + epicID + "-c0" + campaign + "_lpd-lc" + tail + ".fits"
    f = fits.open(fn)
    aperture = np.argmin(f[2].data['cdpp6'])
    time, flux = f[1].data['time'] + f[1].header['BJDREFI'], f[1].data['flux'][:,aperture]
    quality = f[1].data['quality']
    m = np.isfinite(time) * np.isfinite(flux) * (quality==0)
    if injected:
        transits = list(f[3].data['center'] + f[1].header['BJDREFI'])
    f.close()
    if not injected:
        return time[m], flux[m]
    else: #was injected
        return time[m], flux[m], transits
    
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
    f.close()
    return

def clean(epicID, campaign, period, center, sep, pwid, swid, inpath="/k2_data/lighcurves",tail=""):
    fn = "ktwo" + epicID + "-c0" + campaign + "_lpd-lc" + tail + ".fits"
    newfn = fn.split(".")[0] + "_clip.fits"
    shutil.copy(inpath + fn, inpath + newfn)
    f = fits.open(inpath + newfn, mode='update')
    phase = remEB.find_phase(f[1].data['time']+f[1].header['BJDREFI'], period, center )
    mask = remEB.clip_eclipses(phase, period, sep, pwid, swid)
    mask = mask * ((f[1].data['time'] +f[1].header['BJDREFI'])> 2.45672e6 + 50)
    f[1].data['quality'][np.logical_not(mask)]= 16384
    m = (f[1].data['quality'] == 0 )
    f[1].data = f[1].data[m]
    f.flush()
    f.close()
    
def find_phase(time, period, center):
    return (time  - center) % period / period

def eclipse_mask(phase, period, sep, pwid, swid):
    ph, sh = 0.5*(pwid + 0.01), 0.5*(swid+0.01)
    mask = (phase > ph)  * (phase < 1-ph) * ((phase < sep - sh) | (phase > sep + sh))
    return mask
