import json
from base64 import *

class communicator:

    def __init__(self,socket,monitor):
        global id;
        self.socket = socket;
        self.monitor = monitor;
        self.packetSize = 1450;
        self.id = monitor.addMachine(socket);
        self.monitor.addV8(self.id);

    def close(self):
        self.socket.close();

    def send(self,request):
        if(self.id == 0 or request == 0):
            return 0;

        toSend = json.dumps(request);
        toSend = b64encode(toSend);
        padding = ";"*(self.packetSize - len(request));
        response = "";

        try:
            self.socket.send(toSend+padding);
            response = self.socket.recv(self.packetSize);
        except Exception as e:
            self.monitor.removeMachine(self.id);
            self.id = 0;
            return 0;

        try:
            response = b64decode(response);
            response = json.loads(response);
            self.monitor.update(self.id,1,response);
            return 1;
        except Exception as e:
            #print "Warning: error when processing server response:"+str(e)
            return 0;
