from requestbuilder import *
from cli import *
from threading import Thread
import time;

class Policy:
    def __init__(self,monitor,preloadScripts):
        self.monitor = monitor;
        self.interval = 1;#seconds
        self.requestBldr = RequestBuilder(monitor);
        self.keepRunning = True;
        self.cli = CommandLine(self);
        #preloading scripts
        #for script in preloadScripts:
        #  print "Preloading:"+script;
        #  communicator.send(self.requestBldr.startScript(1,script));
        
        #starting cli
        print "Starting default policy...";
        self.thread = Thread(target = self.run)
        self.thread.start();
        print "Starting cli...";
        self.cli.run();
        print "Stopping policy...";

        self.keepRunning = False;
        self.thread.join();
        print "Closing communicators...";
        comms = self.monitor.getCommunicators();
        for id in comms:
            machine = comms[id];
            for v8 in machine:
                machine[v8].close();
        print "Cleanup finished. Exiting...";

    #at the moment this deadlocks, somehow
    def run(self):
        #keep calculating
        while(self.keepRunning):
            time.sleep(self.interval);
            #print "Polling..."
            comms = self.monitor.getCommunicators();
            for id in comms:
                machine = comms[id];
                for v8 in machine:
                    machine[v8].send(self.requestBldr.statusReport(id,v8));
