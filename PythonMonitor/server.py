from socket import *
from threading import Thread
from communicator import *

import sys, traceback

class server:
	def __init__(self,monitor):
		self.soc = socket(AF_INET,SOCK_STREAM);
		
		self.maxConcurrentInstances = 50;
		self.address = ""
		self.port = 15000
		self.error = "";
		
		self.keepRunning = True;
		self.lock = RLock();

		self.monitor = monitor;

	def listen(self):
		try:
			self.soc.listen(self.maxConcurrentInstances);
		except Exception as e:
			self.error = "Listen error:"+str(e);
			self.keepRunning = False;

		while self.keepRunning:
			try:
				soc,addr = self.soc.accept()
				addr = str(addr)
				machineId = self.monitor.getMachine(addr);
				if machineId == 0:
					machineId = self.monitor.addMachine(addr); 
		 		
		 		communicator(soc,self.monitor,machineId)
			except Exception as e:
				self.error = "Accept error:"+str(e);
				print "#ACCEPT ERROR:"+e;
				traceback.print_exc(file=sys.stdout)

	def start(self):
		#bind to port
		try:
			self.soc.bind((self.address,self.port));
		except Exception as e:
			self.error = "Bind error:"+str(e);
			return False;

		print "Starting V8 registry server...";
		self.thread = Thread(target = self.listen)
		self.thread.start();

		return True;

	def close(self):
		self.keepRunning = False;
		self.soc.close();
		self.thread.join();

	def getError(self):
		return self.error;