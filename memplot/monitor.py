import os
import sys
import threading
import time;
#matplotlib
def collect_results(path,duration,alias):
	os.system("mv ./out/mem-graph.png "+path+"/"+alias+".png");

keepMonitoring = True
def memwatch(program,resolution):
	global keepMonitoring;
	os.system("rm /tmp/mem.log");
	while keepMonitoring:
		os.system("ps -C "+str(program)+" -o pid=,rsz=,vsz= >> /tmp/mem.log");
		os.system("gnuplot ./plot.gnuplot");
		os.system("sleep "+str(resolution));

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
