#!/usr/bin/python
import sys
import os
from scenarios.Scenario import *
from Plotter.plotter import *
import subprocess
import time

#Use this to automatically run all test scenarios for one policy

def prettifyTime(time):
		seconds = math.floor(time);
		millis  = int(math.floor(time/1000));
		
		mins    = math.floor(seconds/60)
		seconds = int(seconds%60);

		hours   = int(math.floor(seconds/60));
		mins    = int(mins%60);

		return str(hours)+":"+str(mins)+":"+str(seconds)+"."+str(millis);

evalscens = [
"./scenarios/AllVariableSameApplication/400_binarytree.json",
"./scenarios/AllVariableSameApplication/400_splay.json",
"./scenarios/AllConstantSameApplication/400_aFasta.json",
"./scenarios/AllConstantSameApplication/400_crypto.json",
"./scenarios/AllVariableMixed/AVM400_heavy.json",
"./scenarios/AllVariableMixed/AVM400_heavy2.json",
"./scenarios/AllVariableMixed/AVM400_light.json",
"./scenarios/AllConstantMixed/ACM400_heavy.json",
"./scenarios/AllConstantMixed/ACM400_light.json",
"./scenarios/Mixed/400_all.json",
"./scenarios/Mixed/400_heavy.json",
"./scenarios/Mixed/400_light.json"]

if len(sys.argv) < 2:
	print "USAGE: python chainscenarios.py collection_path policy_name"
else:
	collection_path = sys.argv[1];
	policy_name = sys.argv[2];
    collection_path += policy
	autoCollect = ""
	
	if "autoCollect" in sys.argv:
		autoCollect = "autoCollect"

	start = time.time()

	for scen in evalscens:
		if len(autoCollect) == 0:
			print "Press enter key to run scenario:"+scen
			raw_input("");

		subprocess.check_call(["python","runscen.py",scen,collection_path,policy_name,autoCollect])
		
		print scen + " Duration: "+prettifyTime(time.time()-start)
	
	end = time.time();
	print "Evaluation Run Complete:"+prettifyTime(end-start);