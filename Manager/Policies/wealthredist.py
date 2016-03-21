#Wealth Redistribution - take and give to all
#Author@ Milorad Liviu Felix
import math

#inspect and fix with extra care
context = {}
MAX_TP = 100
DELTA_HEAP_LIMIT    = 0.75 #0.75
DELTA_MAX_FOOTPRINT = 0.20 #0.20
DELTA_THROUGHPUT    = 0.05 #0.05
def init(context):
	if "csvlog" in context:
		context["csvlog"].commitSchema(["gini","redistribute","available","take","commited2isolates"])


def getWelfareIndex(i):
	hhl = float(max(0,i["hardHeapLimit"] - i["footPrint"]))/i["hardHeapLimit"]
	mtp = 1 - float(i["footPrint"])/i["maxFootPrint"]
	tpt = i["throughput"]/MAX_TP

	return DELTA_HEAP_LIMIT*hhl + DELTA_MAX_FOOTPRINT*mtp + DELTA_THROUGHPUT*tpt

def getGivePotential(i):
	return max(0,i["hardHeapLimit"] - i["heap"]) #getWelfareIndex(i)

def getNeedPotential(i):
	return 1 - getWelfareIndex(i)

def getMaxFp(isolates):
	mfp = 0
	for i in isolates:
		mfp = max(mfp,i["footPrint"])

	for i in isolates:
		i["maxFootPrint"] = mfp

def getGini(isolates):
	sumOfDifferences = 0
	sumOfThroughputs = 0

	for x in isolates:
	   for y in isolates:
	       sumOfDifferences += math.fabs(getWelfareIndex(x)-getWelfareIndex(y))
	       sumOfThroughputs += getWelfareIndex(x)

	giniIndex = sumOfDifferences / (2*sumOfThroughputs)

	return giniIndex;

def calculatePotentials(isolates):
	totalInUse = 0;
	totalGivePotential = 0.0
	totalNeedPotential = 0.0
	for i in isolates:
		totalInUse += i["hardHeapLimit"];
		totalGivePotential += getGivePotential(i)
		totalNeedPotential += getNeedPotential(i)

	return (totalGivePotential,totalNeedPotential,totalInUse)

def redistribute(isolates,Take,Available,TGigveP,TNeedP):
	t = 1
	g = 1
	ln = len(isolates)
	for i in isolates:
		
		if TGigveP == 0:
			t = 0
		else:
			t = getGivePotential(i)/TGigveP
		
		if TNeedP == 0:
			g = 1/ln
		else:
			g = getNeedPotential(i)/TNeedP

		i["hardHeapLimit"] += (g-t)*Take + g*Available
		
		#if allocation attempts to kill an isolate, revert to equal share
		if i["hardHeapLimit"] < 1:
			print "WARNING: ATTEMPTED TO KILL ISOLATE"
			return False;

	return True

def equalShare(isolates,totalAvailableMemory):
	memlim = totalAvailableMemory / len(isolates)
	for isolate in isolates:
		isolate["hardHeapLimit"] = memlim;

def markIsolates(isolates,totalAvailableMemory):
	hasNewIsolates = False;
	
	for isolate in isolates:
		if "pMark" not in isolate:
			isolate["pMark"] = True;
			isolate["average"] = 0;
			isolate["avindex"] = 0;
			hasNewIsolates = True

	if hasNewIsolates:
		equalShare(isolates,totalAvailableMemory)

	return hasNewIsolates

def calculate(totalAvailableMemory,isolates,ctx):
	global context
	context = ctx

	if markIsolates(isolates,totalAvailableMemory):
		return isolates;

	getMaxFp(isolates)
	gini = getGini(isolates)
	give,need,used = calculatePotentials(isolates)
	
	Redistribute = min(totalAvailableMemory * gini,give)
	Available    = max(0,totalAvailableMemory - used)
	Take         = max(0,Redistribute - Available)

	success = redistribute(isolates,Take,Available,give,need) 
	if not success:
		equalShare(isolates,totalAvailableMemory)

	if "csvlog" in ctx:
		ctx["csvlog"].commitLine([gini,Redistribute,Available,Take,success]);
	else:
		print "g:"+str(gini)+" r:"+str(Redistribute)+" A:"+str(Available)+" T:"+str(Take)
		
	return isolates

def name():
	return "Wealth Redistribution v3.2:"+str(DELTA_HEAP_LIMIT)+":"+str(DELTA_MAX_FOOTPRINT)+":"+str(DELTA_THROUGHPUT)

def stats():
	return "No stats available"