#Wealth Redistribution
#Author@ Milorad Liviu Felix
import math
POOR_TRESHOLD = 0.99

def init(context):
	pass

def throughputRescale(t):
	return -math.log10(t/200.0);

def getGini(isolates):
	sumOfDifferences = 0
	sumOfThroughputs = 0

	for x in isolates:
	   for y in isolates:
	       sumOfDifferences += math.fabs(throughputRescale(x["throughput"])-throughputRescale(y["throughput"]))
	       sumOfThroughputs += throughputRescale(x["throughput"])

	giniIndex = sumOfDifferences / (2*sumOfThroughputs)

	return giniIndex;

def calcRedistribution(isolates):
	RichContrib = 0.0
	PoorContrib = 0.0
	Redistributable = 0.0
	for i in isolates:
		if i["throughput"] < POOR_TRESHOLD:
			PoorContrib += -math.log(i["throughput"])
		else:
			RichContrib += i["throughput"]
			Redistributable += i["hardHeapLimit"]

	return (RichContrib,PoorContrib,Redistributable)

def redistribute(isolates,rc,pc,redistribute):
	for i in isolates:
		if i["throughput"] < POOR_TRESHOLD:
			i["hardHeapLimit"] += (-math.log(i["throughput"])/pc)*redistribute
		else:
			i["hardHeapLimit"] -= (i["throughput"]/rc)*redistribute

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

	gini = getGini(isolates)
	rc,pc,redist = calcRedistribution(isolates)
	
	redist /= 2
	redist = min(redist,totalAvailableMemory*gini);

	redistribute(isolates,rc,pc,redist)

	return isolates

def name():
	return "Wealth Redistribution v1.0"

def stats():
	return "No stats available"