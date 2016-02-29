#Robin Hood Policy
#Author@ Milorad Liviu Felix
import math

def init(context):
	pass

def markIsolates(isolates,totalAvailableMemory):
	memlim = totalAvailableMemory / len(isolates)
	hasNewIsolates = False;
	
	for isolate in isolates:
		if "rhMark" not in isolate:
			isolate["rhMark"] = True;
			hasNewIsolates = True

	if hasNewIsolates:
		for isolate in isolates:
			isolate["hardHeapLimit"] = memlim;

	return hasNewIsolates

def getNeed(i):
	return max(0,i["heap"]*(-math.log(i["throughput"])) - i["hardHeapLimit"])

def keyGetter(isolate):
	return isolate["throughput"]

def calculate(totalAvailableMemory,isolates,ctx):

	if markIsolates(isolates,totalAvailableMemory):
		return isolates
	
	isolates.sort(key=keyGetter);

	ln = len(isolates)
	mid = ln/2;
	if mid > 0:
		avg = 0.0
		for i in range(mid,ln):
			avg += getNeed(isolates[i])

		avg /= (ln - mid)

		#Take from rich
		for i in range(0,mid):
			isolates[i]["hardHeapLimit"] -= avg;
		#Give to poor
		for i in range(mid,ln):
			isolates[i]["hardHeapLimit"] += avg;

	return isolates;

def name():
	return "JRobinHood v1.2"

def stats():
	if total == 0:
		return "No stats available"
	
	s =  "RobinHood stats:\nFromBudget:"+str(float(fromBudget)/total*100)
	s += "\nFromAvailable:"+str(float(fromAvailable)/total*100)
	s += "\nFromStealing:"+str(float(fromStealing)/total*100)
	s += "\nAllRich:"+str(float(allRich)/total*100)
	s += "\nAllPoor:"+str(float(allPoor)/total*100)
	return s

