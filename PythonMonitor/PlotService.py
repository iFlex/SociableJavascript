from subprocess import *
from PlotServer import *
from sender import *
from socket import *
import time
import json
import random

class PlotService:
	def __init__(self,labels):
		self.pltSoc = 0
		self.pltInstance = 0;
		self.title = "Unnamed";
		self.ready = False;

		self.labels = labels;

	#this means change of focus isolate, so need to clear graph and boom
	def setTitle(self,ttl):
		self.title = ttl;
		if self.ready:
			sendTo(self.pltSoc,{"action":"setTitle","title":self.title});
			
	def init(self):
		self.server = Server(14000);
		print "Starting plotter server...";
		if self.server.start():
			print "Plotter server started";
			self.pltInstance = Popen(["python","IpcPlotWrapper.py","127.0.0.1:14000","none"],0)#,close_fds=True,stdout=file("/dev/null"));
			self.pltSoc = self.server.acquirePlotter();
			self.setTitle(self.title);
			self.ready = True;
			return True;
		else:
			print "Error starting server:"+self.server.getError();
		return False;

	def plot(self,data):
		if self.ready:
			toPlot = [];
			for key in self.labels:
				if key in data:
					toPlot.append(data[key])

			sendTo(self.pltSoc,{"values":toPlot,"labels":self.labels});	
			
	def stop(self):
		if self.ready:
			print "Closing plot server";
			sendTo(self.pltSoc,{"action":"close"});
			self.pltSoc.shutdown(SHUT_RDWR);
			self.pltSoc.close();
			self.server.close();
			print "plot:ktnxbay";

	def takeSnapshot(self):
		if self.ready:
			sendTo(self.pltSoc,{"action":"snapshot"});
	#TODO: add change isolate that is being plotted + graph clearing and a snapshot for the old one