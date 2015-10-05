import os
import sys

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
os.system("ps -C "+str(program)+" -o pid=,rsz=,vsz= >> /tmp/mem.log");

print "Monitoring complete complete";
