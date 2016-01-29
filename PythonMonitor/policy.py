from requestbuilder import *
from cli import *
from threading import Thread
import time;
import imp
import os

class Policy:
    def __init__(self,monitor):
        self.monitor = monitor;
        self.interval = 0.25;#every 1/100 of a second - realtime plotting
        self.requestBldr = RequestBuilder(monitor);
        self.keepRunning = True;
        self.cli = CommandLine(self);
        
        print "Loading default policy..."
        self.policyDefault = "./policies/default.py"
        self.policy = self.__loadModule(self.policyDefault);
        if self.policy == 0:
            print "Could not load default policy. You will need to load one manually using the command line";
        else:
            self.policy.init();

        #starting cli
        print " Starting policy & updater thred...";
        self.thread = Thread(target = self.run)
        self.thread.daemon = True
        self.thread.start();
        print "  Starting cli...";
        self.cli.run();
        print "Stopping policy...";

        self.keepRunning = False;
        self.thread.join();

        print "Closing communicators...";
        comms = self.monitor.listCommunicators();
        for comm in comms:
            comm[0].close();
        print "Cleanup finished. Exiting...";

    def __loadModule(self,filepath):
        mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])

        py_mod = 0;
        try:

            if file_ext.lower() == '.pyc':
                py_mod = imp.load_compiled(mod_name, filepath)
            else:
                if not file_ext.lower() == '.py':
                    filepath += '.py';
                py_mod = imp.load_source(mod_name, filepath)

            print "Module functions:"+str(dir(py_mod));
        except Exception as e:
            print "Error loading policy "+filepath+" "+str(e)
            py_mod = 0;

        return py_mod

    def loadPolicy(self,policyName):
        print "Loading policy "+policyName;
        self.policy = self.__loadModule("./policies/"+policyName);
        
        if self.policy == 0:
            print "Reverting to default policy...";
            self.policy = self.__loadModule(self.policyDefault);

    #at the moment this deadlocks, somehow
    def run(self):
        comms  = {}

        #keep polling and applying policy
        while(self.keepRunning):
            time.sleep(self.interval);
            
            self.monitor.acquire()
            reg = self.monitor.getRegistry()    
            for idd in reg:
                machine = reg[idd]
                v8s = machine['v8s'];
                for v8 in v8s:
                    comm = v8s[v8]["comm"];
                    comm.send(self.requestBldr.statusReport(idd,v8));

                    isolates = v8s[v8]["isolates"];
                    
                    #apply policy
                    if not (self.policy == 0):
                        suggestions = self.policy.calculate(machine,isolates);
                        for suggestion in suggestions:
                            request = self.requestbuilder.setMaxHeapSize(idd,v8,suggestion["id"],suggestion["hardHeapLimit"]);
                            comm.send(request);
                            comm.send(self.requestbuilder.recommendHeapSize(idd,v8,suggestion["id"],suggestedHeapSize,suggestion["softHeapLimit"]));

            self.monitor.release();
            #print "Polling..."
            '''comms = self.monitor.getCommunicators(comms);
            for id in comms:
                machine = comms[id];
                for v8 in machine:
                    machine[v8].send(self.requestBldr.statusReport(id,v8));

                    #apply policy
                    if not (self.policy == 0):
                        maxHeapSize,suggestedHeapSize = self.policy.calculate();
                    #    machine[v8].send(self.requestbuilder.setMaxHeapSize(id,v8,isl,maxHeapSize));
                    #    machine[v8].send(self.requestbuilder.recommendHeapSize(id,v8,isl,suggestedHeapSize));
            '''
        print "#POLICY POLLER EXITING...";
