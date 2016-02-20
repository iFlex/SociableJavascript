#Robin Hood Policy
#Author@ Milorad Liviu Felix
import math

def init(context):
	pass	

def dist(avg,val):
	return math.sqrt(math.pow(avg-val,2));

def calculate(totalAvailableMemory,isolates,ctx):
	avg = 0.0
	for i in isolates:
		avg += i["throughput"];
	avg /= len(isolates)
	
	total = 0.0
	for i in isolates:
		total += dist(avg,i["throughput"]);

	if total == 0:
		return "THROUGHPUT SUM:"+str(total)+" > "+str(isolates)

	for i in isolates:
		i["hardHeapLimit"] = totalAvailableMemory*(dist(avg,i["throughput"])/total)
	
	return isolates;

def name():
	return "Reciprocal Bounding v1.0"

def stats():
	return "No stats available"
