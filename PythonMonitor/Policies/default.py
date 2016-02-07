runningAvg = {}
startOffset = 10;
def init():
	print "POLICY:Instantiated default running average policy"

'''
	Takes in:
		totalAvailableMemory that is the absolute limit for all JS VM instances
		isolates - dictionary containing isolates with information such as heap size, available memory, throughput, etc
	Returns:
		[] - list of dictionary objects, each dictionary object is a suggestion for one isolate
			{} one dictionary object contains id - isolate id, hardHeapLimit - the absolute maximum heap size limit, softHeapLimit - a suggested idea heap size

	CHECKS:
	sum of all hardLimits must be smaller than totalAvailableMemory
	for each isolate, the soft limit is less than the hard limit
'''	
def calculate(totalAvailableMemory,isolates):
	global runningAvg,startOffset
	result = []
	for isolate in isolates:
		if isolate not in runningAvg:
			runningAvg[isolate] = {"count":0,"sum":0}
		runningAvg[isolate]["count"] += 1;
		runningAvg[isolate]["sum"]   += isolates[isolate]["heap"];
		
		if runningAvg[isolate]["count"] > startOffset:
			result.append({"id":isolate,"hardHeapLimit":(runningAvg[isolate]["sum"]/runningAvg[isolate]["count"])})
	print result;
	return result;