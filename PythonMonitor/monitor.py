from threading import *

#threadsafe

class monitor:
    def __init__(self):
        self.STATUS = {"machines":{}};
        self.FreeMachineIDS = list();
        self.lock = RLock();

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

    def addMachine(self,socket):
        machine = {"FreeList":list(),"v8s":dict(),"id":0};

        id = self.getAppropriateId(self.FreeMachineIDS,len(self.STATUS["machines"].keys()));
        machine["id"] = id;
        
        self.lock.acquire();
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
        retval = 0;
        
        self.lock.acquire();
        try:
            retval = self.STATUS["machines"][machineId]
        except Exception as e:
            retval = 0;
        self.lock.release();

        return retval;

    def addV8(self,machineId):
        machine = self.getMachine(machineId);
        if machine == 0:
            return 0;

        self.lock.acquire();
        freeIDs = machine["FreeList"];
        v8 = {"FreeList":list(),"isolates":dict(),"id":0};

        id = self.getAppropriateId(freeIDs,len(machine["v8s"].keys()));
        v8["id"] = id;
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


    def removeV8(self,machineId,v8Id):
        machine = self.getMachine(machineId);
        if machine == 0:
            return 0;

        v8 = self.getV8(self.getMachine(machineId),v8id)
        if v8 == 0:
            return 0;

        self.lock.acquire();
        id = v8["id"]
        del machine["v8s"][id];
        self.lock.release();

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

    def isolateUpdate(self,machineId,v8Id,isolateId,info):
        isolate = self.getIsolate(machineId,v8Id,isolateId);
        if isolate == 0:
            return;

        self.lock.acquire();
        if info["action"] == "update":
            for key in info:
                isolate[key] = info[key];
        self.lock.release();

#        if info["action"] == "terminated":
#            self.removeIsolate(machineId,v8Id,isolateId);

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
        for i in range(0,nris):
            info = response["isolates"][str(i)];
            self.isolateUpdate(machineId,v8Id,i+1,info)

    def prettyPrint(self):
        self.lock.acquire();
        v8 = self.getV8(self.getMachine(1),1);
        if(v8 == 0):
            print "Could not find v8 instance";
            return;

        print "ISOLATES "+"_"*35
        for i in v8["isolates"]:
            isolate = v8["isolates"][i];
            items = "("+str(isolate["id"])+") ";
            for item in isolate:
                if item != "action" and item != "id":
                    items += str(item)+":"+str(isolate[item])+" "
            print items;
            print "_"*45

        self.lock.release();

    def debug(self):
        print self.STATUS;
