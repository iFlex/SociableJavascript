def init():
	print "ALIVE"
'''
	Takes in:
		totalAvailableMemory that is the absolute limit for all JS VM instances
		isolates - dictionary containing isolates with information such as heap size, available memory, throughput, etc
	Returns:
		[] - list of dictionary objects, each dictionary object is a suggestion for one isolate
			{} one dictionary object contains id - isolate id, hardHeapLimit - the absolute maximum heap size limit, softHeapLimit - a suggested idea heap size
'''	
def calculate(totalAvailableMemory,isolates):
	print [];