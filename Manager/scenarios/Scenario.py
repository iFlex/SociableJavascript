import json
from subprocess import *
import time
import os
import math

MB = 1024*1024
class Scenario:
	def __init__(self,fileName,plotter):
		self.evalRez = []
		self.evalSet = []
		self.config = {}
		self.plotter = plotter
		self.defaultMemoryUsage = 1024*MB
		self.minHeapSize = 0;
		self.policyName = "?"
		self.pStartDate = ""

		self.logPath = "./out/processlogs/"
		if not os.path.exists(self.logPath):
			os.makedirs(self.logPath)
		
		print "Cleaning up previous scenario output"
		for the_file in os.listdir(self.logPath):
			file_path = os.path.join(self.logPath, the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
			except Exception, e:
				pass

		self.summaryPath = "./out/scenarios/"
		if not os.path.exists(self.summaryPath):
			os.makedirs(self.summaryPath)
		self.resultFile = open(self.summaryPath+str(time.strftime("%Y_%b_%d_%H_%M"))+"output.txt","w")

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


		if self.plotter == 0:
			return

		if "plot" in self.config and self.config["plot"] == True:
			plotter.configure({"fps":64,"makePNG":True,"path":self.logPath});
		else:
			plotter.close();
			self.plotter = 0;
			
	def startProcess(self,descriptor,count):
		try:
			slog = open(self.logPath+"_"+str(count)+".stdout","w");
			elog = open(self.logPath+"_"+str(count)+".stderr","w");

			print "Started "+str(descriptor)
			self.evalSet.append((Popen(descriptor,stdout=slog,stderr=elog),time.time(),descriptor))
			
			if "sequential" in self.config and self.config["sequential"] == True:
				while len(self.evalSet) > 0:
					self.collectResults()
					time.sleep(0.1)

		except Exception as e:
			print "@ "+str(descriptor)
			print "ScenarioBldr: Error starting process "+str(e)

	def collectResults(self):
		global MB
		surviving   = []
		memoryUsage = [0]
		labels      = ["Total"]
		totalMemoryUsage = 0

		ln = len(self.evalSet)
		for i in range(0,ln):
			process = self.evalSet[i][0]

			#slowest component
			msum = 0
			if "maxMemory" in self.config:
				memuse = check_output("ps -orss= -ovsz= -p "+str(process.pid), shell=True)
				memuse = memuse.split(" ");
				for char in memuse:
					try:
						msum += int(char)
					except:
						pass

			totalMemoryUsage += msum
			memoryUsage.append(msum)
			labels.append(str(process.pid))

			if process.poll() is not None:
				self.evalRez.append({"time":time.time() - self.evalSet[i][1],"retcode":process.returncode,"desc":self.evalSet[i][2]});
				finish = "Failed  "
				if process.returncode == 0:
					finish = "Finished"
				print "Process("+str(process.pid)+") "+finish+" -> "+self.prettifyTime(self.evalRez[len(self.evalRez)-1]["time"]);
			else:
				surviving.append(self.evalSet[i])
		
		self.evalSet = surviving
		#print "Total - "+str(totalMemoryUsage)+" B"
		if self.plotter != 0:
			memoryUsage[0] = totalMemoryUsage
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
	
	def strDesc(self,desc):
		if len(desc) == 3:
			return desc[2][desc[2].rfind("/")+1:]
		elif len(desc) > 3:
			return desc[2];
		else:
			return str(desc)

	def nicePrintMagnitude(self,raw,unit,magnitudes):
		mp = ["G","M","K"]
		for i in range(0,len(mp)):
			if raw >= magnitudes[i]:
				return str(raw/magnitudes[i])+" "+mp[i]+unit
		return str(raw)+" "+unit;
	
	def prettyResult(self):
		out = ""
		success = 0
		for item in self.evalRez:
			ret = self.isSuccess(item["retcode"])
			if ret is "OK":
				success += 1
			out += ret +" > "+self.prettifyTime(item["time"])+"-"+self.strDesc(item["desc"])+"\n";
		
		total = len(self.evalRez)
		out += ("_"*20)+"\nTotal Processes:"+str(len(self.evalRez))+"\nSuccessful:"+str(success)+"("+str(float(success)/total*100)+"%)"+"\nFailed    :"+str(total-success)+"("+str(float(total-success)/total*100)+"%)";
		return out

	def run(self):
		if self.scenario == 0:
			return;

		globalCount = 0;
		start = time.time()
		config = self.scenario["config"];
		for process in self.scenario["run"]:
			count = process["instanceCount"]
			self.resultFile.write(str(count)+"x "+process["program"]+" -> "+str(process["params"]))
			
			if "minimumHeapSize" in process:
				self.minHeapSize += process["minimumHeapSize"] * count;
			else:
				self.minHeapSize += self.defaultMemoryUsage * count;

			while count > 0:
				rundesc = [process["program"]]+process["params"]
				self.startProcess(rundesc,globalCount)
				globalCount += 1
				count -= 1

		self.pStartDate = str(time.strftime("%Y_%b_%d_%H_%M"))

		while len(self.evalSet) > 0:
			self.collectResults()
			time.sleep(0.1)

		if self.plotter != 0:
			self.plotter.close()

		if len(self.evalRez) > 0:
			print "All processes finished - "
			print "Target Memory Utilisation:"+self.nicePrintMagnitude(self.minHeapSize,"B",[1024*1024*1024,1024*1024,1024])
			r = self.prettyResult()
			print r

			self.resultFile.write("All processes finished\n");
			self.resultFile.write(r)
			self.resultFile.close()
		print "Total Scenario Run Time "+self.prettifyTime(time.time() - start)
#todo: add prints of stdout and err of each process
