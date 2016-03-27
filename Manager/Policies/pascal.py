#Pascal2 Policy - uses soft heap limit to put pressure on isolates
#Author@ Milorad Liviu Felix
import math

def init(context):
	pass

def calculate(totalAvailableMemory,isolates,ctx):
	for i in isolates:
		i["softHeapLimit"] = 0;
	
	return isolates

def name():
	return "Pascal v2.0"

def stats():
	return "No stats available"