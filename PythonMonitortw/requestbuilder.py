'''
Create a request for a certain v8 process
'''
from monitor import *

class RequestBuilder:
    def __init__(self, monitor):
        self.monitor = monitor;

    def makeDefaultRequest(self,machineId):
        v8id = 1;

        result = {"global":{"action":""},"TotalIsolates":0,"isolates":{}};
        index = 1;
        while(True):
            isolate = self.monitor.getIsolate(machineId,v8id,index);
            if(isolate == 0):
                break;
            else:
                result["isolates"][str(isolate-1)] = {"action":""};
            index += 1

        index -= 1;
        result["TotalIsolates"] = index;
        return result;

    def statusReport(self,machineId):
        result = self.makeDefaultRequest(machineId);
        if result == 0:
            return 0;

        result["global"]["action"] = "status";
        return result;

    def isolateStatusReport(self,machineId,isolateId,result):
        if result == 0:
            result = self.makeDefaultRequest(machineId);
            if result == 0:
                return 0;

        result["isolates"][str(isolateId)]["action"] = "status";
        return result;

    def recommendHeapSize(self,machineId,isolateId,size,result):
        if result == 0:
            result = self.makeDefaultRequest(machineId);
            if result == 0:
                return 0;
        if "isolates" in result and str(isolateId) in result["isolates"]:
            result["isolates"][str(isolateId)]["action"] = "set_heap_size";
            result["isolates"][str(isolateId)]["heap"] = size;
            return result;
        return 0;

    def setMaxHeapSize(self,machineId,isolateId,size,result):
        if result == 0:
            result = self.makeDefaultRequest(machineId);
            if result == 0:
                return 0;

        if "isolates" in result and str(isolateId) in result["isolates"]:
            result["isolates"][str(isolateId)]["action"] = "set_max_heap_size";
            result["isolates"][str(isolateId)]["heap"] = size;
            return result;
        return 0;

    def terminate(self,machineId,isolateId,result):
        if result == 0:
            result = self.makeDefaultRequest(machineId);
            if result == 0:
                return 0;
        if "isolates" in result and str(isolateId) in result["isolates"]:
            result["isolates"][str(isolateId)]["action"] = "terminate";
            return result;
        return 0;
