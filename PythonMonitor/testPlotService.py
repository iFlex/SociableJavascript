from PlotService import *
import time
import random

labels = ["heap","line","3rd"]
plotter = PlotService(labels);
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
			plotter.update(t,{"values":[random.randint(100,200),random.randint(0,50),random.randint(50,100)],"labels":labels});
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
		if len(cmd) > 2:
			plotter.update(cmd[1],{"heap":int(cmd[2])})
		else:
			print "Usage: s key size";

	if cmd[0] == "raw":
		if len(cmd) > 2 and len(cmd) % 2 == 0:
			data = {}
			for i in range(2,len(cmd)-1):
				data[cmd[i]] = cmd[i+1];

			plotter.update(cmd[1],data)
		else:
			print "Usage: r key k value";

run_test(keys,delay,duration);
plotter.stop();