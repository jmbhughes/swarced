import numpy as np
import matplotlib.pyplot as pl
import sys, os, pickle, copy
#sys.path.append("/Users/nbanale1-temp/Desktop/swarced")
sys.path.append("../")
import swarced as sw
from matplotlib.widgets import Button, RadioButtons

if sys.argv[1] == 'help':
    print("script, blsreportpath, limitsreportpath, directory = sys.argv")
script, blsreportpath, limitsreportpath, directory = sys.argv
#GLOBAL VARIABLES:
CAMPAIGN, INITIAL_TIME = "1", sw.C1INITIALTIME

blsreport = pickle.load(open(blsreportpath,'r'))
blsepic = np.array(blsreport[:,0],dtype=np.int)
blsperiod = blsreport[:,1]
#blsepic = np.array([int(f[0]) for f in blsreport])
#blsperiod = np.array([f[1][0] for f in blsreport])

running=True
try:
    with open(limitsreportpath,"r") as f:
        #print("loaded " + limitsreportpath)
        limitsreport = pickle.load(f)
        if len(limitsreport) ==0:
            limitsepic = []
        else:
            limitsepic = [int(l[0]) for l in limitsreport]
except:
    limitsreport=[]
    limitsepic = []

#print blsepic
#print limitsepic
ls = blsepic
ls = np.array([epic for epic in ls if epic not in limitsepic])
class Select:
        def isUnusable(self,event):
            global limitsreport, mode, bbls2, bbls, bunusable, bnoteb, bwrongp
            mode = "unusable_clipping"
            bunusable.color='red'
            bnoteb.color='grey'
            bwrongp.color='grey'
            sketch(mode)
        def isWrongPeriod(self,event):
            global limitsreport, mode, bbls2, bbls, bunusable, bnoteb, bwrongp
            mode = "wrong_period"
            bunusable.color='grey'
            bnoteb.color='grey'
            bwrongp.color='red'
            sketch(mode)
        def isNotEB(self, event):
            global limitsreport, mode, bbls2, bbls, bunusable, bnoteb, bwrongp
            mode = "not_an_eb"
            bunusable.color='grey'
            bnoteb.color='red'
            bwrongp.color='grey'
            sketch(mode)
        def submit(self,event):
            global limitsreport, limits, epicID, period, mode, multiple, loc
            x = limits_to_params(epicID, CAMPAIGN, multiple*blsperiod[loc], mode, limits)
            print x
            limitsreport.append(x)
            pickle.dump(limitsreport, open(limitsreportpath,'wb'))
            pl.close()
        def undo(self,event):
            global limits, mode
            #mode = "undecided"
            if len(limits) > 0:
                limits = limits[:len(limits)-1]
            print limits
            sketch(mode)
        def exit(self,event):
            global running
            running=False
            pl.close('all')
        def increase(self, event):
            global axs, multiple, limits, phase
            limits = []
            multiple += 0.5
            phase = sw.data.find_phase(time,multiple*blsperiod[loc], 0)
            sketch(mode)
            #axs[1].cla()
            #axs[1].plot(phase,flux,'k.',picker=5)
            #axs[0].set_title("EPIC {0:9.0f}: period of {1:6.3f} days".format( epicID, multiple * blsperiod[loc]))
        def decrease(self, event):
            global axs, multiple, limits, phase
            limits=[]
            if multiple - 0.5 > 0:
                multiple -= 0.5
                print(multiple)
                phase = sw.data.find_phase(time,multiple*blsperiod[loc], 0)
                sketch(mode)
            #axs[1].cla()
            #axs[1].plot(phase,flux,'k.',picker=5)
            #axs[0].set_title("EPIC {0:9.0f}: period of {1:6.3f} days".format( epicID, multiple * blsperiod[loc]))
            
def limits_to_params(epicid, campaign, period, mode, limits):
    while len(limits)!= 4:
        limits += [-1]
    pleft, pright, sleft, sright = limits
    pwidth = (pright - pleft)%1
    swidth = (sright - sleft)%1
    if sleft != -1:
        sep = (sleft - pright)%1 + pwidth #the mod accounts the possibility that the secondary is before the primary
    else:
        sep = 0
    t0 = time[np.argmin(abs(phase - (pwidth/2 + pleft)))] #phase of center of primary
    return epicid, pwidth, swidth, period, sep, t0, mode

