import os
import sys
import threading
import time;
import datetime

def collect_results(duration):
	if os.path.isdir("measurements") == False :
		os.system("mkdir measurements");
	d = datetime.datetime.now();
	out_dir = d.strftime("%d_%m_%Y_%H.%M.%S");
	print "new measurement:"+out_dir;
	os.system("mkdir measurements/"+out_dir);
	os.system("mv ./out/mem-graph.png measurements/"+out_dir);		

keepMonitoring = True
def memwatch(program):
	global keepMonitoring;
	os.system("rm /tmp/mem.log");
	while keepMonitoring:
		os.system("ps -C "+str(program)+" -o pid=,rsz=,vsz= >> /tmp/mem.log");
		os.system("gnuplot ./plot.gnuplot");
		os.system("sleep 1");
	
def monitor_program(program,params):
	global keepMonitoring;
	monThread = threading.Thread(target=memwatch,args=(program,));
	monThread.start();
	
	start_time = time.clock();
	result = os.system(program+" "+" ".join(params));
	end_time = time.clock();	
	
	keepMonitoring = False;
	monThread.join();	
	print "Process has finished running, collecting results"
	collect_results(end_time-start_time);	
	print result;

print sys.argv[0];

program = "firefox"
output  = program+"_memuse.png"
outPath = "out/"

if len(sys.argv) == 1:
	program = raw_input("Program to monitor:")
else:
	program  = sys.argv[1]
	if len(sys.argv) > 2 :	
		output   = sys.argv[2]
	if len(sys.argv) > 3 :
		outPath  = sys.argv[3]

print "Monitoring "+str(program)+" with output at:"+str(outPath)+str(output)
#run command, run plot, measure time and decide if new plot page is required, if process died, stop measuring
monitor_program(program,["~/level4/SociableJavascript/v8runner/test/benchmark.js"]);
print "Monitoring complete";

