from Management.monitor import *
from Management.Communication.requestbuilder import *

testTopo = {}

testTopo["127.0.0.1"] = {"machine":"","v8":0,"isolates":[]};
testTopo["127.0.0.2"] = {"machine":"","v8":0,"isolates":[]};
testTopo["127.0.0.3"] = {"machine":"","v8":0,"isolates":[]};


m = monitor("NONE",0);
index = 0
#3 V8s per machine, 3 isolates per V8
for key in testTopo.keys():
	testTopo[key]["machine"] = m.addMachine(key);
	testTopo[key]["v8"]      = m.addV8(key,0);
	
	#add 3 isolates
	testTopo[key]["isolates"].append(m.addIsolate(key,testTopo[key]["v8"]))
	testTopo[key]["isolates"].append(m.addIsolate(key,testTopo[key]["v8"]))
	testTopo[key]["isolates"].append(m.addIsolate(key,testTopo[key]["v8"]))

	for i in testTopo[key]["isolates"]:
		isl = m.getIsolate(key,testTopo[key]["v8"],i)
		isl["tag"] = "@"+str(index)
		index += 1

def checkRegistryContents(correctNoIsolates):
	found = 0;
	tags  = 0;
	index = 0;
	for key in testTopo.keys():
		for i in testTopo[key]["isolates"]:
			isl = m.getIsolate(key,testTopo[key]["v8"],i)
			if isl != 0:
				if "tag" in isl and isl["tag"] == "@"+str(index):
					tags += 1;
				else:
					print "ERROR: Isolate "+str(key)+"_V8_"+str(testTopo[key]["v8"])+"_"+str(i)+" has INCORRECT_TAG"
			else:
				print "ERROR: Isolate "+str(key)+"_V8_"+str(testTopo[key]["v8"])+"_"+str(i)+" NOT_FOUND"
			
			index += 1
	
	for key in m.STATUS["machines"]:
		for v8 in m.STATUS["machines"][key]["v8s"]:
			found += len(m.STATUS["machines"][key]["v8s"][v8]["isolates"])

	print "Found "+str(found)+" isolates out ouf "+str(3*1*3)
	print "Found "+str(tags) +" correct tags out ouf "+str(3*1*3)
	if found == correctNoIsolates and tags == correctNoIsolates:
		print "SUCCESS "+"*"*50
	else:
		print "FAILURE "+"#"*50

def addAll():
	partMachine = "127.0.0.";
	for i in range(4,10):
		machine = partMachine+str(i)
		m.addMachine(machine)
		for j in range(2,100):
			v8 = m.addV8(machine,0)
			for k in range(4,10):
				m.addIsolate(machine,v8);
	
def removeAll():
	partMachine = "127.0.0.";
	for i in range(4,10):
		machine = partMachine+str(i)
		for j in range(2,100):
			v8 = str(j)
			for k in range(4,10):
				m.removeIsolate(machine,v8,i);
			m.removeV8(machine,v8)
		m.removeMachine(machine)

def addToTopo():
	for key in testTopo.keys():
		for i in range(len(testTopo[key]["isolates"])+1,10):
			m.addIsolate(key,testTopo[key]["v8"]);

def removeFromTopo():
	for key in testTopo.keys():
		for i in range(len(testTopo[key]["isolates"])+1,10):
			v8 = m.getV8(m.getMachine(key),testTopo[key]["v8"])
			m.removeIsolate(key,testTopo[key]["v8"],i);

def runTest():
	addAll();
	addToTopo();
	removeFromTopo();
	removeAll();
	
	addToTopo();
	addAll();
	removeAll();
	removeFromTopo();
	
	addToTopo();
	removeFromTopo();
	

def checkRequest(actual,model):
	if model != actual:
		return "BAD REQUEST FORMATTING\n"+str(actual)+"\n"+str(model)
	return "OK"

print "Checking Registry Building"
checkRegistryContents(index);

print ""
print "Adding and removing items from Registry"
runTest();

print ""
print "Checking Registry Again:"
checkRegistryContents(index);

id = testTopo.keys()[0]
v8 = testTopo[key]["v8"]
isl = testTopo[key]["isolates"][0]

r = RequestBuilder(m);

print ""
print "Testing Request Building:"
print "Default        Request :" + checkRequest(str(r.makeDefaultRequest(id,v8)),"{'TotalIsolates': 3, 'isolates': {'1': {'action': ''}, '3': {'action': ''}, '2': {'action': ''}}, 'global': {'action': ''}}");
print "Status         Request :" + checkRequest(str(r.statusReport(id,v8)),"{'TotalIsolates': 3, 'isolates': {'1': {'action': ''}, '3': {'action': ''}, '2': {'action': ''}}, 'global': {'action': 'status'}}");
print "Isolate Status Request :" + checkRequest(str(r.isolateStatusReport(id,v8,isl,0)),"{'TotalIsolates': 3, 'isolates': {'1': {'action': 'status'}, '3': {'action': ''}, '2': {'action': ''}}, 'global': {'action': ''}}");

base = r.isolateStatusReport(id,v8,isl,0)
print "Testing Request Builder Append Mode:"
print "Reccomend heap size: "+checkRequest(r.recommendHeapSize(id,v8,1,1231,base),"{'TotalIsolates': 3, 'isolates': {'1': {'action': 'set_heap_size', 'heap': 1231}, '3': {'action': ''}, '2': {'action': ''}}, 'global': {'action': ''}}");
print "Reccomend heap size: "+checkRequest(r.recommendHeapSize(id,v8,2,1231,base),"{'TotalIsolates': 3, 'isolates': {'1': {'action': 'set_heap_size', 'heap': 1231}, '3': {'action': ''}, '2': {'action': 'set_heap_size', 'heap': 1231}}, 'global': {'action': ''}}");
print "Absolute  heap size: "+checkRequest(r.setMaxHeapSize(id,v8,1,1231,base),"{'TotalIsolates': 3, 'isolates': {'1': {'action': 'set_max_heap_size', 'heap': 1231}, '3': {'action': ''}, '2': {'action': 'set_heap_size', 'heap': 1231}}, 'global': {'action': ''}}");
print "Absolute  heap size: "+checkRequest(r.setMaxHeapSize(id,v8,2,1231,base),"{'TotalIsolates': 3, 'isolates': {'1': {'action': 'set_max_heap_size', 'heap': 1231}, '3': {'action': ''}, '2': {'action': 'set_max_heap_size', 'heap': 1231}}, 'global': {'action': ''}}");

