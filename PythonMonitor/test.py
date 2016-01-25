from monitor import *
from requestbuilder import *

m = monitor();
id = m.addMachine("127.0.0.1");
if "127.0.0.1" != id:
	print "FAIL: Machine Address Resolution Failed";
else:
	print "SUCCESS: new machine added:"+id;

v8 = m.addV8(id,"127.0.0.1");
if v8 == 0:
	print "FAIL: could not add V8 to valid machine";
else:
	print "SUCCESS: new V8 added:"+str(v8);

isl = m.addIsolate(id,v8);
if isl == 0:
	print "FAIL: could not add isolate to valid V8";
else:
	print "SUCCESS: new isolate added:"+str(isl);

isl = m.addIsolate(id,v8);
if isl == 0:
	print "FAIL: could not add isolate to valid V8";
else:
	print "SUCCESS: new isolate added:"+str(isl);

v8 = m.addV8(id,"b");
m.getCommunicators();

r = RequestBuilder(m);
print r.makeDefaultRequest(id);
print r.statusReport(id)
print r.isolateStatusReport(id,v8,0)

base = r.isolateStatusReport(id,2,0)
print base;
print ""
#
base = r.recommendHeapSize(id,1,1231,base);
print base;
base = r.recommendHeapSize(id,2,1231,base);
print base;
base = r.setMaxHeapSize(id,1,1231,base);
print base;
base = r.setMaxHeapSize(id,2,1231,base);
print base;
