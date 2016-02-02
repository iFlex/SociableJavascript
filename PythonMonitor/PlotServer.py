from socket import *
from threading import Thread
from threading import Condition
from subprocess import *
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

		self.maxPlotters = 50;
		self.startedPlotters = [];
		self.freeSocks = [];

	def listen(self):
		try:
			self.soc.listen(self.maxConcurrentInstances);
		except Exception as e:
			self.error = "PlotServer::Listen error:"+str(e);
			return;

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
				return;


	def start(self):
		#bind to port
		try:
			self.soc.bind((self.address,self.port));
		except Exception as e:
			self.error = "PlotServer::Bind error:"+str(e);
			self.keepRunning = False;
			return False;

		print "Starting PlotServer registry server...";
		self.thread = Thread(target = self.listen)
		self.thread.daemon = True
		self.thread.start();

		return True;

	def close(self):
		self.keepRunning = False;
		try:
			self.soc.shutdown(SHUT_RDWR);
		except Exception as e:
			print "PlotServer socket shutdown error:"+str(e);
		self.soc.close();
		#self.thread.join();

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
		
		self.startedPlotters.append(Popen(["python","IpcPlotWrapper.py","127.0.0.1:14000",key],0))#,close_fds=True,stdout=file("/dev/null")));
		return True;	
