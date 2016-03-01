import sys
import os
from Scenarios.Scenario import *
from Plotter.plotter import *
import subprocess

if len(sys.argv) < 2:
	print "USAGE:python runscen.py path_to_scenario_file"
else:
	scenario = Scenario(sys.argv[1],Plotter(100,"ScenarioMemoryUsage",{})) 
	scenario.run()

	if len(sys.argv) > 3:

		raw_input("Press any key to collect results...");
		print "collect_path:"+sys.argv[2]
		print "policy_name:"+sys.argv[3]
		
		collectPath = sys.argv[2]
		scenario.policyName = sys.argv[3]

		plotpath = "./out/plots/"+scenario.pStartDate
		scenfile = sys.argv[1][sys.argv[1].rfind("/")+1:]
		scenfile = scenfile[:scenfile.rfind(".")]

		procLogs = scenario.logPath
		report   = scenario.resultFile.name
		heapUsed = scenario.minHeapSize

		if collectPath[len(collectPath)-1] != "/":
			collectPath += "/"
		collectPath += scenario.policyName + "_" + scenfile
		
		print "Creating Collection Directory "+str(collectPath)
		if not os.path.exists(collectPath):
			os.makedirs(collectPath)

		print "Moving Results File:"+report
		try:
			os.rename(report,collectPath+"/results.txt")
		except Exception as e:
			print "FAILED:"+str(e);

		print "Moving Process Output Files..."
		try:
			os.rename(procLogs,collectPath+"/process_outputs/");
		except Exception as e:
			print "FAILED:"+str(e);

		print "Moving Plotted Data:"+scenario.pStartDate
		try:
			os.rename(plotpath,collectPath+"/"+scenario.pStartDate)
		except Exception as e:
			print "FAILED:"+str(e);

		print "Making aggregate of memory FootPrint for correctness checkin:"
		print subprocess.check_call(["python","./tools/csvjoin.py",collectPath+"/"+scenario.pStartDate,"footPrint",collectPath+"/footprint.csv"]);

		print "Enjoy results at:"+collectPath