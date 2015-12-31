#!/bin/src/python
from socket import *
from base64 import *

#Defaults
address = "127.0.0.1"
port = 15000
#network
print "V8 Packetisation Tester"
soc = socket(AF_INET,SOCK_STREAM);
print "Connecting:"+str(address)+":"+str(port)
while True:
    try:
        soc.connect((address,port));
        print "Success";
        break;
    except Exception as e:
        print "Could not connect "+str(e);    

while(True):
	txt = raw_input(":");
	if txt == "s":
		txt = raw_input("JSON:");
		toSend = b64encode(txt);
		padding = ";"*(1450 - len(txt));
		soc.send(toSend+padding);

	if txt == "r":
		print soc.recv(1450);

soc.close();     