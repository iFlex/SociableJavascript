from Communication.requestbuilder import *
from cli import *
from csv import *

from threading import Thread
import time;
import imp
import os
import sys, traceback
import types
        
#todo: implement checks for policy output
class Policy:

    def __init__(self,monitor,frequency,cfgfile):
        self.monitor = monitor;
        self.interval = 1;
        self.changeSamplingFrequency(frequency)
        self.requestBldr = RequestBuilder(monitor)
        self.keepRunning = True;
        self.cli = CommandLine(self);
        
        print "Loading default policy..."
        self.policyDefault = "./Policies/robinhood.py" #"./Policies/default.py"
        self.policy = self.__loadModule(self.policyDefault);
        if self.policy == 0:
            print "Could not load default policy. You will need to load one manually using the command line";

        #load default config
        self.ldConfig(cfgfile)
        self.bytesInMb = 1024*1024

        logpath = "./out/logs/"
        if not os.path.exists(logpath):
            os.makedirs(logpath)
        self.log = open(logpath+"policy.log","a");
        
        #starting cli
        print " Starting policy & updater thred...";
        self.thread = Thread(target = self.run)
        self.thread.daemon = True
        self.thread.start();
        print "  Starting cli...";
        self.cli.run();
        print "Stopping policy...";
        self.log.close()

        self.keepRunning = False;
        self.thread.join();

        print "Closing communicators...";
        comms = self.monitor.listCommunicators();
        for comm in comms:
            comm[0].close();
        print "Cleanup finished. Exiting...";

    def ldConfig(self,fileN):
        print "Loading configuration"+"_"*55
        fileN = "./Configuration/"+fileN
        try:
            with open(fileN) as f:
                content = f.readlines()
                for line in content:
                    self.cli.execute(line)
        except IOError as e:
            pass
        except Exception as e:
            print "Error while loading configuration..."+str(e)
        print "_"*80

    def changeSamplingFrequency(self,hz):
        if hz <= 0:
            hz = 1

        if(hz > 60000): #60KHz
            hz = 60000;

        if(hz < 0.01):
            hz = 0.01
            
        self.interval = 1.0/hz;
        return hz;

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
        except Exception as e:
            print "Error loading policy "+filepath+" "+str(e)
            py_mod = 0;

        return py_mod

    def loadPolicy(self,policyName):
        print "Loading policy "+policyName;
        self.policy = self.__loadModule("./Policies/"+policyName);
        
        if self.policy == 0:
            print "Reverting to default policy...";
            self.policy = self.__loadModule(self.policyDefault);
        else:
            print "LOADED"

    def logPolicyInfo(self,name,msg):
        logtime = str(time.strftime("%Y/%m/%d-%H:%M:%S"))
        self.log.write("\n"+logtime+"["+name+"]"+msg)

    def validateSuggestions(self,suggestions,maxMachineMemory):
        if not isinstance(suggestions, types.ListType):
            self.logPolicyInfo(self.policy.name(),"INVALID_RESPONSE:"+str(suggestions));
            return False

        sm = 0
        ss = 0
        for s in suggestions:
            if "hardHeapLimit" in s and s["hardHeapLimit"] > maxMachineMemory:
                sm += s["hardHeapLimit"]
                self.logPolicyInfo(self.policy.name(),"ALLOC_ERROR: GIVEN="+str(s["hardHeapLimit"])+" MACHINE_MAX="+str(maxMachineMemory));
                return False

            if "softHeapLimit" in s and "hardHeapLimit" in s and s["softHeapLimit"] > s["hardHeapLimit"]:
                ss += s["softHeapLimit"]
                self.logPolicyInfo(self.policy.name(),"SOFT_LIM_ERROR: SOFT="+str(s["softHeapLimit"])+" HARD="+str(s["hardHeapLimit"]));
                return False
        
        if sm > maxMachineMemory:
            self.logPolicyInfo(self.policy.name(),"TOTAL_ALLOC_ERROR GIVEN="+str(sm)+" MACHINE_MAX="+str(maxMachineMemory));         
            #return False
        
        return True

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
                    inspectionList = []
        
                    for v8 in v8s:
                        comm = v8s[v8]["comm"];
                        requestQ.append((comm,self.requestBldr.statusReport(idd,v8)))
                        
                        #apply policy
                        if not (self.policy == 0):
                            isolates = v8s[v8]["isolates"];
                        
                            for i in isolates:
                                isolates[i]["v8Id"] = v8;
                                inspectionList.append(isolates[i])

                    #init policy state store per machine
                    if "policy_store" not in machine:
                        machine["policy_store"] = {"csvlog":CSV(self.policy.name()+".csv")}
                        self.policy.init(machine["policy_store"]);
                    
                    if len(inspectionList) == 0:
                        continue
                    
                    suggestions = []
                    try:
                        suggestions = self.policy.calculate(machine["memoryLimit"],inspectionList,machine["policy_store"]);
                    except Exception as e:
                        self.logPolicyInfo(self.policy.name(),"POLICY_ERROR ERROR="+str(e)+" TRACEBACK:");
                        traceback.print_exc(file=self.log)
                        print "POLICY_ERROR";
                        continue

                    if self.validateSuggestions(suggestions,machine["memoryLimit"]):
                        #this could become slow if frequencies are high
                        #self.logPolicyInfo(self.policy.name(),"DECISION="+str(suggestions));
                        for suggestion in suggestions:
                            if "hardHeapLimit" in suggestion:
                                request  = self.requestBldr.setMaxHeapSize(idd,suggestion["v8Id"],suggestion["id"],suggestion["hardHeapLimit"]/self.bytesInMb,0);
                                requestQ.append((self.monitor.getV8Comm(idd,suggestion["v8Id"]),request))
                            
                            if "softHeapLimit" in suggestion: 
                                request2 = self.requestBldr.recommendHeapSize(idd,suggestion["v8Id"],suggestion["id"],suggestion["softHeapLimit"]/self.bytesInMb,0)
                                requestQ.append((self.monitor.getV8Comm(idd,suggestion["v8Id"]),request2))
                                    
            while len(requestQ) > 0:
                comm,request = requestQ.pop()
                comm.send(request);

        print "#POLICY POLLER EXITING...";
