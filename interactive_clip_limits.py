import numpy as np
import matplotlib.pyplot as pl
import sys, os, pickle
sys.path.append("/Users/nbanale1-temp/Desktop/swarced")
import swarced as sw
import remove_EB as remEB
from matplotlib.widgets import Button
directory = "/k2_data/c0eblimits/"
#directory = "/Volumes/k2_data/c0eblimits/"
ls = os.listdir(directory)
ls = [int(l[4:13]) for l in ls if ".fits" in l]
blsreport = pickle.load(open(directory + "blsreport.pkl",'r'))
blsepic = np.array([int(f[0]) for f in blsreport])
blsperiod = np.array([f[1][1] for f in blsreport])
print(type(blsepic))
#check if all ls have blsreport entries
ls = np.array([epic for epic in ls if epic in blsepic])

#limitsreport = np.array([])
#limitsepic = np.array([])
with open(directory + "limitsreport.pkl","r") as f:
    limitsreport = pickle.load(f)
    if len(limitsreport) ==0:
        limitsepic = []
    else:
        limitsepic = [int(l[0]) for l in limitsreport]
        #limitsepic = limitsreport[:,0]
#limitsreport = pickle.load(open(directory + "limitsreport.pkl",'r'))
#limitsepic = limitsreport[:,0]

ls = np.array([epic for epic in ls if epic not in limitsepic])

