from plotter import Plotter
import time
import json
import math
import sys
from socket import *

separator = ";";
period = 1
last_measurement = 0;

if len(sys.argv) < 3:
	print "Usage: python IpcPlotWrapper.py 127.0.0.1:14000 Title";
	sys.exit(1);

print "Connecting to controller...";
addr = sys.argv[1].split(":");
print "Connecting:"+str(addr)
soc = socket(AF_INET,SOCK_STREAM);

#try to connect untill success
while True:
	try:
		soc.connect((addr[0], int(addr[1])))
		break;
	except Exception as e:
		print "Connection failed, retrying..."
		time.sleep(1);

plotter = Plotter(1024,sys.argv[2]);
last = 0

print "Connected, waiting for plot commands"

def handleResponse(cmd):
	global plotter,last
		
	try:
		cmd = json.loads(cmd);
		now = time.time()
	except Exception as e:
		print "Json Error:"+str(e);
		return False;
	
	try:
		#handle commands
		if "action" in cmd:
			if cmd["action"] == "close":
				return True;
			if cmd["action"] == "setTitle":
				plotter.setTitle( cmd["title"] );
				return False;

		#handle data
		#rpt = 1
		#if last != 0:
		#	rpt = math.floor(now - last) + 1
		#plot the same value multiple times to account for no data received
		#while rpt > 0:
		plotter.plot(cmd["values"],cmd["labels"]);	
		#	rpt -= 1;

		last = now;
	except Exception as e:
		print "Plot Error:"+str(e)
	return False;

response = "";
doExit = False;
while not doExit:
    buff = "";
    try:
        buff = soc.recv(1450);
        #print buff;
    except Exception as e:
        break;

    i = 0
    while i < len(buff):
        while i < len(buff) and buff[i] == separator:
            i += 1                  
        
        if i > 0 and len(response) > 0:
            doExit = handleResponse(response)
            response = ""
        
        if doExit:
        	print "Exiting at:"+response;
        	break;

        while i < len(buff) and buff[i] != separator:
            response += buff[i]
            i += 1
print "Closing down the shop...";
plotter.close();
soc.close();
print "ktnxbay"
