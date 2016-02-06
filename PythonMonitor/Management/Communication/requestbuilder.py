'''
Create a request for a certain v8 process
'''
class RequestBuilder:
    def __init__(self, monitor):
        self.monitor = monitor;
                
    def makeDefaultRequest(self,machineId,v8Id):
        
        result = {"global":{"action":""},"TotalIsolates":0,"isolates":{}};
        v8 = self.monitor.getV8(self.monitor.getMachine(machineId),v8Id);
        if v8 == 0:
            print "Generic Request Builder: Invalid Machine, V8 pair:"+str(machineId)+":"+str(v8Id);
            return result;

        isolates = v8["isolates"].keys();
        for i in isolates:
            result["isolates"][i] = {"action":""};
        
        result["TotalIsolates"] = len(isolates);
        return result;

    def statusReport(self,machineId,v8Id):
        result = self.makeDefaultRequest(machineId,v8Id);
        if result == 0:
            return 0;

        result["global"]["action"] = "status";
        return result;

    def isolateStatusReport(self,machineId,v8Id,isolateId,result):
        if result == 0:
            result = self.makeDefaultRequest(machineId,v8Id);
            if result == 0:
                return 0;
        
        if  isolateId in result["isolates"]:
            result["isolates"][isolateId]["action"] = "status";
        
        return result;

    def recommendHeapSize(self,machineId,v8Id,isolateId,size,result):
        if result == 0:
            result = self.makeDefaultRequest(machineId,v8Id);
            if result == 0:
                return 0;

        if  isolateId in result["isolates"]:
            result["isolates"][isolateId]["action"] = "set_heap_size";
            result["isolates"][isolateId]["heap"] = size;
            return result;
        return 0;

    def setMaxHeapSize(self,machineId,v8Id,isolateId,size,result):
        if result == 0:
            result = self.makeDefaultRequest(machineId,v8Id);
            if result == 0:
                return 0;

        if isolateId in result["isolates"]:
            result["isolates"][isolateId]["action"] = "set_max_heap_size";
            result["isolates"][isolateId]["heap"] = size;
            return result;
        else:
            print "The V8 you want to control does not have an isolate_"+str(isolateId);
            print result["isolates"]
        return 0;


    def startScript(self,machineId,v8Id,script):
        result = self.makeDefaultRequest(machineId,v8Id);
        if result == 0:
            return 0;

        result["global"]["action"] = "execute";
        result["global"]["path"]   = script;
        return result;

    #DO NOT USE, causes segfault in v8wrapper
    def terminate(self,machineId,v8Id,isolateId,result):
        if result == 0:
            result = self.makeDefaultRequest(machineId,v8Id);
            if result == 0:
                return 0;

        if  isolateId in result["isolates"]:
            result["isolates"][isolateId]["action"] = "terminate";
            return result;
        return 0;
