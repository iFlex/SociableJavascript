import json
import sys, traceback
from base64 import *
from threading import Thread
from threading import RLock

class communicator:

    def __init__(self,socket,monitor):
        global id;
        self.lock = RLock();
        self.socket = socket;
        self.monitor = monitor;
        self.packetSize = 1450;
        self.id = monitor.addMachine(socket);
        self.monitor.addV8(self.id);
        self.separator = ";"    

        #start listener thread
        print "Starting communicator listener...";
        self.thread = Thread(target = self.listen)
        self.thread.start();

    def close(self):
        if self.socket != 0:
            self.socket.close();

    def handleResponse(self,response):
        try:
            response = b64decode(response);
            #print "R:"+response;
            message = json.loads(response);
            self.monitor.update(self.id,1,message);
        except Exception as e:
            print "Error parsing response from V8 instance:"+str(e);
            traceback.print_exc(file=sys.stdout)

    def listen(self):
        response = "";
        while( self.socket != 0 ):
            buff = "";
            try:
                buff = self.socket.recv(self.packetSize);
                #print buff;
            except Exception as e:
                self.socket = 0;
                break;

            i = 0
            while i < len(buff):
                while i < len(buff) and buff[i] == self.separator:
                    i += 1                  
                
                if i > 0 and len(response) > 0:
                    self.handleResponse(response);
                    response = ""

                while i < len(buff) and buff[i] != self.separator:
                    response += buff[i]
                    i += 1

    def send(self,request):
        if(self.id == 0 or request == 0 or self.socket == 0):
            return 0;

        toSend = json.dumps(request);
        #print "snd:"+toSend;

        toSend = b64encode(toSend);
        padding = self.separator*(self.packetSize - len(toSend));
        
        self.lock.acquire();
        
        try:
            self.socket.send(toSend+padding);                    
        except Exception as e:
            print "Machine disconnected:"+str(e)
            self.monitor.removeMachine(self.id);
            self.id = 0;
            self.socket = 0;

        self.lock.release();