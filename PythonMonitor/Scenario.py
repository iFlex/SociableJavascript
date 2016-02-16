import json
from subprocess import *
import time
import os
import math
from Plotter.plotter import *

class Scenario:
	def __init__(self,fileName):
		self.evalRez = []
		self.evalSet = []
		self.config = {}
		self.plotter = 0
		self.logPath = "./processlogs/"
		if not os.path.exists(self.logPath):
			os.makedirs(self.logPath)

		config = ""
		try:
			with open(fileName) as f:
				content = f.readlines()
				for line in content:
					config += line	
		except IOError as e:
			print "Could not open scenario file:"+fileName+" > "+str(e)

		self.scenario = 0
		if len(config) > 0:
			try:
				self.scenario = json.loads(config);
			except Exception as e:
				print "Could not parse scenario file "+fileName+" "+str(e)
				return

		if "config" in self.scenario:
			self.config = self.scenario["config"]

		if "plot" in self.config and self.config["plot"] == True:
				self.plotter = Plotter(100,"ScenarioMemoryUsage",{});

	def startProcess(self,descriptor,count):
		try:
			pname = descriptor[0][descriptor[0].rfind('/')+1:];
			slog = open(self.logPath+"_"+str(count)+"_"+pname+".stdout","w");
			elog = open(self.logPath+"_"+str(count)+"_"+pname+".stderr","w");
			self.evalSet.append((Popen(descriptor,stdout=slog,stderr=elog),time.time()))
		except Exception as e:
			print "@ "+str(descriptor)
			print "ScenarioBldr: Error starting process "+str(e)

	def collectResults(self):
		#os.system('cls')
		os.system('clear');

		memoryUsage = []
		labels      = []
		totalMemoryUsage = 0

		ln = len(self.evalSet)
		for i in range(0,ln):
			process = self.evalSet[i][0]

			memuse = check_output("ps -orss= -ovsz= -p "+str(process.pid), shell=True)
			memuse = memuse.split(" ");
			msum = 0
			for char in memuse:
				try:
					msum += int(char)
				except:
					pass

			print  str(process.pid)+" - "+str(msum)+" B";
			totalMemoryUsage += msum
			memoryUsage.append(msum)
			labels.append(str(process.pid))

			if process.poll() is not None:
				self.evalRez.append({"time":time.time() - self.evalSet[i][1],"retcode":process.returncode});

		self.evalSet = [x for x in self.evalSet if x[0].poll() is None ]	
		
		print "Total - "+str(totalMemoryUsage)+" B"
		if self.plotter != 0:
			self.plotter.plot(memoryUsage,labels)

		if "maxMemory" in self.config:
			if totalMemoryUsage > self.config["maxMemory"]:
				print "CORRECTNESS ERROR - POLICY HAS NOT KEPT TOTAL MEMORY USAGE UNDER "+str(self.config["maxMemory"])+" Bytes"
				ln = len(self.evalSet)
				for i in range(0,ln):
					process = self.evalSet[i][0]
					print "Killing - "+str(process.pid)
					process.kill()

				del self.evalSet[:]
				del self.evalRez[:]

	def prettifyTime(self,time):
		seconds = math.floor(time);
		millis  = int(math.floor(time/1000));
		
		mins    = math.floor(seconds/60)
		seconds = int(seconds%60);

		hours   = int(math.floor(seconds/60));
		mins    = int(mins%60);

		return str(hours)+":"+str(mins)+":"+str(seconds)+"."+str(millis);

	def isSuccess(self,code):
		if code == 0:
			return "OK"
		return "XX"
		
	def prettyResult(self):
		out = ""
		total = 0
		success = 0
		for item in self.evalRez:
			ret = self.isSuccess(item["retcode"])
			if ret is "OK":
				success += 1
			total += 1
			out += ret +" > "+self.prettifyTime(item["time"])+"\n";
		
		out += ("_"*20)+"\nTotal Processes:"+str(total)+"\nSuccessful:"+str(success)+"("+str(float(success)/total*100)+"%)"+"\nFailed    :"+str(total-success)+"("+str(float(total-success)/total*100)+"%)";
		return out

	def run(self):
		if self.scenario == 0:
			return;

		config = self.scenario["config"];
		for process in self.scenario["run"]:
			count = process[0]
			while count > 0:
				self.startProcess(process[1],count)
				count -= 1

		while len(self.evalSet) > 0:
			self.collectResults()
			time.sleep(0.001)

		if len(self.evalRez) > 0:
			print "All processes finished"
			print self.prettyResult()