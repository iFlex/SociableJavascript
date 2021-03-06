import json
import sys, traceback
from base64 import *
from threading import Thread
from threading import RLock
from socket import *

class communicator:

    def __init__(self,socket,monitor,machineId,requestCallback):
        global id;
        self.lock = RLock();
        self.keepRunning = True;
        self.doJoin = True;
        self.sent = 0
        self.recvd = 0
        self.sentB = 0
        self.recvdB = 0

        self.packetSize = 1450;
        self.socket = socket;
        self.separator = ";"

        self.monitor = monitor;
        self.mid = machineId;
        self.v8id = monitor.addV8(machineId,self);
        self.requestCallback = requestCallback;

        #start listener thread
        print "New V8_"+str(self.v8id)+" @ machine_"+str(machineId);
        self.thread = Thread(target = self.listen)
        self.thread.daemon = True
        self.thread.start();

    def close(self):
        if self.keepRunning == False:
            return;
        
        print "Disconnected V8_"+str(self.v8id)+" @ machine_"+str(self.mid);
        self.monitor.removeV8(self.mid,self.v8id);
        
        with self.lock:
            self.keepRunning = False;
            try:
                self.socket.shutdown(SHUT_RDWR);
            except Exception as e:
                pass
            self.socket.close();
        
        if self.doJoin:
            self.thread.join();

    def getStats(self):
        return {"sent":self.sent,"received":self.recvd,"bytesOut":self.sentB,"bytesIn":self.recvdB}

    def getStrStats(self):
        return "SentCMD:"+str(self.sent)+" RecvCMD:"+str(self.recvd)+" SendB:"+str(self.sentB)+" RecvB:"+str(self.recvdB)

    def handleResponse(self,response):
        try:
            response = b64decode(response);
            message = json.loads(response);
            self.requestCallback(self.mid,self.v8id,message);
            self.recvd += 1
        except Exception as e:
            print "Error parsing response from V8 instance:"+str(e);
            traceback.print_exc(file=sys.stdout)

    def listen(self):
        response = "";
        while( self.keepRunning ):
            buff = "";
            try:
                buff = self.socket.recv(self.packetSize);
                self.recvdB += len(buff)
                #print buff;
            except Exception as e:
                self.doJoin = False;
                self.close();
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
        #print "Graceful Communicator Thread Exit...";

    def send(self,request):
        if request == 0 :
            print "#SEND_ERR:Bad request!";
            return 0;

        toSend = json.dumps(request);
        #print "snd:"+toSend;

        toSend = b64encode(toSend);
        padding = self.separator*(self.packetSize - len(toSend));
        
        with self.lock:
            try:
                self.socket.send(toSend+padding);                    
                self.sent += 1
                self.sentB += len(toSend)+len(padding)
            except Exception as e:
                print "Machine disconnected:"+str(e)
                self.close();