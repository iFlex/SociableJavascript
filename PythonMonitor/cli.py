import sys, traceback

class CommandLine:
	def __init__(self,policy):
		self.p = policy;
		self.monitor = self.p.monitor;

	def run(self):
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

				elif cmd[0] == "poll":
					comms = self.monitor.getCommunicators();
					for id in comms:
						machine = comms[id];
						for v8 in machine:
							machine[v8].send(self.p.requestBldr.statusReport(id));

				elif cmd[0] == "suggest":
					if len(cmd) < 4:
						print "Usage: suggest machineId isolateId heap_size";
					else:
						comm = self.monitor.getV8Comm(int(cmd[1]),int(cmd[2]));
						comm.send(self.p.requestBldr.recommendHeapSize(int(cmd[1]),int(cmd[2]),int(cmd[3]),0));
				
				elif cmd[0] == "set_ceiling":
					if len(cmd) < 4:
						print "Usage: set_ceiling machineId isolateId max_heap_size";
					else:
						comm = self.monitor.getV8Comm(int(cmd[1]),int(cmd[2]));
						comm.send(self.p.requestBldr.setMaxHeapSize(int(cmd[1]),int(cmd[2]),int(cmd[3]),0));

				elif cmd[0] == "kill":
					if len(cmd) < 3:
						print "Usage: kill machineId isolateId";
					else:
						comm = self.monitor.getV8Comm(int(cmd[1]),int(cmd[2]));
						comm.send(self.p.requestBldr.terminate(int(cmd[1]),int(cmd[2]),0));

				elif cmd[0] == "run":
					if len(cmd) < 4:
						print "Usage: run machineId v8id script_path";
					else:
						comm = self.monitor.getV8Comm(int(cmd[1]),int(cmd[2]));
						comm.send(self.p.requestBldr.startScript(int(cmd[1]),cmd[3]))

				elif len(cmd[0]) > 0:
					print "Unknown command '"+cmd[0]+"'";
			
			except Exception as e:
				print "* CLI ERROR:"+str(e);
				traceback.print_exc(file=sys.stdout)

			self.p.keepRunning = False	
			