#!/usr/bin/python
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
pltSvc = PlotService(["heap","footPrint","maxHeapSize","throughput"],15027)
pltSvc.doNormalise({"heap":1024*1024.0,"footPrint":1024*1024.0,"maxHeapSize":1024*1024.0,"throughput":1.0});

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