from subprocess import *
from server import *
from sender import *
import time
import json
import random

server = Server(14000);
print "Starting plotter server...";
if server.start():
	print "Plotter server started";
	instance = Popen(["python","IpcPlotWrapper.py","127.0.0.1:14000","none"],0,close_fds=True,stdout=file("/dev/null"));
	soc = server.acquirePlotter();
	print "Yay got a plotter socket:"+str(soc);
	sendTo(soc,{"action":"setTitle","title":"Super Test"});
	
	i = 0;
	data = {"values":[0,0,0],"labels":["heap","suggested","throughput"]}
	while i < 100:
		data["values"][0] = random.randint(0,500);
		data["values"][1] = random.randint(0,500);
		data["values"][2] = random.randint(0,500);
		
		sendTo(soc,data);
		time.sleep(0.02);
		i += 1
	print "Done sendint stuff";
	sendTo(soc,{"action":"close"});	
	soc.close();
	server.close();
else:
	print "Error starting server:"+server.getError();
print "ktnxbay";