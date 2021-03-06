from socket import *
from threading import Thread
from communicator import *

import sys, traceback

class server:
	def __init__(self,monitor,port):
		self.soc = socket(AF_INET,SOCK_STREAM);
		
		self.maxConcurrentInstances = 50;
		self.address = ""
		self.port = port
		self.error = "";
		
		self.keepRunning = True;
		self.lock = RLock();

		self.monitor = monitor;

	def listen(self):
		try:
			self.soc.listen(self.maxConcurrentInstances);
		except Exception as e:
			self.error = "Listen error:"+str(e);
			return;

		while self.keepRunning:
			try:
				soc,addr = self.soc.accept()
				addr = str(addr[0])
				print "Incoming "+addr;
				machineId = self.monitor.getMachine(addr);
				if machineId == 0:
					machineId = self.monitor.addMachine(addr); 
		 		else:
		 			machineId = machineId["id"];

		 		communicator(soc,self.monitor,machineId,self.monitor.update);
			except Exception as e:
				self.error = "Accept error:"+str(e);
				print self.error;
				traceback.print_exc(file=sys.stdout)

	def start(self):
		#bind to port
		try:
			self.soc.bind((self.address,self.port));
		except Exception as e:
			self.error = "Bind error:"+str(e);
			self.keepRunning = False;
			return False;

		print "Starting V8 registry server @ port "+str(self.port);
		self.thread = Thread(target = self.listen)
		self.thread.daemon = True
		self.thread.start();

		return True;

	def close(self):
		self.keepRunning = False;
		
		try:
			self.soc.close();
		except Exception as e:
			print "Server socket shutdown failed:"+str(e);
		
		#self.thread.join();

	def getError(self):
		return self.error;