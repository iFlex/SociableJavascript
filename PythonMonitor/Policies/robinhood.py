#Robin Hood Policy - soft robin hood, does not force the hand of rich isolates
#Author@ Milorad Liviu Felix

context = {}

def init(context):
	context["immediateBudget"] = 0;
	context["totalBudget"] = 0;

def markIsolates(isolates):
	for isolate in isolates:
		if "rhMark" not in isolate:
			isolate["rhMark"] = True;
			isolate["throughput"] = 0;

def splitInPoorAndRich(isolates):
	poor = []
	rich = []

	for isolate in isolates:
		if isolate["throughput"] >= 1:
			rich.append(isolate)
		else:
			poor.append(isolate)

	return (poor,rich)

def recalculateBudgets(totalMachineAllowance,rich):
	global context;
	used = 0
	available = 0
	for item in rich:
		used += item["heap"]
		available += item["available"]

	context["immediateBudget"] = totalMachineAllowance - used;
	context["totalBudget"]     = context["immediateBudget"] + available;
	print context;

def helpThePoor(poor,rich):
	global context
	suggestions = [];

	if len(poor) > 0:
		memForPoor = context["totalBudget"] / len(poor);
		for i in poor:
			i["hardHeapLimit"] = memForPoor;
			suggestions.append(i);
		
		for i in rich:	
			i["hardHeapLimit"] = i["heap"] - i["available"]
			suggestions.append(i);

	return suggestions

def calculate(totalAvailableMemory,isolates,ctx):
	global context
	context = ctx

	markIsolates(isolates)
	poor,rich = splitInPoorAndRich(isolates)
	recalculateBudgets(totalAvailableMemory,rich)
	r = helpThePoor(poor,rich);
	print r
	return r