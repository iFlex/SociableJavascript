'''
Create a request for a certain v8 process
'''
from monitor import *

class RequestBuilder:
    def __init__(self, monitor):
        self.monitor = monitor;

    def makeDefaultRequest(self,machineId):
        v8id = 1;
        if self.monitor.getV8(self.monitor.getMachine(machineId),v8id) == 0:
            return 0;

        result = {"global":{"action":""},"TotalIsolates":0,"isolates":{}};
        index = 1;
        while(True):
            isolate = self.monitor.getIsolate(machineId,v8id,index);
            if(isolate == 0):
                break;
            else:
                result["isolates"][str(isolate)] = {"action":""};
            index += 1

        index -= 1;
        result["TotalIsolates"] = index;
        return result;

    def statusReport(self,machineId):
        result = self.makeDefaultRequest(machineId);
        result["global"]["action"] = "status";

        return result;

    def isolateStatusReport(self,machineId,isolateId,result):
        if result == 0:
            result = self.makeDefaultRequest(machineId);
        result["isolates"][str(isolateId)]["action"] = "status";
        return result;

    def recommendHeapSize(self,machineId,isolateId,size,result):
        if result == 0:
            result = self.makeDefaultRequest(machineId);
        result["isolates"][str(isolateId)]["action"] = "set_heap_size";
        result["isolates"][str(isolateId)]["heap"] = size;
        return result;

    def setMaxHeapSize(self,machineId,isolateId,size,result):
        if result == 0:
            result = self.makeDefaultRequest(machineId);
        result["isolates"][str(isolateId)]["action"] = "set_max_heap_size";
        result["isolates"][str(isolateId)]["heap"] = size;
        return result;
