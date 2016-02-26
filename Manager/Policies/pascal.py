#Robin Hood Policy
#Author@ Milorad Liviu Felix
import math

def init(context):
	pass

def markIsolates(isolates,totalAvailableMemory):
	memlim = totalAvailableMemory / len(isolates)
	hasNewIsolates = False;
	
	for isolate in isolates:
		if "pMark" not in isolate:
			isolate["pMark"] = True;
			isolate["average"] = 0;
			isolate["avindex"] = 0;
			hasNewIsolates = True

	for isolate in isolates:
		isolate["hardHeapLimit"] = memlim;

	return hasNewIsolates

def calculate(totalAvailableMemory,isolates,ctx):
	if markIsolates(isolates,totalAvailableMemory):
		return isolates;

	for i in isolates:
		if i["throughput"] < 1:
			i["hardHeapLimit"] *= 2
			i["average"] = i["hardHeapLimit"]
			i["avindex"] = 1
		else:
			i["average"] += i["footPrint"];
			i["avindex"] += 1
			i["hardHeapLimit"] = int(i["average"]/i["avindex"])
			#i["hardHeapLimit"] /= 2;

	return isolates

def name():
	return "Pascal v1.0"

def stats():
	return "No stats available"