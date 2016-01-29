from threading import *
from PlotService import *
#threadsafe

class monitor:
    def __init__(self,plotMode):
        self.STATUS = {"machines":{}};
        self.FreeMachineIDS = list();
        self.lock = RLock();

        #PLOT MODES: 0 - NO PLOTTING, 1 - PLOT PER MACHINE ONLY, 2 - PLOT PER ISOLATE ONLY, 3 - PLOT PER ISOLATE AND PER MACHINE
        self.plotMode = 0;
        self.setPlotMode(plotMode);

        self.plotter = PlotService(["heap","available","maxHeapSize"]);

        self.plotter.init();

    def setPlotMode(self,mode):
        if mode == "NONE":
            self.plotMode = 0;
        
        if mode == "MACHINE":
            self.plotMode = 1;
        
        if mode == "ISOLATE":
            self.plotMode = 2;

        if mode == "ALL":
            self.plotMode = 3;

    def close(self):
        self.plotter.stop();

    def takeSnapshot(self,m,v,i):
        self.plotter.takeSnapshot("Machine_"+m+"_V8_"+str(v)+"_isl_"+str(i));

    def getAppropriateId(self,FreeList,alternate):
        self.lock.acquire();

        id = len(FreeList);
        if len(FreeList) > 0:
            id = FreeList[0];
            FreeList.pop();
        else:
            id = alternate + 1;

        self.lock.release();
        return id;

    def addMachine(self,id):
        id = str(id)
        machine = {"FreeList":list(),"v8s":dict(),"id":"0"};
        machine["id"] = id;
        
        self.lock.acquire();
        if id in self.STATUS["machines"].keys():
            id = 0;
        else:
            self.STATUS["machines"][id] = machine;
            
        self.lock.release();

        return id;

    def removeMachine(self,machineId):
        self.lock.acquire();
        machines = self.STATUS["machines"];

        mid = 0;
        if machineId in machines:
            del machines[machineId];
            self.FreeMachineIDS.append(machineId);
            mid = machineId;
            
        self.lock.release();
        return mid;

    def getMachine(self,machineId):
        machineId = str(machineId)

        retval = 0;
        
        self.lock.acquire();
        try:
            retval = self.STATUS["machines"][machineId]
        except Exception as e:
            retval = 0;
        self.lock.release();

        return retval;

    def addV8(self,machineId,communicator):
        machine = self.getMachine(machineId);
        if machine == 0:
            return 0;

        self.lock.acquire();
        freeIDs = machine["FreeList"];
        v8 = {"FreeList":list(),"isolates":dict(),"id":0};

        id = self.getAppropriateId(freeIDs,len(machine["v8s"].keys()));
    
        v8["id"] = id;
        v8["comm"] = communicator;
        machine["v8s"][id] = v8;
        
        self.lock.release();
        return id;

    def getV8(self,machine,v8id):
        retval = 0;

        self.lock.acquire();
        try:
            retval = machine["v8s"][v8id]
        except Exception as e:
            retval = 0;
        self.lock.release();

        return retval;

    def getV8Comm(self,machineId,v8Id):
        v8 = self.getV8(self.getMachine(machineId),v8Id);
        if v8 == 0:
            return 0;

        return v8["comm"];

    def removeV8(self,machineId,v8Id):
        machine = self.getMachine(machineId);
        if machine == 0:
            return 0;

        v8 = self.getV8(self.getMachine(machineId),v8Id)
        if v8 == 0:
            return 0;

        with self.lock:
            id = v8["id"]
            del machine["v8s"][id];
            
            #no more V8s for this machine, delete machine
            if len(machine["v8s"].keys()) == 0:
                self.removeMachine(machineId);

        if self.plotMode > 0:
            self.plotter.update("Machine_"+machineId+"_V8_"+str(v8Id),{"action":"died"});
        
        return id;

    def addIsolate(self,machineId,v8Id):
        v8 = self.getV8(self.getMachine(machineId),v8Id)
        if v8 == 0:
            return 0;

        self.lock.acquire();
        freeIDs = v8["FreeList"];
        isolate = {"id":0};

        id = self.getAppropriateId(freeIDs,len(v8["isolates"].keys()));
        isolate["id"] = id;
        v8["isolates"][id] = isolate;
        
        self.lock.release();
        return id;

    def getIsolate(self,machineId,v8Id,isolateId):
        v8 = self.getV8(self.getMachine(machineId),v8Id)
        if v8 == 0:
            return 0;

        self.lock.acquire();
        retval = 0;
        if isolateId in v8["isolates"]:
            retval = v8["isolates"][isolateId];
        self.lock.release();

        return retval;

    def removeIsolate(self,machineId,v8Id,isolateId):
        v8 = self.getV8(self.getMachine(machineId),v8Id)
        if v8 == 0:
            return 0;

        retval = 0;

        self.lock.acquire();
        if isolateId in v8["isolates"]:
            del v8["isolates"][isolateId];
            retval = isolateId;
        self.lock.release();

        if self.plotMode > 1:
            self.plotter.update("Machine_"+machineId+"_V8_"+str(v8Id)+"_isl_"+str(isolateId),{"action":"died"});
        
        return retval;

    def getIsolateCount(self,machineId,v8Id):
        v8 = self.getV8(self.getMachine(machineId),v8Id)
        if v8 == 0:
            return 0;
        else:
            self.lock.acquire();
            ln = len(v8["isolates"].keys());
            self.lock.release();
            return ln;

    def aggregateMachineInfo(self,machineId):
        if self.plotMode == 0 or self.plotMode == 2:
            return;

        with self.lock:
            aggregateFields = [];
            aggregateValues = {};

            machine = self.getMachine(machineId);
            if machine == 0:
                return;

            for v8 in machine:
                for i in v8["isolates"]:
                    isolate = v8["isolates"][i];
                    items = "("+str(isolate["id"])+") ";
                    firstTime = (len(aggregateFields) == 0)
                    for item in isolate:
                        if firstTime and isinstance( x, int ):
                            aggregateFields.append(item);
                        elif item in aggregateFields:
                            aggregateValues[item] = aggregateValues[item] + isolate[item]; 
        
        self.plotter.update("Machine_"+machineId+"_aggregate",{"values":aggregateValues,"labels":aggregateFields});

    def isolateUpdate(self,machineId,v8Id,isolateId,info):
        isolate = self.getIsolate(machineId,v8Id,isolateId);
        if isolate == 0:
            return;

        self.lock.acquire();
        if info["action"] == "update":
            for key in info:
                isolate[key] = info[key];
        
        if self.plotMode == 3:
            self.plotter.update("Machine_"+machineId+"_V8_"+str(v8Id)+"_isl_"+str(isolateId),info);
        
        self.lock.release();

        self.aggregateMachineInfo(machineId)

    def update(self,machineId,v8Id,response):
        nris = response["TotalIsolates"];
        recordedIsolateCount = self.getIsolateCount(machineId,v8Id)

        #adjust isolate count
        while nris > recordedIsolateCount:
            self.addIsolate(machineId,v8Id);
            recordedIsolateCount += 1;
        while recordedIsolateCount > nris:
            recordedIsolateCount -= 1;
            self.removeIsolate(machineId,v8Id,recordedIsolateCount);

        #update isolate status
        for i in range(1,nris+1):
            info = response["isolates"][str(i)];
            self.isolateUpdate(machineId,v8Id,i,info)

    def prettyPrintV8(self,machineId,v8Id,spaces):
        self.lock.acquire();
        v8 = self.getV8(self.getMachine(machineId),v8Id);
        if(v8 == 0):
            print spaces+"Could not find v8 instance";
            return;

        for i in v8["isolates"]:
            isolate = v8["isolates"][i];
            items = "("+str(isolate["id"])+") ";
            for item in isolate:
                if item != "action" and item != "id":
                    items += str(item)+":"+str(isolate[item])+" "
            print spaces+items;
            print "_"*45

        self.lock.release();
    
    def prettyPrint(self):
        self.lock.acquire();
        for id in self.STATUS["machines"]:
            machine = self.STATUS["machines"][id]["v8s"];
            print "MACHINE_"+str(id);
            for v8 in machine:
                print " V8_"+str(v8);
                self.prettyPrintV8(id,v8," "*2);

        self.lock.release();

    def debug(self):
        print self.STATUS;

    def acquire(self):
        self.lock.acquire();
    def release(self):
        self.lock.release();
    #WARNING, you must lock the mutex before calling this and while using the result
    def getRegistry(self):
        return self.STATUS["machines"];

    def listCommunicators(self):
        self.lock.acquire();
        comm = []
        for idd in self.STATUS["machines"]:
            machine = self.STATUS["machines"][idd]['v8s'];
            for key in machine:
                #returns communicator, machineId, v8Id
                comm.append([machine[key]["comm"],idd,key]);
        self.lock.release();
        return comm;