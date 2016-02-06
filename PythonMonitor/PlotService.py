from PlotServer import *
from sender import *
from socket import *
from threading import RLock
from threading import Thread
from threading import Condition
import time
import json
import random

class PlotService:
	def __init__(self,labels,port):
		self.ready = False;
		self.labels = labels;
		self.maxPlotters = 10
		self.port = port;
		#heavy parallel plotting
		self.cond = Condition()
		self.updateQ = [];
		self.currentPlotData = {};# key = Machine_[MachineId]_V8_[V8Id]_[IsolateId], value = [plotterSocket,array_of_data_to_plot]
		#TODO:
		self.ignoreList = [];   #list of isolates to ignore 
		self.interestList = []; #list of isolates to take interest in and ignore the rest
	
	def init(self):
		self.server = Server(self.port);
		print "Starting plotter server...";
		if self.server.start():
			print "Plotter server started";
			self.ready = True;
			self.thread = Thread(target = self._update)
			self.thread.daemon = True
			self.thread.start();

			return True;
		else:
			print "Error starting server:"+self.server.getError();
		return False;
	
	def setMaxPlotters(self,_max):
		if _max > -1:
			self.maxPlotters = _max

	def extractUsefulData(self,info):
		data = [];
		
		for i in self.labels:
			if i in info:
				if i == "available" and "heap" in info:
					info[i] += info["heap"]
				if i == "heap" or i == "maxHeapSize" or i == "available":
					data.append(info[i]/1000000);
				else:
					data.append(info[i])

		return data;
	
	def _update (self):
		data = [];
		info = [];
		plotterSoc = 0;
		key = "";

		while True:
			self.cond.acquire();
			if len(self.updateQ) == 0:
				self.cond.wait();
			
			key = self.updateQ[0][0];
			info = self.updateQ[0][1];
			self.updateQ.pop(0);
			
			self.cond.release();
			
			data = self.extractUsefulData(info);
			
			if len(data) > 0:
				#place the data in the structure to be updated
				if key not in self.currentPlotData:

					if len(self.currentPlotData.keys()) > self.maxPlotters:
						continue

					self.currentPlotData[key] = [0,0];

					if self.server.getAvailablePlottersCount() == 0:
						if not self.server.startNewPlotterProcess(key):
							del self.currentPlotData[key]
							continue
							
					self.currentPlotData[key][0] = self.server.acquirePlotter();
					self.setTitle(key,key);

				#send plot data
				self.currentPlotData[key][1] = data;
				cdp = self.currentPlotData[key];
				sendTo(cdp[0],{"values":cdp[1],"labels":self.labels});	

			else:
				if "action" in info:
					action  = info["action"]
					if action == "setTitle":
						self.setTitle(key,info["title"]);
					if action == "takeSnapshot":
						self.takeSnapshot(key);
					if action == "died":
						toDel = []
						for active_key in self.currentPlotData.keys():
							if key in active_key:
								self.server.releasePlotter(self.currentPlotData[active_key][0]);
								self.currentPlotData[active_key][0] = 0;
								#sendTo(key,{"action":"close"})
								#print self.server.getAvailablePlottersCount();
								toDel.append(active_key);
								
						for active_key in toDel:
							del self.currentPlotData[active_key];
					
	
	def update(self,key,data):
		self.cond.acquire();
		self.updateQ.append((key,data));
		if len(self.updateQ) == 1:
			self.cond.notify();
		self.cond.release();	
			
	def stop(self):
		if self.ready:
			for key in self.currentPlotData.keys():
				value = self.currentPlotData[key];
				print "Closing Plotter:"+str(key);
				sendTo(value[0],{"action":"snapshot","title":"_"});
				sendTo(value[0],{"action":"close"});
			
			while self.server.getAvailablePlottersCount() > 0:
				print ("Closing spare plotter");
				soc = self.server.acquirePlotter();
				sendTo(soc,{"action":"snapshot","title":"_"});
				sendTo(soc,{"action":"close"});
			
			print "Closing plot server";
			self.server.close();
			print "plot:ktnxbay";

	def takeSnapshot(self,key):
		if self.ready and key in self.currentPlotData:
			sendTo(self.currentPlotData[key][0],{"action":"snapshot"});

	def setTitle(self,key,title):
		if self.ready and key in self.currentPlotData:
			sendTo(self.currentPlotData[key][0],{"action":"setTitle","title":title});

	
	#TODO: add change isolate that is being plotted + graph clearing and a snapshot for the old one