from Management.monitor import *
from Management.Communication.requestbuilder import *

m = monitor("NONE",0);

machine = m.addMachine("127.0.0.1")
v8      = m.addV8(machine,0)
i       = m.addIsolate(machine,v8);

print machine+"_V8_"+str(v8)+"_"+str(i)
isl = m.getIsolate(machine,v8,i)
print "Machine:"
print m.getMachine(machine)
print "V8:"
print m.getV8(m.getMachine(machine),v8)
print "Iso:"
print isl
print "Remove..."
m.removeIsolate(machine,v8,i)