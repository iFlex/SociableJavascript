from requestbuilder import *
from cli import *
from threading import Thread
import time;
import imp
import os
import sys, traceback

class Policy:
    def __init__(self,monitor,frequency):
        self.monitor = monitor;
        self.interval = 1;
        self.changeSamplingFrequency(frequency)
        self.requestBldr = RequestBuilder(monitor)
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

    def changeSamplingFrequency(self,hz):
        if hz <= 0:
            hz = -hz

        intvl = 1.0/hz;
        if intvl < 0.05:
            return False;
        
        self.interval = intvl
        return True;

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
        reg  = {}
        requestQ = []
        #keep polling and applying policy
        while(self.keepRunning):
            time.sleep(self.interval);
            
            with self.monitor.lock:    
                reg = self.monitor.STATUS["machines"];

                for idd in reg:
                    machine = reg[idd]
                    v8s = machine["v8s"];
                    for v8 in v8s:
                        comm = v8s[v8]["comm"];
                        requestQ.append((comm,self.requestBldr.statusReport(idd,v8)))
                        
                        #apply policy
                        if not (self.policy == 0):
                            isolates = v8s[v8]["isolates"];
                            
                            suggestions = []
                            try:
                                suggestions = self.policy.calculate(1024,isolates);
                                if len(suggestions) == 0:
                                    continue
                            except Exception as e:
                                print "Ploicy error:"+str(e)
                                traceback.print_exc(file=sys.stdout)
                                continue

                            for suggestion in suggestions:
                                request  = self.requestbuilder.setMaxHeapSize(idd,v8,suggestion["id"],suggestion["hardHeapLimit"]);
                                request2 = self.requestbuilder.recommendHeapSize(idd,v8,suggestion["id"],suggestedHeapSize,suggestion["softHeapLimit"])
                                requestQ.append((comm,request))
                                requestQ.append((comm,request2))
                                
            while len(requestQ) > 0:
                comm,request = requestQ.pop()
                comm.send(request);

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
