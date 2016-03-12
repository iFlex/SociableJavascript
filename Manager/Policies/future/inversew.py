#Inverse Wealth Policy
#Author@ Milorad Liviu Felix
import math

DELTA_HEAP_LIMIT    = 0.75
DELTA_MAX_FOOTPRINT = 0.20
DELTA_THROUGHPUT    = 0.05

def init(context):
	pass	

def getInverseWelfareIndex(i):
	hhl = 1 - float(max(0,i["hardHeapLimit"] - i["footPrint"]))/i["hardHeapLimit"]
	mtp = 1 - float(i["footPrint"])/i["maxFootPrint"]
	tpt = i["throughput"]/MAX_TP

	return 1 - DELTA_HEAP_LIMIT*hhl + DELTA_MAX_FOOTPRINT*mtp + DELTA_THROUGHPUT*tpt

def calculate(totalAvailableMemory,isolates,ctx):
	total = 0
	for i in isolates:
		total += getInverseWelfareIndex(i);

	for i in isolates:
		i["hardHeapLimit"] = totalAvailableMemory*(getInverseWelfareIndex(i) / total)
	
	return isolates;

def name():
	return "Inverse Wealth v1.0-"+str(DELTA_HEAP_LIMIT)+"-"+str(DELTA_MAX_FOOTPRINT)+"-"+str(DELTA_THROUGHPUT)

def stats():
	return "No stats available"