for epicID in ls:
    epicID, campaign, initial_time = str(epicID), "0", 2.45672e6+50
    #epicID,campaign,initial_time = "205050711","2", 2.45689e6+10
    fig, axs = pl.subplots(3,1)
    time, flux = sw.retrieve(epicID,campaign,inpath=directory)
    axs[0].set_title("EPIC " + epicID)
    axs[0].set_label("Time")
    axs[1].set_xticks([])
    axs[1].set_ylabel("FM15 Flux")
    axs[2].set_xlabel("Phase")

    #print(blsepic)
    #print(epicID in blsepic)
    #print(blsepic == epicID)
    loc = np.argmax(blsepic == int(epicID))
    #print(loc)
    #print(blsperiod[loc])
    phase = remEB.find_phase(time,blsperiod[loc], 0)
    phase2 =  remEB.find_phase(time,blsperiod[loc]*2, 0)
    mask = time>initial_time
    #print(time, "joe",time[mask])
    time, flux = time[mask], flux[mask]
    phase, phase2 = phase[mask],phase2[mask]

    axs[0].plot(time, flux, 'k.',picker=5)
    axs[1].plot(phase,flux,'k.',picker=5)
    axs[2].plot(phase2,flux,'k.',picker=5)

    pl.subplots_adjust(bottom=0.2)	
  
    def limits2save(condition,epicID):
        global limits
        if len(limits)==2:
            limits += [-1]
            limits += [-1]
            limits += [condition]
            return [epicID]+ limits
        else:
            limits += [condition]
            return [epicID] + limits
        
    def sketch(mode):
        axs[0].plot(time, flux, 'k.',picker=5)
        axs[1].plot(phase,flux,'k.',picker=5)
        axs[2].plot(phase2,flux,'k.',picker=5)
        if mode == 1:
            mask = (phase > 2* limits[0]) * (phase < 2* limits[1])
            axs[1].plot(phase[mask], flux[mask], 'o', c='red')
            axs[2].plot(phase2[mask], flux[mask], 'o', c='red')
            mask = (phase > 2* limits[2]) * (phase < 2* limits[3])
            axs[1].plot(phase[mask], flux[mask], 'o', c='green')
            axs[2].plot(phase2[mask], flux[mask], 'o', c='green')
        if mode == 2:
            mask = (phase2 > limits[0]) * (phase2 < limits[1])
            axs[1].plot(phase[mask], flux[mask], 'o', c='red')
            axs[2].plot(phase2[mask], flux[mask], 'o', c='red')
            mask = (phase2 > limits[2]) * (phase2 < limits[3])
            axs[1].plot(phase[mask], flux[mask], 'o', c='green')
            axs[2].plot(phase2[mask], flux[mask], 'o', c='green')
        pl.draw()
    	
    class Select:
        def isBLS(self,event):
            global limitsreport, mode, limits
            mode = 1
            sketch(mode)
            #limitsreport = np.append(limitsreport, limits2save(1))
            #limits = []
            #pickle.dump(limitsreport, open(directory + "temp.pkl",'wb'))
            #pl.close()
        def isBLS2(self,event):
            global limitsreport, mode
            mode = 2
            sketch(mode)
            #limitsreport = np.append(limitsreport, limits2save(2))
            #limits = []
            #pickle.dump(limitsreport, open(directory + "temp.pkl",'wb'))
            #pl.clf()
        def nobls(self,event):
            global limitsreport, mode
            mode = 0
            sketch(mode)
            #limitsreport = np.append(limitsreport, limits2save(0))
            #limits = []
            #pickle.dump(limitsreport, open(directory + "temp.pkl",'wb'))
            #pl.clf()
        def submit(self,event):
            global limitsreport
            limitsreport.append(limits2save(mode,epicID))
            pickle.dump(limitsreport, open(directory + "limitsreport.pkl",'wb'))
            pl.close()
        def undo(self,event):
            global limits, mode
            limits = limits[:-1]
            print limits
            sketch(mode)
        def exit(self,event):
            pickle.dump(limitsreport, open(directory + "limitsreport.pkl",'wb'))
            #break
            #pl.close()
            
      
    #def noSecondary(self, event):
    #  print("no secondary")

    limits = []
    def onpick(event):
        global limits
        thisline = event.artist
        xdata = thisline.get_xdata()
        ydata = thisline.get_ydata()        
        ind = event.ind
      
        if len(limits) == 1:
            mask = (phase2 > limits[0]) * (phase2 < xdata[ind][0])
            axs[1].plot(phase[mask], flux[mask], 'o', c='red')
            axs[2].plot(phase2[mask], flux[mask], 'o', c='red')
        if len(limits) == 3:
            mask = (phase2 > limits[2]) * (phase2 < xdata[ind][0])
            axs[1].plot(phase[mask], flux[mask], 'o', c='green')
            axs[2].plot(phase2[mask], flux[mask], 'o', c='green')

        pl.draw()
        limits += [xdata[ind][0]]

    fig.canvas.mpl_connect('pick_event', onpick)
    callback = Select()
    axbls = pl.axes([0.7-5*0.11,0.05,0.1,0.075])
    bbls = Button(axbls, '1 * BLS \n Period')
    bbls.on_clicked(callback.isBLS)

    axbls2 = pl.axes([0.7-4*0.11,0.05,0.1,0.075])
    bbls2 = Button(axbls2, '2 * BLS \n Period')
    bbls2.on_clicked(callback.isBLS2)

    #axnosecond = pl.axes([0.7-1*0.11,0.05,0.1,0.075])
    #bnosecond = Button(axnosecond, 'No \n Secondary')
    #bnosecond.on_clicked(callback.noSecondary)

    axnobls = pl.axes([0.7-3*0.11,0.05,0.1,0.075])
    bnobls = Button(axnobls, 'False \n Detection')
    bnobls.on_clicked(callback.nobls)

    axsubmit = pl.axes([0.7-2*0.11,0.05,0.1,0.075])
    bsubmit = Button(axsubmit, 'Submit')
    bsubmit.on_clicked(callback.submit)

    #axundo = pl.axes([0.7-1*0.11,0.05,0.1,0.075])
    #bundo = Button(axundo, 'Undo')
    #bundo.on_clicked(callback.undo)
    
    #axexit = pl.axes([0.7+0.11,0.05,0.1, 0.075])
    #bexit = Button(axexit, 'Save')
    #bexit.on_clicked(callback.exit)

    pl.show()
