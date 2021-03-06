from PlotServer import *
from socket import *
from threading import RLock
from threading import Thread
from threading import Condition
import time
import json
import random
import os

class PlotService:
	
	def __init__(self,labels,port):
		self.ready = False;
		self.labels = labels;
		self.maxPlotters = 500
		self.port = port;
		self.log = 0;
		
		#heavy parallel plotting
		self.cond = Condition()
		self.updateQ = [];
		self.currentPlotData = {};# key = Machine_[MachineId]_V8_[V8Id]_[IsolateId], value = [plotterSocket,array_of_data_to_plot]
		self.normalise = {}
		
		#start server
		self.server = Server();
		self.reinit(self.port);
		
		#start updater thread
		self.thread = Thread(target = self._update)
		self.thread.daemon = True
		self.thread.start();

	def reinit(self,port):
		self.port = port;
		print "Starting plotter server("+str(port)+")";
		if self.server.start(self.port):
			print "Plotter server started";
			self.ready = True;
		else:
			self.ready = False;
			print "Error starting server:"+self.server.getError();
		return self.ready;
	
	def logInfo(self,key,info):
		if self.log != 0:
			self.log.write("\n"+str(time.strftime("%Y/%m/%d-%H:%M:%S"))+" "+str(key)+" "+str(info))
	
	def initLogger(self):
		logpath = "./out/logs/"
		if not os.path.exists(logpath):
			os.makedirs(logpath)
		self.log = open(logpath+"plotservice.log","a");

	def closeLogger(self):
		if self.log != 0:
			self.log.close();
		self.log = 0

	def toggleLogging(self,toggle):
		print "PlotService::Logging = "+str(toggle)
		if toggle == True:
			self.initLogger();
		else:
			self.closeLogger();

	def setPlotterStartupConfig(self,cfg):
		self.server.setPlotterStartupConfig(cfg);

	def setMaxPlotters(self,_max):
		if _max > -1:
			self.maxPlotters = _max
	
	def doNormalise(self,items):
		for key in items:
			self.normalise[key] = items[key];

	def extractUsefulData(self,info):
		data = [];
		
		for i in self.labels:
			if i in info:
				if i in self.normalise:
					data.append(info[i]/self.normalise[i]);
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
					self.logInfo(key,"CREATED");

				#send plot data
				self.currentPlotData[key][1] = data;
				cdp = self.currentPlotData[key];
				self.server.sendTo(cdp[0],{"values":cdp[1],"labels":self.labels});	

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
								self.server.sendTo(self.currentPlotData[active_key][0],{"action":"idle"});
								self.server.releasePlotter(self.currentPlotData[active_key][0]);
								self.currentPlotData[active_key][0] = 0;
								
								toDel.append(active_key);
								self.logInfo(active_key,"TERMINATED");
								
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
				self.server.sendTo(value[0],{"action":"snapshot","title":"_"});
				self.server.sendTo(value[0],{"action":"close"});
			
			while self.server.getAvailablePlottersCount() > 0:
				print ("Closing spare plotter");
				soc = self.server.acquirePlotter();
				self.server.sendTo(soc,{"action":"snapshot","title":"_"});
				self.server.sendTo(soc,{"action":"close"});
			
			self.logInfo("PlotterService","Shutting down");
			self.toggleLogging(False)

			print "Closing plot server";
			self.server.close();
			print "plot:SHUTDOWN COMPLETE";

	def takeSnapshot(self,key):
		if self.ready and key in self.currentPlotData:
			self.server.sendTo(self.currentPlotData[key][0],{"action":"snapshot"});
			self.logInfo(key,"SNAPSHOT");

	def setTitle(self,key,title):
		if self.ready and key in self.currentPlotData:
			self.server.sendTo(self.currentPlotData[key][0],{"action":"setTitle","title":title});
			self.logInfo(key,"TITLE_CHANGE:"+title)

	#TODO: add change isolate that is being plotted + graph clearing and a snapshot for the old one