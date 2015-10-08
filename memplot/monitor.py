import os
import sys
import threading

keepMonitoring = True
def monitor(program):
	global keepMonitoring;
	os.system("rm /tmp/mem.log");
	while keepMonitoring:
		os.system("ps -C "+str(program)+" -o pid=,rsz=,vsz= >> /tmp/mem.log");
		os.system("gnuplot ./plot.gnuplot");
		#os.system("sleep 1");
	
def run_program(program,params):
	global keepMonitoring;
	monThread = threading.Thread(target=monitor,args=(program,));
	monThread.start();
	result = os.system("time "+program+" "+" ".join(params));
	keepMonitoring = False;
	monThread.join();	
	print "Process has finished running"	
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
run_program(program,["../v8runner/test/benchmark.js"]);
print "Monitoring complete complete";
