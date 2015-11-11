import json
import math
import subprocess
import staticPlot
from datetime import datetime

MAX_HEAP = 1024

def run(heapSize,program,scripts):
    start_time = datetime.now()

    try:
        cmd = str(program)+" "+str(heapSize)+" "+scripts
        print cmd
        result = subprocess.check_output(cmd, shell=True)
    except Exception as e:
        return (False,-1);

    end_time = datetime.now()
    duration = end_time - start_time
    return (True,duration.total_seconds());

def findHeapCurve(program,script,minheap,increment):
    global MAX_HEAP

    increment = (MAX_HEAP - minheap) / increment;
    report = [];
    heap = minheap

    while heap < MAX_HEAP:
        r = run(heap,program,script);

        report.append([heap/minheap,r[1]]);

        heap = math.floor(heap+increment)

    return report;

def findMinimumHeapBinSrc(program,scripts):
    maxFailing = 0;
    size = 1024; #1GB initial  - well over the 750MB default old_space_size v8 sets on 32bit systems
    lastWorkingUpperLimit = size * 2;
    report = [];
    while size != lastWorkingUpperLimit:
        rt = run(size,program,scripts)
        report.append([size,rt[1]]);
        print str(size)+" - "+str(lastWorkingUpperLimit)+" r:"+str(rt)

        if rt[0] == True:
            lastWorkingUpperLimit = size;
            size = math.floor(size / 2)
            
            if size < maxFailing:
                size = maxFailing + math.ceil((lastWorkingUpperLimit - maxFailing ) / 2.0)    
        else:
            if maxFailing < size:
                maxFailing = size;

            size = size + math.ceil(( lastWorkingUpperLimit - size ) / 2.0)

    return (lastWorkingUpperLimit,report);

#read config file and start measuring
cfgfile = raw_input("cfg file:");
if len(cfgfile) == 0:
    cfgfile = "config.json"

content = "";
with open(cfgfile, 'r') as content_file:
	content = content_file.read()
cfg = json.loads(content);

results = []
for test in cfg["tests"]:
    try:
        #add in the abs location of the scripts
        scripts = ""
        for i in range(0,len(test["script"])):
            scripts += " " + cfg["location"] + test["script"][i];

        #execute test pack
        if test.has_key('heapSize'):
            mhs = findHeapCurve(cfg["location"]+cfg["binary"],scripts,test["heapSize"], 10);
            staticPlot.save(mhs,"measurements/refined/"+test["alias"]+".png");
        else:
            mhs = findMinimumHeapBinSrc(cfg["location"]+cfg["binary"],scripts);
            test["heapSize"] = mhs[0]
            #staticPlot.plot(mhs[1]);
            staticPlot.save(mhs[1],"measurements/"+test["alias"]+".png");

    except Exception as e:
        print "### Failed to process test"
        print test
        print "###:"+str(e)

print "Save Report"
#save the report
f = file(cfgfile,"w");
f.write(json.dumps(cfg,indent=4, sort_keys=True));
f.close();

print "Done"
