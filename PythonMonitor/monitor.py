class monitor:
    def __init__(self):
        self.STATUS = {"machines":{}};
        self.FreeMachineIDS = list();

    def getAppropriateId(self,FreeList,alternate):
        id = len(FreeList);
        if len(FreeList) > 0:
            id = FreeList[0];
            FreeList.pop();
        else:
            id = alternate + 1;

        return id;

    def addMachine(self,socket):
        machine = {"FreeList":list(),"v8s":dict(),"id":0};

        id = self.getAppropriateId(self.FreeMachineIDS,len(self.STATUS["machines"].keys()));
        machine["id"] = id;
        self.STATUS["machines"][id] = machine;
        return id;

    def removeMachine(self,machineId):
        machines = self.STATUS["machines"];

        if machineId in machines:
            del machines[machineId];
            self.FreeMachineIDS.append(machineId);
            return machineId;

        return 0;

    def getMachine(self,machineId):
        try:
            return self.STATUS["machines"][machineId]
        except Exception as e:
            return 0;

    def addV8(self,machineId):
        machine = self.getMachine(machineId);
        if machine == 0:
            return 0;

        freeIDs = machine["FreeList"];
        v8 = {"FreeList":list(),"isolates":dict(),"id":0};

        id = self.getAppropriateId(freeIDs,len(machine["v8s"].keys()));
        v8["id"] = id;
        machine["v8s"][id] = v8;
        return id;

    def getV8(self,machine,v8id):
        try:
            return machine["v8s"][v8id]
        except Exception as e:
            return 0;


    def removeV8(self,machineId,v8Id):
        machine = self.getMachine(machineId);
        if machine == 0:
            return 0;

        v8 = self.getV8(self.getMachine(machineId),v8id)
        if v8 == 0:
            return 0;

        id = v8["id"]
        del machine["v8s"][id];
        return id;

    def addIsolate(self,machineId,v8Id):
        v8 = self.getV8(self.getMachine(machineId),v8Id)
        if v8 == 0:
            return 0;

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
        if isolateId in v8["isolates"]:
            return isolateId;
        return 0;

    def removeIsolate(self,machineId,v8Id,isolateId):
        v8 = self.getV8(self.getMachine(machineId),v8Id)
        if v8 == 0:
            return 0;

        if isolateId in v8["isolates"]:
            del v8["isolates"][isolateId];
            return isolateId;

        return 0;

    def getIsolateCount(self,machineId,v8Id):
        v8 = self.getV8(self.getMachine(machineId),v8Id)
        if v8 == 0:
            return 0;
        else:
            return len(v8["isolates"].keys())

    def isolateUpdate(self,machineId,v8Id,isolateId,info):
        isolate = self.getIsolate(machineId,v8Id,isolateId);
        if isolate == 0:
            return;

        if info["action"] == "update":
            for key in info:
                isolate[key] = info[key];

        if info["action"] == "terminated":
            self.removeIsolate(machineId,v8Id,isolateId);

    def update(self,machineId,v8Id,response):
        nris = response["TotalIsolates"];
        recordedIsolateCount = self.getIsolateCount(machineId,v8Id)

        #adjust isolate count
        diff = nris - recordedIsolateCount;
        if nris > recordedIsolateCount:
            while diff > 0:
                self.addIsolate(machineId,v8Id);
                diff -= 1;
        elif nris < recordedIsolateCount:
            #TODO deal with this properly
            while recordedIsolateCount > nris:
                recordedIsolateCount -= 1;
                self.removeIsolate(machineId,v8Id,recordedIsolateCount);

        #update isolate status
        for i in range(0,nris):
            info = response["isolates"][str(i)];
            self.isolateUpdate(machineId,v8Id,i,info)

    def debug(self):
        print self.STATUS;
