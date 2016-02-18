#Robin Hood Policy
#Author@ Milorad Liviu Felix
import math

def init(context):
	pass	

def invert(tp):
	return 101 - tp;

def calculate(totalAvailableMemory,isolates,ctx):
	total = 0
	for i in isolates:
		total += invert(i["throughput"]);

	for i in isolates:
		i["hardHeapLimit"] = totalAvailableMemory*(float(invert(i["throughput"]))/total)
	
	return isolates;

def name():
	return "Inverse Throughput v1.0"

def stats():
	return "No stats available"
