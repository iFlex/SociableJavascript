#Robin Hood Policy
#Author@ Milorad Liviu Felix
import math

def init(context):
	pass

def transform(tp):
	if tp < 0.0001:
		tp = 0.0001;
	return -math.log10(tp/1000.0);

def calculate(totalAvailableMemory,isolates,ctx):
	total = 0
	for i in isolates:
		if "tpstate" not in i:
			i["tpstate"] = i["throughput"]
		else:
			if i["tpstate"] < 0.9 and i["throughput"] < 0.9:
			#if i["tpstate"] < 0.9 and i["throughput"] < 0.9 and i["tpstate"] > i["throughput"]:
				i["tpstate"] *= i["throughput"]
			else:
				i["tpstate"] = i["throughput"]  
			
		total += transform(i["tpstate"]);

	for i in isolates:
		i["hardHeapLimit"] = totalAvailableMemory*(transform(i["tpstate"])/total)
	
	return isolates;

def name():
	return "Inverse Throughput With State v1.0"

def stats():
	return "No stats available"
