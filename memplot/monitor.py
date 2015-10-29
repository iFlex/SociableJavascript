import os
import sys
import threading
import time;
import plotter;
import subprocess;
#matplotlib
def collect_results(path,duration,alias):
	os.system("mv ./out/mem-graph.png "+path+"/"+alias+".png");

def strip(s):
	idof = s.find("./")

	if idof > -1:
		s = s[idof+2:];

	return s;

plt = 0
keepMonitoring = True
def memwatch(program,resolution):
	program = strip(program);
	global keepMonitoring,plt;
	#os.system("rm /tmp/mem.log");

	if plt == 0:
		plt = plotter.Plotter(1);

	while keepMonitoring:
		result = subprocess.check_output("ps -C "+str(program)+" -o pid=,rsz=,vsz=", shell=True)
		result = result.split(" ");
		#print result
		plt.plot(str(result[1]));
		os.system("sleep "+str(resolution));
	plt.save("out.png");


def monitor_program(program,script,alias,resolution,collection_path):
	global keepMonitoring;

	keepMonitoring = True
	monThread = threading.Thread(target=memwatch,args=(program,resolution,));
	monThread.start();

	start_time = time.clock();
	result = os.system(program+" "+script);
	end_time = time.clock();

	keepMonitoring = False;
	monThread.join();
	print "Process has finished running, collecting results"
	alias = str(resolution)+"_"+alias
	collect_results(collection_path,end_time-start_time,alias);
	print result;
