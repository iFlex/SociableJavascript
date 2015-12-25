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

    def update(self,id,response):
        return ""

    def debug(self):
        print self.STATUS;
