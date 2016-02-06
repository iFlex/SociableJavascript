from plotter import Plotter
import time
import json
import math
import sys
from socket import *
from threading import Thread
from threading import Condition

separator = "|";
period = 1

if len(sys.argv) < 3:
	print "IPC::Usage: python IpcPlotWrapper.py 127.0.0.1:14000 Title";
	sys.exit(1);

print "IPC::Connecting to controller...";
addr = sys.argv[1].split(":");
print "IPC::Connecting:"+str(addr)
soc = socket(AF_INET,SOCK_STREAM);

cond = Condition();
dataQ = []

#try to connect untill success
while True:
	try:
		soc.connect((addr[0], int(addr[1])))
		break;
	except Exception as e:
		print "IPC::Connection failed, retrying..."
		time.sleep(1);

plotter = Plotter(1024,sys.argv[2]);
doExit = False;

print "IPC::Connected, waiting for plot commands"

def handleResponse(cmd):
	global plotter
		
	try:
		cmd = json.loads(cmd);
		now = time.time()
	except Exception as e:
		print "IPC::Json Error:"+str(e);
		print cmd
		return False;

	try:
		#handle commands
		if "action" in cmd:
			if cmd["action"] == "close":
				plotter.save();
				return True;
			if cmd["action"] == "setTitle":
				plotter.reset(cmd["title"]);
				return False;
			if cmd["action"] == "snapshot":
				plotter.save();
				return False;

		plotter.plot(cmd["values"],cmd["labels"]);	

	except Exception as e:
		print "IPC::Plot Error:"+str(e)
	return False;

def keepReceiving():
	global soc,cond,dataQ,plotter,doExit
	request = ""
	while not doExit:
		buff = "";
		try:
		    buff = soc.recv(1450);
		except Exception as e:
		    break;
		ln = len(buff)
		if ln == 0:
			break;

		i = 0
		while i < ln:
			while (i < ln) and (buff[i] != separator):
				request += buff[i]
				i+=1
		
			if not i < ln:
				break;
		
			while (i < ln) and (buff[i] == separator):
				i += 1
		
			if handleResponse(request):
				break;
			request = ""
		
	print "IPC::Closing down the shop...";
	plotter.close();
	try:
		soc.shutdown(SHUT_RDWR);
	except Exception as e:
		print "IPC::IpcPlotWrapper socket shutdown error:"+str(e);

	soc.close();

keepReceiving();

print "IPC::ktnxbay"
