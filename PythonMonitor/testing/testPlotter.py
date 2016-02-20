from plotter import *
import time
import timeit
import random

plotter = Plotter(1024,"Test",{"makeLiveDrawing":True});

nrPltLines = input("No. concurrent plots:")
nrResets   = input("No. plotter resets:");

pltData = []
labels = []
for i in range(0,nrPltLines):
	pltData.append(0)
	labels.append(str(i))

repeat = 2000
resetTres = repeat/nrResets

time1 = time.time()
for i in range(0,repeat):
	for j in range(0,nrPltLines):
		pltData[j] = random.randint(j*100+0,j*100+200)
	
	plotter.plot(pltData,labels);
	
	if i > 0 and i % resetTres == 0:
		print "plotter reset"
		plotter.reset("Test"+str(i));

time2 = time.time()
duration = (time2-time1)*(1000.0)
print time2-time1
print '%s replots %0.3f ms %0.3f ms/redraw - %0.3f FPS' % (str(repeat), duration, duration/repeat, 1000.0/(duration/repeat))

plotter.close();	
#TODO: checkson files and picture	 