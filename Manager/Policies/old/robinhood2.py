#Robin Hood Policy
#Author@ Milorad Liviu Felix
import math

context = {}
fromBudget = 0
fromAvailable = 0
fromStealing  = 0
allPoor       = 0
allRich       = 0
total         = 0

def max(a,b):
	if b > a:
		return b
	return a;

def min(a,b):
	if b < a:
		return b;
	return a;

def init(context):
	context["StealPool"]         = 0;
	context["ImmediateBudget"]   = 0;
	context["poorReffFiled"]     = "hardHeapLimit";
	context["TotalNeed"]         = 0;
	context["OverflowNeed"]      = 0;
	context["AllocatableNeed"]   = 0;

	context["StealAllowance"]    = 0;
	context["AllocateAllowance"] = 0;
	context["GiveAllowance"]     = 0;
	
def markIsolates(isolates):
	global context
	for isolate in isolates:
		if "rhMark" not in isolate:
			isolate["rhMark"] = True;
			isolate["throughput"] = 0.0001;
			isolate["hardHeapLimit"] = isolate["footPrint"];
			print name()+" MARK"
		#aggravated unresponsiveness
		#elif isolate["hardHeapLimit"] < isolate["heap"]:
		#	if isolate["throughput"] < 1:
		#		isolate["throughput"] /= 2;
		#	else:
		#		isolate["throughput"] = 0.1

def splitInPoorAndRich(isolates):
	poor = []
	rich = []

	for isolate in isolates:
		if isolate["throughput"] >= 1.0:
			rich.append(isolate)
		else:
			poor.append(isolate)

	return (poor,rich)
#budget
def recalculateBudgets(totalMachineAllowance,rich,poor):
	global context;
	
	used = 0
	for item in rich:
		used += item["hardHeapLimit"]
	context["StealPool"] = used

	for item in poor:
		used += item["hardHeapLimit"];

	context["ImmediateBudget"] = totalMachineAllowance - used;
	if(context["ImmediateBudget"] < 0):
		context["ImmediateBudget"] = 0

#needs
def getNeed(i):
	global context
	n = math.floor(i[context["poorReffFiled"]] * (-math.log(i["throughput"]))) - i["hardHeapLimit"]
	n *= context["NeedScale"];
	return max(0,n)

def calcTotalNeed(poor):
	global context
	context["TotalNeed"] = 0
	context["NeedScale"] = 1.0
	for i in poor:
		context["TotalNeed"] += getNeed(i)

	#cap need
	if context["TotalNeed"] > context["TotalAvailableMemory"]:
		context["NeedScale"] = float(context["TotalAvailableMemory"]) / context["TotalNeed"]
		context["TotalNeed"] = context["TotalAvailableMemory"]
	#pump budget
	if context["TotalNeed"] < (context["ImmediateBudget"]*0.5):
		context["TotalNeed"] = context["ImmediateBudget"]*0.5

def divideNeed():
	global context
	context["OverflowNeed"]    = max(0,context["TotalNeed"] - context["ImmediateBudget"])
	context["AllocatableNeed"] = max(0,context["TotalNeed"] - context["OverflowNeed"])

# Allowances
def calcAllowances():
	global context

	if context["StealPool"] == 0:
		context["StealAllowance"] = 0.0
	else:
		context["StealAllowance"] = min(0.5,float(context["OverflowNeed"])/context["StealPool"])
	
	if context["ImmediateBudget"] == 0 or context["TotalNeed"] == 0:
		context["AllocateAllowance"] = 0;	
	else:
		context["AllocateAllowance"] = float(context["AllocatableNeed"])/context["TotalNeed"]*min(1.0,float(context["AllocatableNeed"])/context["ImmediateBudget"])

def calcGiveAllowance():
	if context["TotalStolen"] == 0.0 or context["TotalNeed"] == 0:
		context["GiveAllowance"] = 0.0
	else:
		context["GiveAllowance"] = float(context["OverflowNeed"])/context["TotalNeed"]*min(1.0,float(context["OverflowNeed"])/context["TotalStolen"])

def getSteal(i):
	global context
	return i["hardHeapLimit"]*context["StealAllowance"]

def getGive(i):
	global context
	if context["GiveAllowance"] + context["AllocateAllowance"] > 1.0:
		print "ERROR _ OVERFLOWING ALLOWANCES!!!";
		#return 0;
	return getNeed(i)*(context["GiveAllowance"] + context["AllocateAllowance"]);

def steal(rich):
	global context
	for i in rich:
		stolen = getSteal(i)
		i["hardHeapLimit"] -= stolen
		context["TotalStolen"] += stolen 

def give(poor):
	global context
	sm = 0
	for i in poor:
		given = getGive(i)
		i["hardHeapLimit"] = i[context["poorReffFiled"]] + given
		sm += given

	return sm

def allRichOrPoor(isolates,totalAvailableMemory):
	share = float(totalAvailableMemory) / len(isolates)
	for i in isolates:
		i["hardHeapLimit"] = int(share);

def calculate(totalAvailableMemory,isolates,ctx):
	if len(isolates) == 0:
		return []

	global context
	context = ctx
	context["TotalAvailableMemory"] = totalAvailableMemory;
	#print str(totalAvailableMemory)+" B "+" > "+str(totalAvailableMemory/(1024*1024*1024))+" GB" 
	
	context["TotalStolen"] = 0
	markIsolates(isolates)
	poor,rich = splitInPoorAndRich(isolates)
	recalculateBudgets(totalAvailableMemory,rich,poor)
	if len(poor) == 0 or len(rich) == 0:
		allRichOrPoor(isolates,totalAvailableMemory)
	else:
		calcTotalNeed(poor)
		divideNeed()
		calcAllowances()
		steal(rich)
		calcGiveAllowance()
		
		given = give(poor)
		
		mb = 1204*1024*1.0;
		ttl = 0
		for i in isolates:
			ttl += i["hardHeapLimit"]

		#if ttl > totalAvailableMemory:
		#print "ALLOC OVERFLOW "+str((ttl - totalAvailableMemory)/mb)+" OvrNeed "+str(context["OverflowNeed"]/mb)+" AlcNeed "+str(context["AllocatableNeed"]/mb)+" Budget "+str(context["ImmediateBudget"]/mb)+" StealPool "+str(context["StealPool"]/mb)+" Stolen "+str(context["TotalStolen"]/mb)+" Given "+str(given/mb)+" AAL "+str(context["AllocateAllowance"])+" SAL "+str(context["StealAllowance"])+" GAL:"+str(context["GiveAllowance"])
	return isolates;

def name():
	return "RobinHood v1.1"

def stats():
	if total == 0:
		return "No stats available"
	
	s =  "RobinHood stats:\nFromBudget:"+str(float(fromBudget)/total*100)
	s += "\nFromAvailable:"+str(float(fromAvailable)/total*100)
	s += "\nFromStealing:"+str(float(fromStealing)/total*100)
	s += "\nAllRich:"+str(float(allRich)/total*100)
	s += "\nAllPoor:"+str(float(allPoor)/total*100)
	return s

