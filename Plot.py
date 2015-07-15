def plot_periodogram(epicID,result,pickled=True):
    '''Given a peak_detect result object will plot the phic periodgram
    epicID--the K2 object ID for the periodogram
    result--if pickled==True the pickled results from JUST the ketu.two_d_search otherwise the full result with all parent info
    pickled--whether or not result is the abbreviated pickled version or the raw version from ketu
    '''
    fig = pl.figure(figsize=(10, 4))
    ax = fig.add_subplot(111)
    if not pickled:
        response = result.response
    else:
        response = result
    peaks = response['peaks']
    x, y = response['periods'],response['phic_scale']
    m = np.isfinite(y)
    ax.plot(x[m], y[m], "k")
    pl.title("EPIC " + str(epic))
    pl.xlabel("Period (Days)")
    pl.ylabel("Strength of response (scaled phic)")
    for i, peak in enumerate(peaks):
        x0, y0 = peak["period"], peak["phic_norm"]
        ax.plot(x0, y0, ".r")
        ax.annotate("{0:.2f}".format(x0), xy=(x0, y0), ha="center",fontsize=10,
                    xytext=(10, 5), textcoords="offset points")
    pl.show()
    
def plot_phase(epicID,campaign,period, t0, inpath ="/k2_data/lightcurves/",tail="",initial_time=0):
    '''Plots a period folded curve'''
    time, flux = retrieve(epicID,campaign,inpath,tail)
    if initial_time != 0:
        time,flux = time[time>initial_time], flux[time>initial_time]
    plot_phase_work(time, period, flux, "EPIC " + str(epicID))
    
def plot_phase_work(time, period, flux, title):
    fig = pl.figure(figsize=(5 * 1.61803398875,5))
    pl.title(title)
    phase = remEB.find_phase(time, period, t0)
    pl.plot((phase + 0.25) % 1 - 0.25,flux,'k.',ms=10)
    pl.xlabel("Phase")
    pl.ylabel("FM15 Flux")
    pl.show()
    
def plot_lc(epicID, campaign, inpath="/k2_data/lightcurves/",mark_list=[],tail="",injected=False,ylimtype="med",xlim=[0,0],initial_time = 0):
    '''Plots the best lightcurve from photometry'''
    epicID,campaign = str(epicID),str(campaign)
    if not injected:
        time, flux = retrieve(epicID,campaign,inpath,tail)
    else:
        time, flux, transits = retrieve(epicID,campaign,inpath,tail,injected=True)
    if initial_time != 0:
        time,flux = time[time>initial_time], flux[time>initial_time]
    fig = pl.figure(figsize=(5 * 1.61803398875,5))
    pl.title("EPIC " + epicID)
    pl.plot(time,flux,'k.',ms=10)
    pl.xlabel("Time (BJD)")
    pl.ylabel("FM15 Flux")
    pl.plot(mark_list, np.median(flux) + np.zeros(len(mark_list)),'r*',markersize=20)
    if injected:
        pl.plot(transits, np.median(flux) + np.zeros(len(transits)),'r*',markersize=20)
    if xlim != [0,0]:
        pl.xlim(xlim)
        flux = flux[((time>xlim[0])*(time<xlim[1]))]
    else:
        xlim = [min(time),max(time)]
        flux = flux[((time>xlim[0])*(time<xlim[1]))]
    if ylimtype=="med":
           pl.ylim(np.median(flux)-0.5*np.std(flux),np.median(flux)+0.5*np.std(flux))
    elif ylimtype=="minmax":
           pl.ylim(np.min(flux),np.max(flux))
    elif ylimtype=="pick":
        pl.ylim(min([np.min(flux),np.median(flux)-0.5*np.std(flux)]), 
                max([np.max(flux),np.median(flux)+0.5*np.std(flux)]))

    pl.show()
    del mark_list
    #return fig
