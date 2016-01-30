#!/bin/src/python
from communicator import *
from monitor import *
from server import *
from policy import *
import time
import subprocess

print "V8 Manager CLI"
#create a v8 instance
#print "Starting V8 instance..."
#v8instance = subprocess.Popen(["../v8runner/v8wrapper.bin","1024","../v8runner/jsplayg/endless.js"],0,close_fds=True,stdout=file("/dev/null"));
raw_input("press any key after you start a v8 instance");

print "Reading preload configuration...";
#read initial configuration
preloadScripts = [];
with open("preload.txt") as f:
    content = f.readlines()
    for script in content:
    	if script.find("\n") != -1:
    		script = script[0:len(script)-1];
    	preloadScripts.append(script)

print ""
print "Scripts to be pre-loaded:"
print "_"*80
for script in preloadScripts:
	print script;
print "_"*80

#flags
DEBUG = True
#Defaults
mon = monitor("ALL");
srv = server(mon);

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