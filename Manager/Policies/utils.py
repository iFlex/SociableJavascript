import math

def throughputRescale(t):
	return -math.log10(t/200.0);

def GiniIndex(isolates):
	sumOfDifferences = 0
	sumOfThroughputs = 0

	for x in isolates:
	   for y in isolates:
	       sumOfDifferences += math.fabs(throughputRescale(x["throughput"])-throughputRescale(y["throughput"]))
	       sumOfThroughputs += throughputRescale(x["throughput"])

	giniIndex = sumOfDifferences / (2*sumOfThroughputs)

	return giniIndex;