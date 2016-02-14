#Robin Hood Policy
#Author@ Milorad Liviu Felix
import math

context = {}
fromBudget = 0
fromAvailable = 0
fromStealing  = 0
total         = 1

def init(context):
	context["immediateBudget"] = 0;
	context["totalBudget"] = 0;
	context["stealPool"] = 0;

def markIsolates(isolates):
	for isolate in isolates:
		if "rhMark" not in isolate:
			isolate["rhMark"] = True;
			isolate["throughput"] = 0;
			isolate["hardHeapLimit"] = 0;

def splitInPoorAndRich(isolates):
	poor = []
	rich = []

	for isolate in isolates:
		if isolate["throughput"] >= 1.0:
			rich.append(isolate)
		else:
			poor.append(isolate)

	return (poor,rich)

def recalculateBudgets(totalMachineAllowance,rich,poor):
	global context;
	used = 0
	available = 0
	context["stealPool"] = 0
	for item in rich:
		used += item["hardHeapLimit"]
		available += item["available"]
		context["stealPool"] += item["hardHeapLimit"]
	
	for item in poor:
		used += item["hardHeapLimit"];

	context["immediateBudget"] = totalMachineAllowance - used;
	if(context["immediateBudget"] < 0):
		context["immediateBudget"] = 0

	context["totalBudget"]     = context["immediateBudget"] + available;

def poorIsolateNeed(i):
	n = math.floor(i["heap"] * (-math.log(i["throughput"])/2)) - i["hardHeapLimit"]
	if n < 0:
		return 0;
	return n;

def getPoorNeeds(poor):
	need = 0;
	for i in poor:
		need += poorIsolateNeed(i)

	return need

def helpThePoor(poor,rich):
	global context,fromStealing,fromAvailable,fromBudget,total
	suggestions = [];

	if len(poor) > 0:
		raw_need   = getPoorNeeds(poor)
		steal_need = raw_need - context["immediateBudget"]
		if steal_need < 0:
			steal_need = 0

		total += 1
		if steal_need <= (context["totalBudget"] - context["immediateBudget"]): #can allocate from free memory
			for i in poor:
				i["hardHeapLimit"] += poorIsolateNeed(i);
				suggestions.append(i);
			fromBudget += 1
		elif len(rich) > 0: # need to force the hand of rich isolates
			stolen = 0;
			for i in rich:
				i["hardHeapLimit"] -= i["available"]
				stolen += i["available"]
				suggestions.append(i);

			if stolen < steal_need: #need to take memory away from the in use heap - this has the potential to crash rich isolates
				steal_need -= stolen;
				coef = float(steal_need) / context["stealPool"];
				if coef > 1: 
					coef = 0.3;
				if coef < 0.01:
					coef = 0.01;

				for i in rich:
					if stolen < steal_need:
						steal = math.floor(i["heap"] * coef)
						i["hardHeapLimit"] -= steal; 
						stolen += steal;
				fromStealing += 1
			else:
				fromAvailable += 1

			for i in poor:
				need = poorIsolateNeed(i)
				if stolen > need:
					i["hardHeapLimit"] += + need;
					stolen -= need
				else:
					i["hardHeapLimit"] += stolen;
					steal = 0
				suggestions.append(i);
	#print suggestions
	return suggestions

def calculate(totalAvailableMemory,isolates,ctx):
	global context
	context = ctx

	markIsolates(isolates)
	poor,rich = splitInPoorAndRich(isolates)
	recalculateBudgets(totalAvailableMemory,rich,poor)
	r = helpThePoor(poor,rich);
	return r

def name():
	return "RobinHood v1.0"

def stats():
	return "RobinHood stats - FromBudget:"+str(float(fromBudget)/total*100)+". FromAvailable:"+str(float(fromAvailable)/total*100)+". FromStealing:"+str(float(fromStealing)/total*100)+"."


