import os
os.chdir("../")

from PlotFacility.PlotService import *
import time
import random

labels = ["a","b","c","d"]
plotter = PlotService(labels,15005);

keys = [];
delay = 0.1
duration = 60;

def generateKeys(number):
	k = [];
	while number > 0:
		k.append(str(number)+"_test");
		number -= 1;
	return k;

def run_test(k,d,ttr):
	global labels;
	if len(k) == 0:
		return;
	print "Starting plot test..."
	elapsed = 0.0;
	
	while elapsed < ttr:

		data = {}
		tres = 0;
		for l in labels:
			data[l] = random.randint(tres,tres+100);
			tres += 800/len(labels);


		for t in k:
			plotter.update(t,data);
		time.sleep(d);
		elapsed += d;
print "Available commands:exit,set_duration,set_delay,set_parallel,start,s,raw"
while True:
	cmd = raw_input(">");
	cmd = cmd.split(" ");

	if cmd[0] == "exit":
		break;

	if cmd[0] == "set_duration":
		if len(cmd) > 1:
			duration = float(cmd[1]);
		else:
			print "Usage: set_duration number_of_seconds";

	if cmd[0] == "set_delay":
		if len(cmd) > 1:
			delay = float(cmd[1]);
		else:
			print "Usage: set_delay number_of_seconds";

	if cmd[0] == "set_parallel":
		if len(cmd) > 1:
			keys = generateKeys(int(cmd[1]));
			print keys
		else:
			print "Usage: set_parallel nr_of_parallel_plots";

	if cmd[0] == "start":
		if len(keys) == 0:
			keys = generateKeys(1);
		break;

	if cmd[0] == "s":
		if len(cmd) > 2:
			labels = generateKeys(len(cmd) - 2);
			plotter.labels = labels;
			data = {};
			for i in range(0,len(labels)):
				data[labels[i]] = int(cmd[i+2])
			plotter.update(cmd[1],data)
		else:
			print "Usage: s key size size ...";

	if cmd[0] == "raw":
		if len(cmd) > 2 and len(cmd) % 2 == 0:
			data = {}
			for i in range(2,len(cmd)-1):
				data[cmd[i]] = cmd[i+1];

			plotter.update(cmd[1],data)
		else:
			print "Usage: raw key k value";
			
plotter.labels = labels
run_test(keys,delay,duration);
plotter.stop();