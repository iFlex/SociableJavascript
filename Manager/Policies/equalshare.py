#Robin Hood Policy
#Author@ Milorad Liviu Felix
import math

def init(context):
	pass

def calculate(totalAvailableMemory,isolates,ctx):
	mem = totalAvailableMemory / len(isolates);
	for isolate in isolates:
		isolate["hardHeapLimit"] = mem;
	return isolates;

def name():
	return "Equal Share"

def stats():
	return "No stats available"
