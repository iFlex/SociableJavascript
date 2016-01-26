from socket import *
from threading import Thread
from threading import Condition
import sys, traceback

class Server:
	def __init__(self,port):
		self.soc = socket(AF_INET,SOCK_STREAM);
		
		self.maxConcurrentInstances = 50;
		self.address = ""
		self.port = port
		self.error = "";
		
		self.keepRunning = True;
		self.lock = Condition();

		self.freeSocks = [];

	def listen(self):
		try:
			self.soc.listen(self.maxConcurrentInstances);
		except Exception as e:
			self.error = "Listen error:"+str(e);
			self.keepRunning = False;
		while self.keepRunning:
			try:
				soc,addr = self.soc.accept()
				print "New plotter connected...";
				self.releasePlotter(soc);
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

	#blocks untill plotter is found
	def releasePlotter(self,soc):
		self.lock.acquire();
		self.freeSocks.append(soc);
		self.lock.notify();
		self.lock.release();
		
	def acquirePlotter(self):
		ret = 0;
		
		self.lock.acquire();
		self.lock.wait();
		ret = self.freeSocks.pop(0);
		self.lock.release();

		return ret;
