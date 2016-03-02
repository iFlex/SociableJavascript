import sys, traceback
import os
import json
from subprocess import *
from os import listdir
from os.path import isfile, join

class CommandLine:
	
	def __init__(self,policy):
		self.p = policy;
		self.monitor = self.p.monitor;
		self.echo = True
		self.initCmds()
		self.history = []

	def addToHistory(self,cmd):
		if len(self.history) == 0 or self.history[len(self.history)-1] != cmd:
			self.history.append(cmd)

		if len(self.history) > 9:
			self.history.pop(0)

	def execHistory(self,pos):
		if pos >= 0 and pos <= len(self.history):
			cmd = self.history[len(self.history) - pos]
			print cmd
			self.execute(cmd)
		else:
			print "* No such command in history"

	def printHistory(self):
		cnt = len(self.history)
		if cnt == 0:
			print "Empty Command History"
			return

		for i in self.history:
			print str(cnt)+":"+i;
			cnt -= 1

	def toggleEcho(self,toggle):
		if toggle == 0:
			self.echo = False;
		else:
			self.echo = True;
		print "Echo is now:"+str(self.echo)

	def getCommandShortForms(self,cmd):
		forms = []
		for i in self.shortForms:
			form = self.shortForms[i];
			if form == cmd:
				forms.append(i)
		return forms
	
	def listNiceFormat(self,lst,sep):
		st = ""
		for item in lst:
			st += str(item)+sep
		return st

	def help(self):
		print "Monitor Commands "
		print "_"*80
		keys = self.commands.keys()
		keys.sort(key=str.lower);
		for key in keys:
			params = ""
			types  = " " * len(key)
			for i in range(0,len(self.commands[key]["param"])):
				params += " ["+self.commands[key]["param"][i][1]+"("+self.commands[key]["param"][i][0]+")]"
			print ">> "+key+params;
			
			details = ""
			sf = self.getCommandShortForms(key)
			if len(sf) > 0:
				details = "   ("+self.listNiceFormat(sf," ")+") "
			
			if "desc" in self.commands[key]:
				details += self.commands[key]["desc"]
			
			if len(details)>0:
				print details

		print "_"*80

	def printUsage(self,cmd,params):
		p = ""
		for i in params:
			p += " ["+str(i[1])+" ("+str(i[0])+")]"
		print "Usage: "+cmd+" "+p

	def matchCommand(self,cmd):
		if cmd[0] in self.shortForms:
			cmd[0] = self.shortForms[cmd[0]]

		if cmd[0] in self.commands:
			params = self.commands[cmd[0]]["param"]
			method = self.commands[cmd[0]]["method"]
			
			if self.echo:
				print "."+str(cmd)

			if len(cmd) - 1 < len(params):
				self.printUsage(cmd[0],params)
			else:
				actuals = []
				for i in range(0,len(params)):
					if params[i][0] == "int":
						actuals.append(int(cmd[i+1]))
					elif params[i][0] == "float":
						actuals.append(float(cmd[i+1]))
					elif params[i][0] == "str":
						actuals.append(str(cmd[i+1]))
				
				ln = len(actuals)
				if ln == 0:
					method()
				elif ln == 1:
					method(actuals[0])
				elif ln == 2:
					method(actuals[0],actuals[1])
				elif ln == 3:
					method(actuals[0],actuals[1],actuals[2])
				elif ln == 4:
					method(actuals[0],actuals[1],actuals[2],actuals[3])

				self.addToHistory(" ".join(cmd))
		else:
			if len(cmd[0]) == 0:
				self.prettyPrint()
			else:
				print "Unknown command '"+cmd[0]+"'"

	def execute(self,cmd):
		cmd = cmd.split(" ");
		try:
			self.matchCommand(cmd);
		except Exception as e:
			print "* CLI ERROR:"+str(e);
			traceback.print_exc(file=sys.stdout)
	
	def run(self):
		self.machine_id = "127.0.0.1";
		self.v8_id      = 1;
		while True:
			cmd = raw_input(">");
			
			if cmd == "exit":
			   break;

			if cmd.isdigit():
				try:
					self.execHistory(int(cmd));
				except:
					pass
				continue;

			self.execute(cmd);

		self.p.keepRunning = False

	def prettyPrint(self):
		os.system('clear');
		self.monitor.prettyPrint(self.machine_id,self.v8_id,False,False)

	def printMachines(self):
		os.system('clear');
		self.monitor.prettyPrint(self.machine_id,self.v8_id,True,True)

	def printV8s(self):
		os.system('clear');
		self.monitor.prettyPrint(self.machine_id,self.v8_id,False,True)

	def nicePrintMagnitude(self,raw,unit,magnitudes):
		mp = ["G","M","K"]
		for i in range(0,len(mp)):
			if raw >= magnitudes[i]:
				return str(int(raw/magnitudes[i]))+" "+mp[i]+unit
		return str(raw)+" "+unit;

	def hz(self):
		print "Polling frequency "+self.nicePrintMagnitude(1/self.p.interval,"Hz",[1000000000,1000000,1000]);
		print "Estimated Network Load "+self.nicePrintMagnitude(2048*(1.0/self.p.interval),"B/s",[1024*1024*1024,1024*1024,1024]) + " -> " + self.nicePrintMagnitude(8*2048*(1.0/self.p.interval),"b/s",[1000000000,1000000,1000]);

	def chhz(self,hz):
		print "Attempting to change polling frequency to "+str(hz)+" Hz";
		print "."*40
		self.p.changeSamplingFrequency(hz)
		self.hz()

	def where(self):
		print "@ Machine_"+str(self.machine_id)+" V8_"+str(self.v8_id);

	def chv8(self,id):
		self.v8_id = id;

	def switch(self,m,v):
		self.machine_id = m;
		self.v8_id = v;
		self.where()

	def takeSnapshot(self,iid):
		self.monitor.takeSnapshot(self.machine_id,self.v8_id,iid);

	def suggest(self,id,size):
		comm = self.monitor.getV8Comm(self.machine_id,self.v8_id);
		comm.send(self.p.requestBldr.recommendHeapSize(self.machine_id,self.v8_id,id,size*1024*1024,0));

	def setmax(self,id,size):
		comm = self.monitor.getV8Comm(self.machine_id,self.v8_id);
		comm.send(self.p.requestBldr.setMaxHeapSize(self.machine_id,self.v8_id,id,size,0));
	
	def runscript(self,script):
		comm = self.monitor.getV8Comm(self.machine_id,self.v8_id);
		comm.send(self.p.requestBldr.startScript(self.machine_id,self.v8_id,script));
	
	def setNewMachineMemoryLimit(self,limit):
		self.monitor.newMachineMemLimit = limit*1024*1024;

	def setMachineMemoryLimit(self,mid,limit):
		machine = self.monitor.getMachine(mid);
		if machine != 0:
			machine["memoryLimit"] = limit;
			return True;
		return False;

	def setPlotterStartupConfig(self,strcfg):
		try:
			cfg = json.loads(strcfg);
			cfg["action"] = "settings";
			print "StartupPlotterConfig:"+strcfg
			self.monitor.plotter.setPlotterStartupConfig(cfg);
		except Exception as e:
			print "ERROR your json is invalid:"+str(e)
	
	def policyName(self):
		print self.p.policy.name();
	
	def policyStats(self):
		print self.p.policy.stats()

	def getRegistryNetUsage(self):
		comms = self.monitor.listCommunicators();
		print "Registry Network Usage "+"_"*40
		for comm in comms:
			print str(comm[1])+"_V8_"+str(comm[2])+" "+comm[0].getStrStats()
		print "_"*60

	def runScenario(self,path,cpath):
		if path.find("/") == -1:
			path = "./scenarios/"+path
		if path.find(".json") == -1:
			path += ".json"

		polName = ""
		try:
			polName = self.p.policy.name();
		except:
			pass

		self.scenario = Popen(["python","runscen.py",path,cpath,polName],0)

	def listFiles(self,path,ext):
		accumulator = ""
		for f in listdir(path):
			if isfile(join(path, f)):
				if f.rfind(ext) > -1 and f.rfind(ext)+len(ext) == len(f):
					accumulator+= str(join(path, f))+"\n";
			else:
				accumulator += self.listFiles(join(path, f),ext)
		return accumulator

	def listScenarios(self):
		path = "./scenarios/"
		print self.listFiles(path,".json");

	def listPolicies(self):
		path = "./Policies/"
		print self.listFiles(path,".py").replace(path,"");

	def togglePServiceLogging(self,toggle):
		self.monitor.plotter.toggleLogging(toggle=="ON")
		
	def initCmds(self):
		self.commands = {
							"help":{
								"param":[],
								"method":self.help,
							},
							"chhz":{
								"param":[("float","frequency in Hz")],
								"method":self.chhz,
								"desc":"Change the machine polling frequency."
							},
							"hz":{
								"param":[],
								"method":self.hz,
								"desc":"Get the current polling frequency"
							},
							"stats":{
								"param":[],
								"method":self.prettyPrint,
								"desc":"Status report of all machines, V8 and isolates."
							},"machines":{
								"param":[],
								"method":self.printMachines,
								"desc":"Status report of all machines, V8 and isolates."
							},"v8s":{
								"param":[],
								"method":self.printV8s,
								"desc":"Status report of all machines, V8 and isolates."
							},
							"dbg":{
								"param":[],
								"method":self.monitor.debug
							},
							"where":{
								"param":[],
								"method":self.where,
								"desc":"What V8 from what machine the shell is set to at the moment."
							},
							"loadpolicy":{
								"param":[("str","policy name")],
								"method":self.p.loadPolicy,
								"desc":"Load a difference memory management ploicy."
							},
							"chv8":{
								"param":[("int","V8Id")],
								"method":self.chv8,
								"desc":"Change the V8 that the shell is set to."
							},
							"switch":{
								"param":[("str","machineId"),("int","V8Id")],
								"method":self.switch,
								"desc":"Change the machine and V8 that the shell is set to."
							},
							"snapshot":{
								"param":[("int","isolateId")],
								"method":self.takeSnapshot,
								"desc":"Take a snapshot of an isolate form the V8 the shell is set to."
							},
							"suggest":{
								"param":[("int","isolateId"),("int","heap size in bytes")],
								"method":self.suggest,
								"desc":"Send hard limmit reccomendation to the isolate from the V8 the shell is set to."
							},
							"setmax":{
								"param":[("int","isolateId"),("int","heap size in bytes")],
								"method":self.setmax,
								"desc":"Set hard limit reccodendation to the isolate from the V8 the shell is set to."	
							},
							"run":{
								"param":[("str","script")],
								"method":self.runscript,
								"desc":"Run a JS script on the V8 the shell is set to."
							},
							"setMaxPlotters":{
								"param":[("int","max")],
								"method":self.monitor.setMaxPlotters,
								"desc":"Set maximum plotter windows allowed"
							},
							"loadConfig":{
								"param":[("str","configuration")],
								"method":self.p.ldConfig,
								"desc":"Load and apply configuration file"
							},
							"setPlotMode":{
								"param":[("str","mode")],
								"method":self.monitor.setPlotMode,
								"desc":"Set the plot mode: NONE,MACHINE,ISOLATE,ALL"
							},
							"setPlotServerPort":{
								"param":[("int","port")],
								"method":self.monitor.restartPlotterService,
								"desc":"Restart the plotter server on a different port"
							},
							"setMachineMemoryLimit":{
								"param":[("str","machine_id"),("int","memory_limit_in_MB")],
								"method":self.setMachineMemoryLimit,
								"desc":"Set the global memory limit for all JS instances per machine"
							},
							"setNewMachineMemoryLimit":{
								"param":[("int","memory_limit_in_MB")],
								"method":self.setNewMachineMemoryLimit,
								"desc":"Set the global memory limit for all JS instances for new machines that connect"
							},
							"setPlotterStartupConfig":{
								"param":[("str","JSON config")],
								"method":self.setPlotterStartupConfig,
								"desc":"Configure how the plotters behave, using a JSON string. This is applied to plotters created after this command is issued. options: makePNG(boolean) makeCSV(boolean)"
							},
							"policyname":{
								"param":[],
								"method":self.policyName,
								"desc":"Configure how the plotters behave, using a JSON string. This is applied to plotters created after this command is issued. options: makePNG(boolean) makeCSV(boolean)"
							},
							"policystats":{
								"param":[],
								"method":self.policyStats,
								"desc":"Configure how the plotters behave, using a JSON string. This is applied to plotters created after this command is issued. options: makePNG(boolean) makeCSV(boolean)"
							},
							"echo":{
								"param":[("int","0/1 off/on")],
								"method":self.toggleEcho,
								"desc":"Toggle echo function on or off"			
							},
							"registryIO":{
								"param":[],
								"method":self.getRegistryNetUsage,
								"desc":"Get a summary of the network usage on the registry side"
							},
							"testScenario":{
								"param":[("str","path_to_scenario"),("str","path_to_collect_in")],
								"method":self.runScenario,
								"desc":"Run a testing scenario"
							},
							"listScenarios":{
								"param":[],
								"method":self.listScenarios,
								"desc":"Show a listiong of all scenarios"	
							},
							"togglePlotServiceLogging":{
								"param":[("str","ON/OFF")],
								"method":self.togglePServiceLogging,
								"desc":"Toggle PlotService logging"	
							},
							"history":{
								"param":[],
								"method":self.printHistory,
								"desc":"Print command history"	
							},
							"listPolicies":{
								"param":[],
								"method":self.listPolicies,
								"desc":"List available policies"	
							}
						}

		self.shortForms = {
		"?":"help",
		"ldp":"loadpolicy",
		"ps":"policystats",
		"p?":"policyname",
		"pltsconf":"setPlotterStartupConfig",
		"hard":"setmax",
		"soft":"suggest",
		"h":"setmax",
		"s":"suggest",
		"plotport":"setPlotServerPort",
		"pp":"setPlotServerPort",
		"pmode":"setPlotMode",
		"pm":"setPlotMode",
		"nmlim":"setNewMachineMemoryLimit",
		"mlim":"setMachineMemoryLimit",
		"maxPlt":"setMaxPlotters",
		"mp":"setMaxPlotters",
		"r":"run",
		"conf":"loadConfig",
		"lc":"loadConfig",
		"rio":"registryIO",
		"r?":"registryIO",
		"scenario":"testScenario",
		"scen":"testScenrio",
		"t":"testScenario",
		"rs":"testScenario",
		"tpsl":"togglePlotServiceLogging",
		"pslog":"togglePlotServiceLogging",
		"ls":"listScenarios",
		"lscen":"listScenarios",
		"listscen":"listScenarios",
		"h":";history",
		"lsp":"listPolicies",
		"m":"machines",
		"v":"v8s"
		}
#TODO - screenshot all frames, stop plotter, stop all plotters