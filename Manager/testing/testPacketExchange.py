#!/bin/src/python
from Management.Communication.communicator import *
from Management.monitor import *
from socket import *
from Management.policy import *
from Management.Communication.requestbuilder import *
import time;
import os
import subprocess

print "V8 Packet Exchange test. You need to start a V8 instance for this test"
#create a v8 instance
v8instance = 0
c = raw_input("Would you to attempt to automatically start one?(y/n)")
if c == 'y':
    try:
        print "Starting V8 instance..."
        path = os.getcwd()
        path += "/../../v8runner/"
        print "Assumed V8 wrapper location:"
        print path;
        v8instance = subprocess.Popen([path+"v8wrapper.bin","1024",path+"test/binarytree.js"],0,close_fds=True,stdout=file("/dev/null"));
    except Exception as e:
        print "ERROR: Failed to start V8 instance... "+str(e)
        v8instance = 0

if v8instance == 0:
    raw_input("Press any key after you have started a V8 instance")

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

if v8instance != 0:
    raw_input("Terminate?");
    print "Terminating V8 instance...";
    v8instance.kill();