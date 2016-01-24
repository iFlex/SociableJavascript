#!/bin/src/python
from communicator import *
from monitor import *
from socket import *
from policy import *
import time
import subprocess

print "V8 Manager CLI"
#create a v8 instance
#print "Starting V8 instance..."
#v8instance = subprocess.Popen(["../v8runner/v8wrapper.bin","1024","../v8runner/jsplayg/endless.js"],0,close_fds=True,stdout=file("/dev/null"));
raw_input("press any key after you start a v8 instance");

print "Reading preloading configuration...";
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
address = "127.0.0.1"
port = 15000
#network
mon = monitor();

soc = socket(AF_INET,SOCK_STREAM);
print "Connecting to local V8 instance:"+str(address)+":"+str(port)
while True:
    try:
        soc.connect((address,port));
        print "Success";
        break;
    except Exception as e:
        continue; #print "Could not connect "+str(e);    

print("Starting ...");
time.sleep(1);
print "Initialising communicator";
comm = communicator(soc,mon);
print "Initialising policy...";
policy = Policy(comm,mon,preloadScripts);

#print "Terminating V8 instance...";
#v8instance.kill();
