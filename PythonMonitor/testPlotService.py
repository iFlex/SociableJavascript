from PlotService import *
import time
import random

plotter = PlotService(["heap"]);
plotter.init();

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
	if len(k) == 0:
		return;

	elapsed = 0.0;
	while elapsed < ttr:
		for t in k:
			plotter.plot(t,{"heap":random.randint(0,200)});
		time.sleep(d);
		elapsed += d;

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
		else:
			print "Usage: set_parallel nr_of_parallel_plots";

	if cmd[0] == "start":
		break;

	if cmd[0] == "s":
		if len(cmd) > 3:
			plotter.plot(cmd[1],{"heap":int(cmd[2])})
		else:
			print "Usage: r key size";

run_test(keys,delay,60);
plotter.stop();