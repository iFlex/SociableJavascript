from socket import *
from threading import Thread
from threading import Condition
from subprocess import *
import sys, traceback
import json

class Server:
	def __init__(self):
		self.soc = socket(AF_INET,SOCK_STREAM);
		
		self.maxConcurrentInstances = 50;
		self.address = ""
		self.error = "";

		self.keepRunning = True;
		self.isListening = False;
		self.lock = Condition();

		self.maxPlotters = 50;
		self.startedPlotters = [];
		self.freeSocks = [];

		self.plotterStartupConfig = {};
	
	def setPlotterStartupConfig(self,cfg):
		self.plotterStartupConfig = cfg;

	def listen(self):
		try:
			self.soc.listen(self.maxConcurrentInstances);
		except Exception as e:
			self.error = "PlotServer::Listen error:"+str(e);
			return;

		self.isListening = True;
		while self.keepRunning:
			try:
				soc,addr = self.soc.accept()
				print "PlotServer::New plotter connected...";
				self.releasePlotter(soc);
			except Exception as e:
				self.error = "PlotServer::Accept error:"+str(e);
				print self.error;
				traceback.print_exc(file=sys.stdout)
				print "###PlotServer shutting down!";
				break;
		self.isListening = False;
	
	def start(self,port):
		
		if self.isListening:
			self.soc = socket(AF_INET,SOCK_STREAM)
			self.isListening = False

		#bind to port
		self.port = port;
		self.keepRunning = True
		try:
			self.soc.bind((self.address,self.port));
		except Exception as e:
			self.error = "PlotServer::Bind error:"+str(e);
			self.keepRunning = False;
			return False;

		print "Starting PlotServer registry server @ port "+str(self.port);
		
		if not self.isListening: 
			self.thread = Thread(target = self.listen)
			self.thread.daemon = True
			self.thread.start();

		return True;

	def close(self):
		self.keepRunning = False;
		self.soc.close();

	def getError(self):
		return self.error;

	#blocks untill plotter is found
	def releasePlotter(self,soc):
		self.lock.acquire();
		self.freeSocks.append(soc);
		if len(self.freeSocks) - 1 == 0:
			self.lock.notify();
		self.lock.release();
	
	def getAvailablePlottersCount(self):
		ln = 0;
		self.lock.acquire();
		ln = len(self.freeSocks);
		self.lock.release();

		return ln;	
			
	def acquirePlotter(self):
		ret = 0;
		
		self.lock.acquire();
		if len(self.freeSocks) == 0:
			self.lock.wait();
		ret = self.freeSocks.pop();
		self.lock.release();

		return ret;

	def startNewPlotterProcess(self,key):
		if(len(self.startedPlotters) > self.maxPlotters):
			return False;
		
		conf = "{}"
		try:
			conf = json.dumps(self.plotterStartupConfig)
		except Exception as e:
			pass

		self.startedPlotters.append(Popen(["python","./Plotter/IpcPlotWrapper.py","127.0.0.1:"+str(self.port),key,conf],0))#,close_fds=True,stdout=file("/dev/null")));
		return True;

	def sendTo(self,soc,data):
		packet_size = 1450;
		separator = "|"

		try:
			data = json.dumps(data);
		except Exception as e:
			print "Could not encode to JSON:"+str(e)
			return 1;

		data += separator
	
		try:
			soc.send(data);
		except Exception as e:
			print "Network error:"+str(e)
			return 0;