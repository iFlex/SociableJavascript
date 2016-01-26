import sys, traceback

class CommandLine:
	def __init__(self,policy):
		self.p = policy;
		self.monitor = self.p.monitor;

	def run(self):
		machine_id = "not_set";
		v8_id      = "not_set";
		while True:
			cmd = raw_input(">");
			cmd = cmd.split(" ");
			try:
				if cmd[0] == "exit":
				   break;
				
				elif cmd[0] == "stats" or len(cmd[0]) == 0:
				   self.monitor.prettyPrint();
				
				elif cmd[0] == "dbg":
				   self.monitor.debug();
				
				elif cmd[0] == "where":
					print "@ Machine_"+str(machine_id)+" V8_"+str(v8_id);
				
				elif cmd[0] == "chv8":
					if len(cmd) < 2:
						print "Usage: chv8 V8_id"
					else:
						v8_id      = int(cmd[1]);

				elif cmd[0] == "switch":
					if len(cmd) < 3:
						print "Usage: switch machine_id V8_id"
					else:
						machine_id = cmd[1];
						v8_id      = int(cmd[2]);

				elif cmd[0] == "changePlotFocus" or cmd[0] == "cpf":
					if len(cmd) < 2:
						print "Usage: changePlotFocus isolateId"
					else:
						isl = int(cmd[1]);
						self.monitor.changeMonitoredIsolate(machine_id,v8_id,isl);
				
				elif cmd[0] == "snapshot":
					self.monitor.takeSnapshot();

				elif cmd[0] == "poll":
					comms = self.monitor.getCommunicators();
					for id in comms:
						machine = comms[id];
						for v8 in machine:
							machine[v8].send(self.p.requestBldr.statusReport(machine_id,v8_id));

				elif cmd[0] == "suggest":
					if len(cmd) < 3:
						print "Usage: suggest isolateId heap_size";
					else:
						comm = self.monitor.getV8Comm(machine_id,v8_id);
						comm.send(self.p.requestBldr.recommendHeapSize(machine_id,v8_id,int(cmd[1]),int(cmd[2]),0));
				
				elif cmd[0] == "setmax":
					if len(cmd) < 3:
						print "Usage: setmax isolateId max_heap_size";
					else:
						comm = self.monitor.getV8Comm(machine_id,v8_id);
						comm.send(self.p.requestBldr.setMaxHeapSize(machine_id,v8_id,int(cmd[1]),int(cmd[2]),0));

				elif cmd[0] == "kill":
					if len(cmd) < 2:
						print "Usage: kill isolateId";
					else:
						comm = self.monitor.getV8Comm(machine_id,v8_id);
						comm.send(self.p.requestBldr.terminate(machine_id,v8_id,int(cmd[1]),0));

				elif cmd[0] == "run":
					if len(cmd) < 2:
						print "Usage: run script_path";
					else:
						comm = self.monitor.getV8Comm(machine_id,v8_id);
						comm.send(self.p.requestBldr.startScript(machine_id,v8_id,cmd[1]));

				elif len(cmd[0]) > 0:
					print "Unknown command '"+cmd[0]+"'";
			
			except Exception as e:
				print "* CLI ERROR:"+str(e);
				traceback.print_exc(file=sys.stdout)

			self.p.keepRunning = False	
			