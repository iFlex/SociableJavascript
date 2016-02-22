import sys
from Scenario import *

if len(sys.argv) < 2:
	print "USAGE:python runscen.py path_to_scenario_file"
else:
	scenario = Scenario(sys.argv[1]) 
	scenario.run()
