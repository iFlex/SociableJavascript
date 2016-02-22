#!/bin/src/python
from Management.Communication.communicator import *
from Management.monitor import *
from socket import *
from Management.policy import *
from Management.Communication.requestbuilder import *
import time;

import subprocess

print "V8 Packet Exchange test"
#create a v8 instance
#print "Starting V8 instance..."
#v8instance = subprocess.Popen(["../v8runner/v8wrapper.bin","1024","../v8runner/jsplayg/endless.js"],0,close_fds=True,stdout=file("/dev/null"));
raw_input("Press any key after you have started a V8 instance");

#flags
DEBUG = True
#Defaults
address = "127.0.0.1"
port = 15004
#network
mon = monitor("NONE",0);

soc = socket(AF_INET,SOCK_STREAM);
print "Connecting to local V8 instance:"+str(address)+":"+str(port)
while True:
    try:
        soc.connect((address,port));
        print "Success";
        break;
    except Exception as e:
        continue; #print "Could not connect "+str(e);    

print "Initialising communicator";
requester = RequestBuilder(mon);
comm = communicator(soc,mon);

#start sending requests
for i in range(0,10):
	rqst = requester.startScript(1,"/home/airjack/level4/SociableJavascript/benchmarks/a_BinaryTrees.js");#statusReport(1);
	print "Sending:"+str(rqst);
	comm.send(rqst);
	time.sleep(1);

raw_input("Terminate?");
#print "Terminating V8 instance...";
#v8instance.kill();