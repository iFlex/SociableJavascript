import os
import sys
toRun = [];


def populateQueueFromFolder(path):
	global toRun;
	lst = os.listdir(path);
	print lst;
	for item in lst:
		if item.find(".js",0,len(item)) > -1:
			toRun.append(item);

def runTest(fn):
	print("running test:"+fn);
	#os.system("python monitor.py v8wrapper.bin &");
	os.system("../v8runner/v8wrapper.bin "+fn);
	print("done running");


populateQueueFromFolder(raw_input("where are your scripts:"));
print toRun;
for script in toRun:
	runTest(script);

