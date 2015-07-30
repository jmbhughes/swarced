import data
import matplotlib.pyplot as pl
import numpy as np
import matplotlib as mpl
mpl.rcParams['lines.linewidth'] = 2
mpl.rcParams['xtick.labelsize'] = 20
mpl.rcParams['ytick.labelsize'] = 20
golden = 1.61803398875

title_font = {'fontname':'Arial', 'size':'36', 'color':'black', 'weight':'normal',
              'verticalalignment':'bottom'} # Bottom vertical alignment for more space
axis_font = {'fontname':'Arial', 'size':'30'}

def periodogram(epicID, result, pickled=True,ylim=(0,0)):
    plot_periodogram(epicID, result, pickled=pickled,ylim=ylim)
    
def plot_periodogram(epicID,result,pickled=True,ylim=(0,0)):
    '''Given a peak_detect result object will plot the phic periodgram
    epicID--the K2 object ID for the periodogram
    result--if pickled==True the pickled results from JUST the ketu.two_d_search otherwise the full result with all parent info
    pickled--whether or not result is the abbreviated pickled version or the raw version from ketu
    '''
    fig = pl.figure(figsize=(10*golden, 10))
    ax = fig.add_subplot(111)
    if not pickled:
        response = result.response
    else:
        response = result
    peaks = response['peaks']
    x, y = response['periods'],response['phic_scale']
    m = np.isfinite(y)
    ax.plot(x[m], y[m], 'darkslategrey')
    pl.title("EPIC " + str(epicID), **title_font)
    pl.xlabel("Period (Days)", **axis_font)
    pl.ylabel("Strength of response (scaled phic)", **axis_font)
    if ylim != (0,0):
        pl.ylim(ylim[0],ylim[1])
    for i, peak in enumerate(peaks):
        x0, y0 = peak["period"], peak["phic_norm"]
        ax.plot(x0, y0, ".r")
        ax.annotate("{0:.2f}".format(x0), xy=(x0, y0), ha="center",fontsize=10,
                    xytext=(10, 5), textcoords="offset points")
    pl.show()

def phase(epicID,campaign,period, t0, directory="/k2_data/",tail="",initial_time=0,fn='',save_path = ''):
    plot_phase(epicID,campaign,period, t0, directory=directory,tail=tail,initial_time=initial_time,fn=fn, save_path=save_path)
    
def plot_phase(epicID,campaign,period, t0, directory ="/k2_data/",tail="",initial_time=0,fn='',raw=False, save_path=''):
    '''Plots a period folded curve'''
    time, flux = data.retrieve(epicID,campaign,directory,tail,fn=fn,raw=raw)
    if initial_time != 0:
        time,flux = time[time>initial_time], flux[time>initial_time]
    plot_phase_work(time, period, t0, flux, "EPIC " + str(epicID) + ":period={0:.3f}, t0={1:.6f}".format(period,t0),save_path=save_path)
    
def plot_phase_work(time, period, center, flux, title,save_path=''):
    fig = pl.figure(figsize=(10* golden,10))
    pl.title(title, **title_font)
    phase = data.find_phase(time, period, center)
    pl.scatter((phase + 0.25) % 1 - 0.25,flux,c='darkslategrey',lw=0,s=30)
    #pl.plot((phase + 0.25) % 1 - 0.25,flux,'k')
    pl.xlabel("Phase", **axis_font)
    pl.ylabel("Flux", **axis_font)
    if save_path == '':
        pl.show()
    else:
        pl.savefig(save_path)
        pl.close()
    
def lightcurve(epicID, campaign, directory="/k2_data/",mark_list=[],tail="",injected=False,ylimtype="minmax",xlim=[0,0],initial_time = 0,fn='',raw=False, save_path =''):
    plot_lc(epicID, campaign,
            directory=directory,mark_list=mark_list,tail=tail,
            injected=injected,ylimtype=ylimtype,xlim=xlim,initial_time = initial_time,
            fn=fn,raw=raw, save_path=save_path)

def plot_lc(epicID, campaign, directory="/k2_data/",mark_list=[],tail="",injected=False,ylimtype="med",xlim=[0,0],initial_time = 0,fn='',raw=False,save_path=''):
    '''Plots the best lightcurve from photometry'''
    epicID,campaign = str(epicID),str(campaign)
    if not injected:
        time, flux = data.retrieve(epicID,campaign,directory,tail,fn=fn,raw=raw)
    else:
        time, flux, transits = data.retrieve(epicID,campaign,directory,tail,injected=True,fn=fn,raw=raw)
    if initial_time != 0:
        time,flux = time[time>initial_time], flux[time>initial_time]
    fig = pl.figure(figsize=(10 * golden,10))
    pl.title("EPIC " + epicID, **title_font)
    print(time)
    print(flux)
    pl.plot(time,flux,'k',lw=0.3)####################
    pl.scatter(time,flux,c='darkslategrey',lw=0,s=30)#######################
    pl.xlabel("Time (BJD)", **axis_font)
    pl.ylabel("Flux", **axis_font)
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
           pl.ylim(np.min(flux)-500,np.max(flux)+500)
    elif ylimtype=="pick":
        pl.ylim(min([np.min(flux),np.median(flux)-0.5*np.std(flux)]), 
                max([np.max(flux),np.median(flux)+0.5*np.std(flux)]))
    if save_path == '':
        pl.show()
    else:
        pl.savefig(save_path)
        pl.close()
    del mark_list
    #return fig
