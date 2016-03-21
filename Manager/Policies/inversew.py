#Inverse Wealth
#Author@ Milorad Liviu Felix
import math

MAX_TP = 100
DELTA_HEAP_LIMIT    = 0.75
DELTA_THROUGHPUT    = 0.25
def init(context):
	if "csvlog" in context:
		context["csvlog"].commitSchema(["gini","redistribute","available","take","commited2isolates"])

def getInvWelfareIndex(i):
	if i["hardHeapLimit"] == 0:
		i["hardHeapLimit"] = 1;

	hhl = 1 - float(max(0,i["hardHeapLimit"] - i["footPrint"]))/i["hardHeapLimit"]
	tpt = i["throughput"]/MAX_TP

	return 1 - (DELTA_HEAP_LIMIT*hhl + DELTA_THROUGHPUT*tpt);

def equalShare(isolates,totalAvailableMemory):
	memlim = totalAvailableMemory / len(isolates)
	for isolate in isolates:
		isolate["hardHeapLimit"] = memlim;

def markIsolates(isolates,totalAvailableMemory):
	hasNewIsolates = False;
	
	for isolate in isolates:
		if "pMark" not in isolate:
			isolate["pMark"] = True;
			hasNewIsolates = True

	if hasNewIsolates:
		equalShare(isolates,totalAvailableMemory)

	return hasNewIsolates

def calculate(totalAvailableMemory,isolates,ctx):
	if markIsolates(isolates,totalAvailableMemory):
		return isolates;

	total = 0
	for i in isolates:
		total += getInvWelfareIndex(i)

	for i in isolates:
		i["hardHeapLimit"] = totalAvailableMemory*(getInvWelfareIndex(i)/total)
		if i["hardHeapLimit"] == 0:
			i["hardHeapLimit"] = 1;

	return isolates;

def name():
	return "Inverse_Wealth_"+str(DELTA_HEAP_LIMIT)+"_"+str(DELTA_THROUGHPUT)

def stats():
	return "No stats available"
