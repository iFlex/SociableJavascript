#Inverse Throughput
#Author@ Milorad Liviu Felix
import math

def init(context):
	pass	

def transform(tp):
	if tp < 0.99:
		tp = 0.01;
	return -math.log10(tp/1000.0);

def calculate(totalAvailableMemory,isolates,ctx):
	total = 0
	for i in isolates:
		total += transform(i["throughput"]);

	for i in isolates:
		i["hardHeapLimit"] = totalAvailableMemory*(transform(i["throughput"])/total)
	
	return isolates;

def name():
	return "Inverse Throughput Social v1.0"

def stats():
	return "No stats available"
