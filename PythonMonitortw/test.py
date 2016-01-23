from monitor import *
from requestbuilder import *

m = monitor();
m.addMachine(0);
m.addV8(1);
m.addIsolate(1,1);
m.addIsolate(1,1);

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
