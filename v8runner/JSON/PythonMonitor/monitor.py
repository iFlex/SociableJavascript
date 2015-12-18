STATUS = {"machines":{}};
FreeMachineIDS = list();

def getAppropriateId(FreeList,alternate):
    id = len(FreeList);
    if len(FreeList) > 0:
        id = FreeList[0];
        FreeList.pop();
    else:
        id = alternate + 1;

    return id;

def addMachine(socket):
    global STATUS, FreeMachineIDS;
    machine = {"FreeList":list(),"v8s":dict(),"id":0};

    id = getAppropriateId(FreeMachineIDS,len(STATUS["machines"].keys()));
    machine["id"] = id;
    STATUS["machines"][id] = machine;
    return id;

def removeMachine(machineId):
    global STATUS;
    machines = STATUS["machines"];

    if machineId in machines:
        del machines[machineId];
        FreeMachineIDS.append(machineId);
        return machineId;

    return 0;

def getMachine(machineId):
    global STATUS;

    try:
        return STATUS["machines"][machineId]
    except Exception as e:
        return 0;

def addV8(machineId):
    machine = getMachine(machineId);
    if machine == 0:
        return 0;

    freeIDs = machine["FreeList"];
    v8 = {"FreeList":list(),"isolates":dict(),"id":0};

    id = getAppropriateId(freeIDs,len(machine["v8s"].keys()));
    v8["id"] = id;
    machine["v8s"][id] = v8;
    return id;

def getV8(machine,v8id):
    try:
        return machine["v8s"][v8id]
    except Exception as e:
        return 0;


def removeV8(machineId,v8Id):
    machine = getMachine(machineId);
    if machine == 0:
        return 0;

    v8 = getV8(getMachine(machineId),v8id)
    if v8 == 0:
        return 0;

    id = v8["id"]
    del machine["v8s"][id];
    return id;

def addIsolate(machineId,v8Id):
    v8 = getV8(getMachine(machineId),v8Id)
    if v8 == 0:
        return 0;

    freeIDs = v8["FreeList"];
    isolate = {"id":0};

    id = getAppropriateId(freeIDs,len(v8["isolates"].keys()));
    isolate["id"] = id;
    v8["isolates"][id] = isolate;
    return id;


def removeIsolate(machineId,v8Id,isolateId):
    v8 = getV8(getMachine(machineId),v8Id)
    if v8 == 0:
        return 0;

    if isolateId in v8["isolates"]:
        del v8["isolates"][isolateId];
        return isolateId;

    return 0;

def debug():
    global STATUS;
    print STATUS;
