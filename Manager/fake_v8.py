#!/bin/src/python
from Management.Communication.requestbuilder import *
from Management.Communication.communicator import *
from Management.monitor import *
from socket import *
from base64 import *
import json
import time
import sys
import random
import math

address = 0
port = 0 
labels = 0
csv = 0
terminate = False
#Machine properties
HEAP       = 1024*1024 # 1MB
AVAILABLE  = 1024*1024 # 1MB
THROUGHPUT = 1.0       #
#CLI args
try:
    for cmd in sys.argv:
        if "manager=" in cmd:
            cmd = cmd[8:].split(":");
            address = cmd[0];
            port = int(cmd[1])

        if "playback=" in cmd:
            csv = cmd[9:]

except Exception as e:
    print "Could not parse command line arguments "+str(e);
    print "Usage: python fake_v8.py manager=[IP_ADDRESS]:[PORT] playback=[PATH TO CSV FILE TO PLAY BACK]"

if address == 0:
    address = raw_input("IP:")

if port == 0:
    port = input("port:")

if csv == 0:
    csv = raw_input("CSV file to output to manager:")

labels = 0;
try:
    csv = open(csv,"r")
    labels = csv.readline()
    labels = labels.split(",")[0:-1]
except Exception as e:
    print "Could not open CSV file for playback. "+str(e)
    csv = 0 

#initialise monitor
m = monitor("NONE",0);
IDs = [address,0,0];
comm = 0;
r = RequestBuilder(m);

INDEX = 0.0
def fakeAnswer(mid,vid,msg):
    global comm,r,IDs,csv,labels,terminate,HEAP,AVAILABLE,THROUGHPUT,INDEX
    if(msg["global"]["action"] == "status"):
        request = r.statusReport(IDs[0],IDs[1]);
        if csv != 0:
            line = csv.readline()
            print "LINE:("+str(len(line))+") "+line
            if len(line) < 3:
                terminate = True;

            line = line.split(",")[:-1];
            lbln = len(labels)
            lnln = len(line)

            for i in range(0,lnln):
                if i < lbln: 
                    request["isolates"][str(IDs[2])][labels[i]] = float(line[i])*1000000;
                    request["isolates"][str(IDs[2])]["action"] = "update";
        else:
            for i in request["isolates"]:
                request["isolates"][str(IDs[2])]["heap"]       = HEAP;
                request["isolates"][str(IDs[2])]["footPrint"]  = HEAP+2;
                request["isolates"][str(IDs[2])]["throughput"] = THROUGHPUT;
                request["isolates"][str(IDs[2])]["available"]  = AVAILABLE;
                request["isolates"][str(IDs[2])]["action"]     = "update";

                ampl = 50
                HEAP = abs(ampl*math.sin(INDEX))*1024*1024
                AVAILABLE = abs(ampl*0.6*math.sin(INDEX))*1024*1024
                INDEX += 0.1

        request["global"]["action"] = "update";
        comm.send(request);
        print "FAKE ANSWERED"
    else:
        print msg;
        
#network
soc = socket(AF_INET,SOCK_STREAM);
print "Starting message loop..."
while not terminate:
    connected = True;
    try:
        print "Connecting to manager...";
        soc.connect((address,port));
    except Exception as e:
        connected = False;

    comm = communicator(soc,m,IDs[0],fakeAnswer);
    if m.getMachine(IDs[0]) == 0:
        m.addMachine(IDs[0]);
    if m.getV8(IDs[0],IDs[1]) == 0:
        IDs[1] = m.addV8(IDs[0],comm)
    if m.getIsolate(IDs[0],IDs[1],IDs[2]) == 0:
        IDs[2] = m.addIsolate(IDs[0],IDs[1])

    print "Created fake Machine_"+IDs[0]+"_V8_"+str(IDs[1])+"_Isolate_"+str(IDs[2]);
    while connected and not terminate:
        connected = comm.keepRunning;
        newState = raw_input("[HEAP(MB),AVAILABLE(MB),THROUGHPUT]:");
        newState = newState.split(",");
        if len(newState) == 3:
            HEAP = int(newState[0])*1024*1024
            AVAILABLE = int(newState[1])*1024*1024
            THROUGHPUT = float(newState[2])
        else:
            print "Wrong format len="+str(len(newState))+" should be 3";

    print "Updater thread exited..."
    time.sleep(3);
print "Closing last communicator"
comm.close()
print "<>SHUTDOWN COMPLETE<>"