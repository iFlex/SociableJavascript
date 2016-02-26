#!/bin/src/python
from Management.Communication.server import *
from Management.monitor import *
from Management.policy import *
from PlotFacility.PlotService import *
import time
import subprocess
import sys

print "V8 Manager CLI"

confFile = "default.txt"
if len(sys.argv) > 1:
	confFile = sys.argv[1]
	
#flags
DEBUG = True
#Defaults
pltSvc = PlotService(["heap","footPrint","maxHeapSize","throughput","hardHeapLimit"],15027)
#pltSvc.doNormalise({"heap":1000000,"suggestedHeapSize":1000000,"maxHeapSize":1000000});
#pltSvc.doNormalise({"heap":1000000000.0,"suggestedHeapSize":1000000000.0,"maxHeapSize":1000000000.0,"throughput":100.0});

print "Initialising Registry..."
mon = monitor("ISOLATE",pltSvc);
srv = server(mon,15004);

if srv.start() == False:
    print "Error starting registry server - "+srv.getError();
else:
    print("Starting ...");
    time.sleep(1);
    
    print "Initialising policy...";
    policy = Policy(mon,4,confFile);

    print "Shutting Down..."
    srv.close();
    mon.close();    
print "ktnxbai";