from Management.cli import *
from Management.Communication.communicator import *
from Management.monitor import *
from Management.Communication.server import *
from Management.policy import *

mon = monitor("NONE",0);

mon.addMachine("127.0.0.1");
mon.addV8("127.0.0.1",0);
mon.addIsolate("127.0.0.1",1);
mon.addIsolate("127.0.0.1",1);
mon.addV8("127.0.0.1",0);
mon.addIsolate("127.0.0.1",2);
mon.addIsolate("127.0.0.1",2);

mon.addMachine("127.0.0.2");
mon.addV8("127.0.0.2",0);
mon.addIsolate("127.0.0.2",1);
mon.addIsolate("127.0.0.2",1);
mon.addV8("127.0.0.2",0);
mon.addIsolate("127.0.0.2",2);
mon.addIsolate("127.0.0.2",2);

policy = Policy(mon,1);