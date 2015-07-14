import numpy as np
import matplotlib.pyplot as plt
import sys

sys.path.append("/home/mhughes/Desktop/swarced/")

import swarced as sw
import remove_EB as remEB

fig = plt.figure()
ax = fig.add_subplot(111)
#ax.set_title('click on points')

'''Plots the best lightcurve from photometry'''
epicID,campaign = "202060506","0"
time, flux = sw.retrieve(202060506,0,inpath="/home/mhughes/Desktop/swarced/lcs/")
#ax.figure(figsize=(5 * 1.61803398875,5))
plt.title("EPIC " + epicID)
phase = remEB.find_phase(time, 1.9597767, 56775.796171+2400000)
#ax.plot(phase, flux, 'k.', ms=10,picker=5)
ax.plot((phase + 0.25) % 1 - 0.25,flux,'k.',ms=10,picker=5)
plt.xlabel("Phase")
plt.ylabel("FM15 Flux")

clickcount = 1
lastclick = 0
def onpick(event):
    global clickcount,lastclick
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()	
    ind = event.ind
    #print('onpick points:', zip(xdata[ind], ydata[ind]))
    #print(xdata[ind],ydata[ind])
    if clickcount == 1:
     # ax.plot(phase[phase<xdata[ind][0]],flux[phase<xdata[ind][0]],'o',c='red')
      lastclick = xdata[ind][0]
    if clickcount == 2:
      print(lastclick)
      mask = (phase < xdata[ind][0])
      ax.plot(phase[mask], flux[mask], 'o', c='red')
      mask = (phase > 1 + lastclick)
      ax.plot(phase[mask]-1, flux[mask], 'o', c='red')
      print(phase[mask])
      #ax.plot(phase[phase>xdata[ind][0]],flux[phase>xdata[ind][0]],'o',c='red')
    plt.draw()
    clickcount+=1

def clicktophase(click):
  click + 0.25

fig.canvas.mpl_connect('pick_event', onpick)

plt.show()
