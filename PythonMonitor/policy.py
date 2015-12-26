from requestbuilder import *
from threading import Thread
from time import sleep
import time;

class Policy:
    def __init__(self,communicator,monitor):
        self.comm = communicator;
        self.monitor = monitor;
        self.interval = 1;#seconds
        self.requestBldr = RequestBuilder(monitor);
        self.keepRunning = True;

        self.thread = Thread(target = self.run)
        print "Starting default policy...";
        self.thread.start();
        print "Starting cli...";
        self.cli();
        print "Stopping policy...";
        self.thread.join();
        print "Closing connection...";
        communicator.close();
        print "Cleanup finished. Exiting...";

    def run(self):
        #get an initial status report
        self.comm.send(self.requestBldr.statusReport(1));
        #keep calculating
        print "KeepRunning:"+str(self.keepRunning);
        while(self.keepRunning):
            time.sleep(self.interval);
            self.comm.send(self.requestBldr.statusReport(1));

    def cli(self):
       while True:
           cmd = raw_input(">");
           cmd = cmd.split(" ");

           if cmd[0] == "exit":
               break;

           elif cmd[0] == "stats":
               self.monitor.debug();

           elif cmd[0] == "suggest":
               if len(cmd) < 4:
                   print "Usage: suggest machineId isolateId heap_size";
               else:
                   self.comm.send(self.requestBldr.recommendHeapSize(int(cmd[1]),int(cmd[2]),int(cmd[3]),0));
           elif cmd[0] == "set_ceiling":
              if len(cmd) < 4:
                  print "Usage: set_ceiling machineId isolateId max_heap_size";
              else:
                  self.comm.send(self.requestBldr.setMaxHeapSize(int(cmd[1]),int(cmd[2]),int(cmd[3]),0));

           elif cmd[0] == "kill":
              if len(cmd) < 3:
                  print "Usage: kill machineId isolateId";
              else:
                  self.comm.send(self.requestBldr.terminate(int(cmd[1]),int(cmd[2]),0));
           else:
               print "Unknown command '"+cmd[0]+"'";

       self.keepRunning = False
