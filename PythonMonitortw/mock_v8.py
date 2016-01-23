#!/bin/src/python
from requestbuilder import *
from monitor import *
from socket import *
from base64 import *
import json

#Defaults
port = 15000
#network
m = monitor();
id = m.addMachine(1);
print id;
idv = m.addV8(id);
print idv;
print m.addIsolate(id,idv);
r = RequestBuilder(m);

print "V8 Mock Overlod"
soc = socket(AF_INET,SOCK_STREAM);
print "Binding to port "+str(port)
soc.bind(("localhost",port));
print "Listening...";
soc.listen(1);
while True:
    skt = 0;
    address = 0;
    print "Listening..."
    try:
        skt,address = soc.accept()
    except Exception as e:
        print "error while accepting connection";
        break;

    while True:
        try:
            data = skt.recv(1450);
            if len(data) == 0:
                print "Broken connection, going back to listening";
                break;

            try:
                index = data.find(";",0,len(data))
                if index == -1:
                    print "not designed for large packets";
                    continue;
                print ">>"+str(index)
                data = data[0:index];
                data = b64decode(data)
                print "Received:"+data+"|";
                data = json.loads(data)
                m.update(1,1,data);
            except Exception as e:
                print "Invalid request, json parser has failed to process request:"+str(e);

            enc = r.statusReport(1);
            print  "R:"+str(enc);

            resp = json.dumps(enc);
            padding = ";"*(1450 - len(resp))
            skt.send(b64encode(resp)+padding);
        except Exception as e:
            print "Error while processing request:"+str(e);
