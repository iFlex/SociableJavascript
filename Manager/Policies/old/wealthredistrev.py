#Wealth Redistribution - ThDrop
#Author@ Milorad Liviu Felix
import math

#inspect and fix with extra care
MAX_THPT = 200.0
context = {}

def init(context):
	context["poor_treshold"] = 0
	if "csvlog" in context:
		context["csvlog"].commitSchema(["totalAvailableMemory","redistributable","RichD","PoorD"])

def throughputRescale(t):
	t = max(0.00001,t)
	return -math.log10(t/MAX_THPT);

def getGini(isolates):
	sumOfDifferences = 0
	sumOfThroughputs = 0

	for x in isolates:
	   for y in isolates:
	       sumOfDifferences += math.fabs(throughputRescale(x["throughput"])-throughputRescale(y["throughput"]))
	       sumOfThroughputs += throughputRescale(x["throughput"])

	giniIndex = sumOfDifferences / (2*sumOfThroughputs)

	return giniIndex;

def calcPoorTreshold(isolates):
	sm = 0.0
	for i in isolates:
		sm += throughputRescale(i["throughput"])
		#sm += i["throughput"]
	sm = float(sm)/len(isolates);

	return math.pow(10,-sm)
	#return sm

def calcThroughputDrops(isolates):
	for i in isolates:
		if "old_tp" in i:
			i["tdrop"] = max(0.0,throughputRescale(i["throughput"]) - i["old_tp"])
		else:
			i["tdrop"] = 0.0

		i["old_tp"] = throughputRescale(i["throughput"])

def calcRedistribution(isolates,poor_treshold):
	
	RichContrib     = 0.0
	PoorContrib     = 0.0
	Redistributable = 0.0
	totalUsed       = 0.0 
	for i in isolates:
		totalUsed += i["hardHeapLimit"]
		if i["throughput"] <= poor_treshold:
			PoorContrib += i["tdrop"]
		else:
			RichContrib += i["hardHeapLimit"]
			Redistributable += i["hardHeapLimit"]

	return (RichContrib,PoorContrib,Redistributable,totalUsed)

def redistribute(isolates,rc,pc,ac,redistribute,allocatable,poor_treshold):
	richd = []
	poord = []

	allocatable += redistribute;
	
	if rc == 0 and pc == 0:
		return;

	#poor and rich exist
	if rc != 0 and pc != 0:
		for i in isolates:
			if i["throughput"] <= poor_treshold:
				coef = i["tdrop"]/pc;
				poord.append(coef);
				i["hardHeapLimit"] += coef*allocatable
			else:
				richd.append((i["hardHeapLimit"]/rc))
				i["hardHeapLimit"] -= (i["hardHeapLimit"]/rc)*redistribute
	
	#everyone is rich
	if pc == 0:
		allocatable -= redistribute
		for i in isolates:
			richd.append((i["hardHeapLimit"]/rc))
			i["hardHeapLimit"] += (i["hardHeapLimit"]/rc)*allocatable
	
	#everyone is poor
	if rc == 0:
		allocatable -= redistribute
		for i in isolates:
			poord.append((i["hardHeapLimit"]/ac))
			i["hardHeapLimit"] += (i["hardHeapLimit"]/ac)*allocatable
				
	return (richd,poord)

def markIsolates(isolates,totalAvailableMemory):
	memlim = totalAvailableMemory / len(isolates)
	hasNewIsolates = False;
	
	for isolate in isolates:
		if "pMark" not in isolate:
			isolate["pMark"] = True;
			isolate["average"] = 0;
			isolate["avindex"] = 0;
			hasNewIsolates = True

	if hasNewIsolates:
		for isolate in isolates:
			isolate["hardHeapLimit"] = memlim;

	return hasNewIsolates

def calculate(totalAvailableMemory,isolates,ctx):
	global context
	context = ctx

	if markIsolates(isolates,totalAvailableMemory):
		return isolates;

	old = []
	new = []
	
	for i in isolates:
		old.append(i["hardHeapLimit"])

	poor_treshold = 0.99 #calcPoorTreshold(isolates);
	calcThroughputDrops(isolates);

	gini = getGini(isolates)
	rc,pc,redist,totalUsed = calcRedistribution(isolates,poor_treshold)
	allocatable = totalAvailableMemory - totalUsed;
	allocatable = max(0,allocatable)

	redist /= 3
	redist = min(redist,totalAvailableMemory*gini);
	redist -= allocatable;
	redist = max(0,redist)

	richd,poord = redistribute(isolates,rc,pc,totalUsed,redist,allocatable,poor_treshold)
	
	for i in isolates:
		new.append(i["hardHeapLimit"])

	if "csvlog" in ctx:
		richds = "("+str(len(richd))+")"
		poords = "("+str(len(poord))+")"
		for i in richd:
			richds += str(i)+"|"
		for i in poord:
			poords += str(i)+"|"
		ctx["csvlog"].commitLine(["gini:"+str(gini)+" alc:"+str(allocatable)+" rdst:"+str(redist)]);

	return isolates

def name():
	return "Wealth Redistribution v1.2"

def stats():
	return "No stats available"