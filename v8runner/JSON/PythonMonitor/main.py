#!/bin/src/python
import operations;
import packaging;

#flags
DEBUG = True
#Defaults
address = "127.0.0.1"
port = 12456

#network

from socket import *

print "V8 Manager CLI"
soc = socket(AF_INET,SOCK_STREAM);
print "Connecting:"+str(address)+":"+str(port)
try:
    soc.connect((address,port));
    print "Success";
except Exception as e:
    print "Could not connect "+str(e);
    #if DEBUG == False:


#exec loop
while True:
    cmd = raw_input(">");
    if cmd == "exit":
        break;

    operations.execute(cmd);

print "Closing connection"
soc.close();
