#!/usr/bin/python
from Management.Communication.server import *
from Management.monitor import *
from Management.policy import *
from PlotFacility.PlotService import *
import time
import subprocess
import sys

print "V8 Manager CLI"

port = 15004
confFile = "default.txt"

for i in range(0,len(sys.argv)):
    if sys.argv[i] == "port" and i+1 < len(sys.argv):
        port = int(sys.argv[i+1])
    
    if "config=" in sys.argv[i]:
        cfg = sys.argv[i].split("=");
        if len(cfg) > 1:
            confFile = cfg[1];

#Defaults
pltSvc = PlotService(["heap","footPrint","maxHeapSize","throughput"],15027)
pltSvc.doNormalise({"heap":1024*1024.0,"footPrint":1024*1024.0,"maxHeapSize":1024*1024.0,"throughput":1.0});

print "Initialising Registry..."
mon = monitor("ISOLATE",pltSvc);
srv = server(mon,port);

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