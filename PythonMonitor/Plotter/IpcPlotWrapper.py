from plotter import Plotter
import time
import json
import math
import os
import sys

period = 1
last_measurement = 0;

if len(sys.argv) < 3:
	print "Usage: python IpcPlotWrapper.py namedPipePath Title";
	sys.exit(1);

while True:
	try:
	    comm = open(sys.argv[1], 'r');
	    break;
	except IOError:
		print "Could not open pipe:"+str(IOError);
		time.wait(5);

plotter = Plotter(1024,sys.argv[2]);
data = {};
last = 0
while True:
	cmd = comm.readLine();
	if cmd == "close":
		plotter.close();
		break;

	try:
		data = json.loads(cmd);
		now = time.time()
	except Exception as e:
		print "Json Error:"+str(e);
		continue
	
	try:
		rpt = 1
		if last != 0:
			rpt = math.floor(now - last) + 1
			print rpt;
		#plot the same value multiple times to account for no data received
		while rpt > 0:
			plotter.plot(data["values"],data["labels"]);	
			rpt -= 1;

		last = now;
	except Exception as e:
		print "Plot Error:"+str(e)

comm.close();