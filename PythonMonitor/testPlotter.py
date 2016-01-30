from plotter import *
import time
import timeit
import random

plotter = Plotter(1024,"Test");

repeat = 1000
time1 = time.time()
for i in range(0,repeat):
	plotter.plot([random.randint(0,250),random.randint(260,500),random.randint(600,800)],["a","b","c"]);
	
time2 = time.time()
duration = (time2-time1)*1000.0
print '%s replots %0.3f ms %0.3f ms/redraw' % (str(repeat), duration, duration/repeat)

	
#TODO: checkson files and picture	