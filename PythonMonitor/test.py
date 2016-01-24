from monitor import *
from requestbuilder import *

m = monitor();
id = m.addMachine("addr");
v8 = m.addV8(id,"a");
m.addIsolate(id,v8);
m.addIsolate(id,v8);
v8 = m.addV8(id,"b");
m.getCommunicators();

r = RequestBuilder(m);
print r.makeDefaultRequest(1);
print r.statusReport(1)
print r.isolateStatusReport(1,1,0)
base = r.isolateStatusReport(1,2,0)
print base;
print ""
#
base = r.recommendHeapSize(1,1,1231,base);
print base;
base = r.recommendHeapSize(1,2,1231,base);
print base;
base = r.setMaxHeapSize(1,1,1231,base);
print base;
base = r.setMaxHeapSize(1,2,1231,base);
print base;
