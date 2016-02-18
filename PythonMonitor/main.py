#!/bin/src/python
from Management.Communication.server import *
from Management.monitor import *
from Management.policy import *
from PlotFacility.PlotService import *
import time
import subprocess

print "V8 Manager CLI"

print "Reading configuration...";
#read initial configuration
#config = Configuration();

#flags
DEBUG = True
#Defaults
pltSvc = PlotService(["heap","maxHeapSize","footPrint","throughput","hardHeapLimit"],15027)
#pltSvc.doNormalise({"heap":1000000,"suggestedHeapSize":1000000,"maxHeapSize":1000000});
#pltSvc.doNormalise({"heap":1000000000.0,"suggestedHeapSize":1000000000.0,"maxHeapSize":1000000000.0,"throughput":100.0});

mon = monitor("ISOLATE",pltSvc);
srv = server(mon,15004);

if srv.start() == False:
    print "Error starting registry server - "+srv.getError();
else:
    print("Starting ...");
    time.sleep(1);
    print "Initialising policy...";
    policy = Policy(mon,4);

    srv.close();
    mon.close();    
print "ktnxbai";
    #print "Terminating V8 instance...";
    #v8instance.kill();