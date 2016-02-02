from cli import *
from communicator import *
from monitor import *
from server import *
from policy import *

mon = monitor("ALL");

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