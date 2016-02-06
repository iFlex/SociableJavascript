#!/bin/src/python
from communicator import *
from monitor import *
from server import *
from policy import *
import time
import subprocess

print "V8 Manager CLI"

print "Reading configuration...";
#read initial configuration
#config = Configuration();

#flags
DEBUG = True
#Defaults
pltSvc = PlotService(["heap"],15001)
mon = monitor("ALL",pltSvc);
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