for i,epicID in enumerate(ls):
    if running:
        print(str(i) + " of " + str(len(ls)))
        limits, mode, multiple = [], "undecided", 1
        fig, axs = pl.subplots(2,1)
        time, flux = sw.data.retrieve(str(epicID),CAMPAIGN,fn=sw.data.get_lc_path(epicID,CAMPAIGN,directory))
        loc = np.argmax(blsepic == int(epicID))
        phase, mask = sw.data.find_phase(time,blsperiod[loc], 0), time>INITIAL_TIME
        time, flux, phase = time[mask], flux[mask], phase[mask]
        
        axs[0].set_title("EPIC {0:9.0f}: period of {1:6.3f} days".format( epicID, blsperiod[loc]))
        axs[0].set_label("Time")
        #axs[1].set_xticks([])
        axs[1].set_ylabel("FM15 Flux")
        axs[0].plot(time, flux, 'k.',picker=5)
        axs[1].plot(phase,flux,'k.',picker=5)
        pl.subplots_adjust(bottom=0.2)

        def limits2save(condition,epicID):
            global limits
            if len(limits)!=4:
            	while len(limits)!=4:
                	limits += [-1]
                limits += [condition]
                return [epicID]+ limits
            else:
                limits += [condition]
                return [epicID] + limits
        def limitsutility():
            global limits
            ll = copy.copy(limits)
            while len(ll) != 4:
                ll += [-1]
            return ll
        
        def sketch(mode):
            axs[1].cla()
            axs[1].plot(phase,flux,'k.',picker=5)
            axs[0].set_title("EPIC {0:9.0f}: period of {1:6.3f} days".format( epicID, multiple * blsperiod[loc]))
            axs[0].set_xlabel("Time")
            axs[1].set_xlabel("Phase")
            axs[1].set_ylabel("FM15 Flux")
            axs[0].set_ylabel("FM15 Flux")
            if len(limits) >=2:

                if limits[0] < limits[1]:
                    mask = (phase > limits[0]) * (phase < limits[1])
                else:
                    mask = ((phase > limits[0]) * (phase < 1)) | ((phase < limits[1]) * (phase > 0))
                axs[1].plot(phase[mask], flux[mask], 'r.')
            if len(limits) == 4:
                if limits[2] < limits[3]:
                    mask = (phase > limits[2]) * (phase < limits[3])
                else:
                    mask = ((phase > limits[2]) * (phase < 1)) | ((phase < limits[3]) * (phase > 0))
                axs[1].plot(phase[mask], flux[mask], 'g.')
            pl.draw()
            #print mode

        def onpick(event):
            global limits
            thisline, ind = event.artist, event.ind
            xdata = thisline.get_xdata()       
            if len(limits) < 4:
                limits += [xdata[ind][0]]
            sketch(mode)
            print limits
            #ll = limitsutility()
            #print clicks_to_params(epicID, CAMPAIGN, blsperiod[loc]*multiple, 1, ll[0], ll[1], sleft=ll[2], sright=ll[3])

        fig.canvas.mpl_connect('pick_event', onpick)
        callback = Select()
        
        axincrease = pl.axes([0.7-6*0.11,0.05,0.1,0.075])
        bincrease = Button(axincrease,'Increase',color='white')
        bincrease.on_clicked(callback.increase)

        axdecrease = pl.axes([0.7-5*0.11,0.05,0.1,0.075])
        bdecrease = Button(axdecrease,'Decrease',color='white')
        bdecrease.on_clicked(callback.decrease)
        
        #axunusable = pl.axes([0.7-4*0.11,0.05,0.1,0.075])
        #bunusable = Button(axunusable, 'Unusable \n Clipping')
        #bunusable.on_clicked(callback.isUnusable)

        #axnoteb = pl.axes([0.7-3*0.11,0.05,0.1,0.075])
        #bnoteb = Button(axnoteb, 'Not an EB')
        #bnoteb.on_clicked(callback.isNotEB)
        
        #axwrongp = pl.axes([0.7-2*0.11,0.05,0.1,0.075])
        #bwrongp = Button(axwrongp, 'Wrong \n Period')
        #bwrongp.on_clicked(callback.isWrongPeriod)

        axsubmit = pl.axes([0.7-1*0.11,0.05,0.1,0.075])
        bsubmit = Button(axsubmit, 'Submit',color='white')
        bsubmit.on_clicked(callback.submit)

        axundo = pl.axes([0.7-0*0.11,0.05,0.1,0.075],axisbg='white')
        bundo = Button(axundo, 'Undo',color='white')
        bundo.on_clicked(callback.undo)

        axexit = pl.axes([0.7-(-1)*0.11,0.05,0.1,0.075])
        bexit = Button(axexit, 'Exit',color='white')
        bexit.on_clicked(callback.exit)

        axcolor = 'lightgoldenrodyellow'
        rax = pl.axes([0.7-4*0.11,0,0.2,0.2])
        #x0, y0 = rax.transAxes.transform((0, 0)) # lower left in pixels
        #x1, y1 = rax.transAxes.transform((1, 1)) # upper right in pixes
        #dx = x1 - x0
        #dy = y1 - y0
        #maxd = max(dx, dy)
        #width = .15 * maxd / dx
        #height = .15 * maxd / dy
        #rax.axis(aspect = 'equal')
        #rax.set_aspect(1)
        #rax.add_artist(Circle((.5, .5), .15))
        
        def resize_buttons(r, f):
            "Resize all radio buttons in `r` collection by fractions `f`"
            [c.set_radius(0.15) for c in r.circles]
            
        radio3 = RadioButtons(rax, ("EB", 'EB but check', 'Not an EB', 'Sinusoidal','Periodic','Odd'))
        #resize_buttons(radio3,5)
        def modefunc(label):
            global mode
            mode = label
            sketch(mode)
            #print  mode
        radio3.on_clicked(modefunc)
        mode = "EB"

        pl.show()
        

