from requestbuilder import *
from cli import *
from threading import Thread
import time;

class Policy:
    def __init__(self,communicator,monitor,preloadScripts):
        self.comm = communicator;
        self.monitor = monitor;
        self.interval = 1;#seconds
        self.requestBldr = RequestBuilder(monitor);
        self.keepRunning = True;
        self.cli = CommandLine(self);
        #preloading scripts
        for script in preloadScripts:
          print "Preloading:"+script;
          communicator.send(self.requestBldr.startScript(1,script));
        
        #starting cli
        print "Starting default policy...";
        self.thread = Thread(target = self.run)
        #self.thread.start();
        print "Starting cli...";
        self.cli.run();
        print "Stopping policy...";
        self.thread.join();
        print "Closing connection...";
        communicator.close();
        print "Cleanup finished. Exiting...";

    def run(self):
        #keep calculating
        while(self.keepRunning):
            time.sleep(self.interval);
            self.comm.send(self.requestBldr.statusReport(1));   
