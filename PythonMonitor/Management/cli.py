import sys, traceback
import os
import json

class CommandLine:
	
	def __init__(self,policy):
		self.p = policy;
		self.monitor = self.p.monitor;
		self.echo = True
		self.initCmds()
	
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
			
			sf = self.getCommandShortForms(key)
			if len(sf) > 0:
				print "   "+self.listNiceFormat(sf," ")
			
			if "desc" in self.commands[key]:
				print "     "+self.commands[key]["desc"]
				print ""

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
			
			self.execute(cmd);

		self.p.keepRunning = False

	def prettyPrint(self):
		os.system('cls')
		os.system('clear');
		self.monitor.prettyPrint(self.machine_id,self.v8_id)

	def chhz(self,hz):
		print "Changed frequency:"+str(self.p.changeSamplingFrequency(hz))+" @ "+str(1/self.p.interval)+"Hz";

	def where(self):
		print "@ Machine_"+str(self.machine_id)+" V8_"+str(self.v8_id);

	def chv8(self,id):
		self.v8_id = id;

	def switch(self,m,v):
		self.machine_id = m;
		self.v8_id = v;
		self.where()

	def takeSnapshot(self,iid):
		self.monitor.takeSnapshot(self.monitor_id,self.v8_id,iid);

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
		self.monitor.newMachineMemoryLimit = limit;

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
							"stats":{
								"param":[],
								"method":self.prettyPrint,
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
							}
						}

		self.shortForms = {
		"?":"help",
		"ldp":"loadpolicy",
		"ps":"policystatus",
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
		"lc":"loadConfig"
		}
#TODO - screenshot all frames, stop plotter, stop all plotters