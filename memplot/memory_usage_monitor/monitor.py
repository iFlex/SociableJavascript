import os
import sys
import json
import math
import subprocess
import staticPlot
import plotter;
import threading
from datetime import datetime


def strip(s):
    idof = s.rfind("/")
    if idof > -1:
	       s = s[idof+1:];

    return s;

plt = 0
keepMonitoring = True
def memwatch(program,resolution,alias):
    program = strip(program);
    global keepMonitoring,plt;
    #os.system("rm /tmp/mem.log");

    if plt == 0:
    	plt = plotter.Plotter(1);

    while keepMonitoring:
    	result = subprocess.check_output("ps -C "+str(program)+" -o rsz=", shell=True)
    	result = result.split(" ");
    	#print result
    	plt.plot(str(result[0]));
    	os.system("sleep "+str(resolution));

    plt.save("measurements/"+alias+".png");

def monitor_program(program,script,alias,resolution):
    global keepMonitoring,plt;
    keepMonitoring = True

    alias = str(resolution)+"_"+alias
    monThread = threading.Thread(target=memwatch,args=(program,resolution,alias,));
    monThread.start();

	#start_time = time.clock();
    result = os.system(program+" 1024 "+script);
	#end_time = time.clock();

    keepMonitoring = False;
    monThread.join();
    print "Process has finished running, collecting results"

#read config file and start measuring
#read config file and start measuring
cfgfile = raw_input("cfg file:");
if len(cfgfile) == 0:
    cfgfile = "config.json"

content = "";
with open(cfgfile, 'r') as content_file:
	content = content_file.read()
cfg = json.loads(content);

results = []
for test in cfg["tests"]:
    try:
        #add in the abs location of the scripts
        for i in range(0,len(test["script"])):
            test["script"][i] = cfg["location"] + test["script"][i];
        #execute test pack
        monitor_program(cfg["location"]+cfg["binary"],(" ").join(test["script"]),test["alias"],test["resolution"]);

    except Exception as e:
        print "### Failed to process test"
        print test
        print "###:"+str(e)

print "### DONE ###"
