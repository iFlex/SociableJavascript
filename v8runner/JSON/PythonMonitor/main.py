#!/bin/src/python
from communicator import *
from monitor import *
from socket import *

#flags
DEBUG = True
#Defaults
address = "127.0.0.1"
port = 15000
#network
mon = monitor();

print "V8 Manager CLI"
soc = socket(AF_INET,SOCK_STREAM);
print "Connecting:"+str(address)+":"+str(port)
while True:
    try:
        soc.connect((address,port));
        print "Success";
        break;
    except Exception as e:
        print "Could not connect "+str(e);

comm = communicator(soc,mon);
policy = Policy(comm,mon);
policy.run();
