#!/bin/src/python
from Management.Communication.requestbuilder import *
from Management.monitor import *
from socket import *
from base64 import *
import json
import time

#Defaults
address = raw_input("IP:")
port = input("port:")
#network
m = monitor("NONE",0);
id = m.addMachine(address);
print id;
idv = m.addV8(id,"no comm");
print idv;
isl = m.addIsolate(id,idv);
print isl

r = RequestBuilder(m);

print "V8 Mock Overlod"
soc = socket(AF_INET,SOCK_STREAM);

while True:
    connected = True;
    try:
        print "Connecting...";
        soc.connect((address,port));
    except Exception as e:
        connected = False;

    while connected:
        try:
            data = soc.recv(1450);
            if len(data) == 0:
                print "Broken connection, going back to listening";
                break;

            try:
                index = data.find(";",0,len(data))
                if index == -1:
                    print "not designed for large packets";
                    continue;

                data = data[0:index];
                data = b64decode(data)
                print "Received:"+data+"|";
                data = json.loads(data)
                m.update(1,1,data);
            except Exception as e:
                print "Invalid request, json parser has failed to process request:"+str(e);

            enc = r.statusReport(address,idv);
            for i in enc["isolates"].keys():
                enc["isolates"][i]["heap"] = 1024012;
                enc["isolates"][i-1] = enc["isolates"][i];
                del enc["isolates"][i]
                
            print  "R:"+str(enc);
            resp = json.dumps(enc);
            padding = ";"*(1450 - len(resp))
            soc.send(b64encode(resp)+padding);
        except Exception as e:
            print "Error while processing request:"+str(e);

    time.sleep(3);
