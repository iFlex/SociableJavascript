import os
import sys
import monitor
import json
import datetime
toRun = [];

def makeCollectionFolder():
	if os.path.isdir("measurements") == False :
		os.system("mkdir measurements");
	d = datetime.datetime.now();
	out_dir = d.strftime("%d_%m_%Y_%H.%M.%S");
	os.system("mkdir measurements/"+out_dir);
	return "./measurements/"+out_dir;

def populateQueueFromFolder(path):
	global toRun;
	lst = os.listdir(path);
	print lst;
	for item in lst:
		if item.find(".js",0,len(item)) > -1:
			toRun.append([item,item]);

def runTest(test,path):
	resolution = 1
	if 'resolution' in test:
		resolution = test['resolution'];

	print("RUNNING TEST:"+test['alias']);
	monitor.monitor_program("v8wrapper.bin",test['script'],test['alias'],resolution,path);
	print("DONE");

if len(sys.argv) > 1:
	content = "";
	with open(sys.argv[1], 'r') as content_file:
		content = content_file.read()
	toRun = json.loads(content);
else:
	populateQueueFromFolder(raw_input("where are your scripts:"));

print "Running tests"
print toRun;
collection_path = makeCollectionFolder();
for test in toRun:
	runTest(test,collection_path);
