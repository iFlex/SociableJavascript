from threading import *
from PlotService import *
import copy

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
    #NOT THREAD SAGFE, NEEDS TO BE CALLED WHILE LOCK IS HELD
    def getAppropriateId(self,FreeList,alternate):
        id = len(FreeList);
        if len(FreeList) > 0:
            id = FreeList[0];
            FreeList.pop();
        else:
            id = alternate + 1;

        return id;

    def addMachine(self,id):
        id = str(id)
        machine = {"FreeList":list(),"v8s":dict(),"id":"0"};
        machine["id"] = id;
        with self.lock:
            if id in self.STATUS["machines"].keys():
                id = 0;
            else:
                self.STATUS["machines"][id] = machine;
        return id;

    def removeMachine(self,machineId):
        with self.lock:
            machines = self.STATUS["machines"];

            mid = 0;
            if machineId in machines:
                del machines[machineId];
                self.FreeMachineIDS.append(machineId);
                mid = machineId;
                print "RemovedMachine"+machineId
        return mid;

    def getMachine(self,machineId):
        machineId = str(machineId)

        retval = 0;
        
        with self.lock:
            try:
                retval = self.STATUS["machines"][machineId]
            except Exception as e:
                retval = 0;

        return retval;

    def addV8(self,machineId,communicator):
        machine = self.getMachine(machineId);
        if machine == 0:
            return 0;

        with self.lock:
            freeIDs = machine["FreeList"];
            v8 = {"FreeList":list(),"isolates":dict(),"id":0};

            id = self.getAppropriateId(freeIDs,len(machine["v8s"].keys()));
        
            v8["id"] = id;
            v8["comm"] = communicator;
            machine["v8s"][id] = v8;
        
        return id;

    def getV8(self,machine,v8id):
        retval = 0;

        with self.lock:
            try:
                retval = machine["v8s"][v8id]
            except Exception as e:
                retval = 0;

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
            freeIDs = machine["FreeList"]
            freeIDs.append(v8Id);
            
            print "removed v8:"+machineId+"_"+str(v8Id);
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

        with self.lock:
            freeIDs = v8["FreeList"];
            isolate = {"id":0};

            id = self.getAppropriateId(freeIDs,len(v8["isolates"].keys()));
            isolate["id"] = id;
            v8["isolates"][id] = isolate;
        return id;

    def getIsolate(self,machineId,v8Id,isolateId):
        v8 = self.getV8(self.getMachine(machineId),v8Id)
        if v8 == 0:
            return 0;

        with self.lock:
            retval = 0;
            if isolateId in v8["isolates"]:
                retval = v8["isolates"][isolateId];

        return retval;

    def removeIsolate(self,machineId,v8Id,isolateId):
        v8 = self.getV8(self.getMachine(machineId),v8Id)
        if v8 == 0:
            return 0;

        retval = 0;
        with self.lock:
            if isolateId in v8["isolates"]:
                del v8["isolates"][isolateId];
                freeIDs = v8["FreeList"];
                freeIDs.append(isolateId)
                retval = isolateId;
                print "removed isolate:"+machineId+"_"+str(v8Id)+"_"+str(isolateId)
        if self.plotMode > 1:
            self.plotter.update("Machine_"+machineId+"_V8_"+str(v8Id)+"_isl_"+str(isolateId),{"action":"died"});
        
        return retval;

    def getIsolateCount(self,machineId,v8Id):
        v8 = self.getV8(self.getMachine(machineId),v8Id)
        if v8 == 0:
            return 0;
        else:
            with self.lock:
                return len(v8["isolates"].keys());

    def __aggregateMachineInfo(self,machineId):
        if self.plotMode == 0 or self.plotMode == 2:
            return;

        aggregateFields = [];
        aggregateValues = {};

        machine = self.getMachine(machineId);
        if machine == 0:
            return;

        v8s = machine["v8s"]
        for v8 in v8s:
            isolates = v8s[v8]["isolates"];
            for i in isolates:
                isolate = isolates[i];
                firstTime = (len(aggregateFields) == 0)
                for item in isolate:
                    if firstTime and isinstance( isolate[item], int ):
                        aggregateFields.append(item);
                        aggregateValues[item] = isolate[item]
                    elif item in aggregateFields:
                        aggregateValues[item] = aggregateValues[item] + isolate[item]; 

        self.plotter.update("Machine_"+machineId+"_aggregate",aggregateValues);

    #NOT THREAD SAFE, MEANT TO BE CALLED FROM WITHIN update() only
    def __isolateUpdate(self,machineId,v8Id,isolateId,info):
        isolate = self.getIsolate(machineId,v8Id,isolateId);
        if isolate == 0:
            return;

        if info["action"] == "update":
            for key in info:
                isolate[key] = info[key];
            
        if self.plotMode == 3:
            self.plotter.update("Machine_"+machineId+"_V8_"+str(v8Id)+"_isl_"+str(isolateId),info);

        

    def update(self,machineId,v8Id,response):
        with self.lock:
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
                self.__isolateUpdate(machineId,v8Id,i,info)
            
            self.__aggregateMachineInfo(machineId)


    def __prettyPrintV8(self,machineId,v8Id,spaces):        
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

    def prettyPrint(self):
        with self.lock:
            for id in self.STATUS["machines"]:
                machine = self.STATUS["machines"][id]["v8s"];
                print "MACHINE_"+str(id);
                for v8 in machine:
                    print " V8_"+str(v8);
                    self.__prettyPrintV8(id,v8," "*2);

    def debug(self):
        print self.STATUS;
 
    def listCommunicators(self):
        comm = []
        with self.lock:
            for idd in self.STATUS["machines"]:
                v8s = self.STATUS["machines"][idd]['v8s'];
                for key in v8s:
                    #returns communicator, machineId, v8Id
                    comm.append([v8s[key]["comm"],idd,key]);

        return comm;