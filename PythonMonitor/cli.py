class CommandLine:
	def __init__(self,policy):
		self.p = policy;

	def run(self):
		while True:
			cmd = raw_input(">");
			cmd = cmd.split(" ");

			if cmd[0] == "exit":
			   break;

			elif cmd[0] == "stats" or len(cmd[0]) == 0:
			   self.p.monitor.prettyPrint();
			elif cmd[0] == "dbg":
			   self.p.monitor.debug();

			elif cmd[0] == "poll":
			   self.p.comm.send(self.p.requestBldr.statusReport(1));		
			
			elif cmd[0] == "suggest":
			   if len(cmd) < 4:
			       print "Usage: suggest machineId isolateId heap_size";
			   else:
			       self.p.comm.send(self.p.requestBldr.recommendHeapSize(int(cmd[1]),int(cmd[2]),int(cmd[3]),0));
			elif cmd[0] == "set_ceiling":
			  if len(cmd) < 4:
			      print "Usage: set_ceiling machineId isolateId max_heap_size";
			  else:
			      self.p.comm.send(self.p.requestBldr.setMaxHeapSize(int(cmd[1]),int(cmd[2]),int(cmd[3]),0));

			elif cmd[0] == "kill":
			  if len(cmd) < 3:
			      print "Usage: kill machineId isolateId";
			  else:
			      self.p.comm.send(self.p.requestBldr.terminate(int(cmd[1]),int(cmd[2]),0));

			elif cmd[0] == "run":
			  if len(cmd) < 3:
			      print "Usage: run machineId script_path";
			  else:
			      self.p.comm.send(self.p.requestBldr.startScript(int(cmd[1]),cmd[2]))

			elif len(cmd[0]) > 0:
			   print "Unknown command '"+cmd[0]+"'";

			self.p.keepRunning = False	