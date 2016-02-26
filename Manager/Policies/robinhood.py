#Robin Hood Policy (naive)
#Concept@ Jeremy Singer
#Implementation@ Milorad Liviu Felix

import math
from operator import itemgetter

def init(context):
	context["alpha"] = 25*1024*1024; # 25 MB |other values trid 10MB 1MB
	context["robLimit"] = 1;
	
def markIsolates(isolates,totalAvailableMemory):
	memlim = totalAvailableMemory / len(isolates)
	hasNewIsolates = False;
	
	for isolate in isolates:
		if "rhMark" not in isolate:
			isolate["rhMark"] = True;
			hasNewIsolates = True

	for isolate in isolates:
		isolate["hardHeapLimit"] = memlim;

	return hasNewIsolates

def keyExtractor(isolate):
	return isolate["throughput"]

def sort(isolates):
	isolates.sort(key=keyExtractor)

def getNeed(i):
	n = max(0,i["hardHeapLimit"]*(-math.log(i["throughput"])/2) - i["hardHeapLimit"])
	return min(i["hardHeapLimit"],n)

def calculate(totalAvailableMemory,isolates,ctx):
	if markIsolates(isolates,totalAvailableMemory):
		return isolates

	sort(isolates)
	
	roblimit = ctx["robLimit"]
	if roblimit > len(isolates)/2:
		roblimit = len(isolates)/2;

	#enhanced version
	#successfully packs 5 binarytree.json(203MB min heap) in 1GB
	if len(isolates) > 1:
		need = getNeed(isolates[-1])
		isolates[0]["hardHeapLimit"] -= need
		isolates[-1]["hardHeapLimit"] += need
	
	#initial version, worked well with sum of heap sizes much smaller then 
	#total available memory.
	#failed to fit 5 binarytree.js(203MB min heap) in 1GB - 1 instance failed

	#i = 0
	#while roblimit > 0:
	#	isolates[i]["hardHeapLimit"] -= ctx["alpha"]
	#	isolates[-(i+1)]["hardHeapLimit"] += ctx["alpha"]
	#	roblimit -= 1
	#	i += 1

	return isolates;

def name():
	return "JRobinHood v1.0"

def stats():
	return "No stats available"