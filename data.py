def retrieve(epicID, campaign, directory="/k2_data/", tail="", injected=False,fn=''):
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
        get_lc_path(epicID, campaign, directory)
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
    clip_work(newfn, period, center, separation, pwdith, swidth, initial_time)
    
def clip_work(fn, period, center, separation, pwidth, swidth, initial_time):
    '''the main work function for clip, see clip'''
    f = fits.open(fn, mode='update')
    time = f[1].data['time']+f[1].header['BJDREFI']
    phase = find_phase(time, period, center )
    mask = eclipse_mask(phase, period, sep, pwid, swid)
    mask = mask * (time > initial_time)
    f[1].data['quality'][np.logical_not(mask)]= 16384
    m = (f[1].data['quality'] == 0 )
    f[1].data = f[1].data[m]
    f.flush()
    f.close()
    
def find_phase(time, period, center):
    '''Returns an array of phases corresponding to the input time array
    time--an array of BJD times
    period--the period of the EB (or planet)
    center--the BJD time of the primary eclipse (what you want at phase 0)
    '''
    return (time  - center) % period / period

def eclipse_mask(phase, period, separation, pwidth, swidth,cushion=0.01):
    '''Determines which phase times are in the eclipse
    phase--an array of phases (can be gotten from find_phase)
    period--the period of the EB in days
    center--the center of one of the primary eclipses in BJD
    separation--the phase distance between primary and secondary eclipses
    pwidth--how wide the primary eclipses are
    swidth--how wide the secondary eclipses are
    cushion--since masking parameters are sometimes not sufficient you can add a small amount to make sure they fully mask the eclipse
    '''
    phalf, shalf = 0.5*(pwidth + cushion), 0.5*(swidth+cushion)
    mask = (phase > phalf)  * (phase < 1-phalf) * ((phase < separation - shalf) | (phase > separation + shalf))
    return mask
