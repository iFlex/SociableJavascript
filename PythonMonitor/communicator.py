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
        self.separator = ";"

    def close(self):
        self.socket.close();

    def send(self,request):
        if(self.id == 0 or request == 0):
            return 0;

        toSend = json.dumps(request);
        toSend = b64encode(toSend);
        padding = self.separator*(self.packetSize - len(request));
        response = "";
        buff = "";
        
        try:
            self.socket.send(toSend+padding);

            while( True ):
                buff = self.socket.recv(self.packetSize);
                if(len(buff) > 0):                
                    for i in range(0,len(buff)):
                        if( buff[i] == self.separator and i == 0 ):
                            response = ""

                        if( not (buff[i] == self.separator) ):
                            response += buff[i];

                    if(buff[len(buff)-1] == self.separator):
                        break;
                else:
                    break;
                    
        except Exception as e:
            print "Machine disconnected:"+str(e)
            self.monitor.removeMachine(self.id);
            self.id = 0;
            return 0;

        try:
            response = b64decode(response);
            response = json.loads(response);
            print response
            self.monitor.update(self.id,1,response);
            return 1;
        except Exception as e:
            print "Warning: error when processing server response:"+str(e)
            return 0;
