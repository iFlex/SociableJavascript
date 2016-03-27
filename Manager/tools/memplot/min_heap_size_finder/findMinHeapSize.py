import json
import math
import subprocess
import staticPlot
from datetime import datetime
import os

MAX_HEAP = 1024
recalcHeapSize = False
measureTime    = True
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
    size = 1; 
    lastFailingLimit = 0;
    lastWorkingLimit = 0;
    report = [];
    while size != lastFailingLimit and size < 1024:
        rt = run(size,program,scripts)
        report.append([size,rt[1]]);
        print str(lastFailingLimit)+" ->("+str(size)+") r:"+str(rt)

        if rt[0] == True:
            lastWorkingLimit = size;
            size = size - math.ceil(( size - lastFailingLimit ) / 2.0)
        else:
            lastFailingLimit = size
            if lastWorkingLimit == 0:
                size *= 2
            else:
                size += math.ceil((lastWorkingLimit - lastFailingLimit)/2.0)
            
    return (size+1,report);

#read config file and start measuring
cfgfile = raw_input("cfg file:");
if len(cfgfile) == 0:
    cfgfile = "config.json"

content = "";
with open(cfgfile, 'r') as content_file:
	content = content_file.read()
cfg = json.loads(content);

results = []
ti = 1
for test in cfg["tests"]:
    try:
        #add in the abs location of the scripts
        print ">>> "+str(ti)+"/"+str(len(cfg["tests"]))
        ti += 1

        scripts = ""
        cont = False
        for i in range(0,len(test["script"])):
            path = cfg["location"] + test["script"][i];
            if not os.path.exists(path):
                print "Unable to locate file:"+path
                print "Skipping test..."
                cont = True
                break
            scripts += " "+path
        if cont:
            continue

        
        #execute test pack
        if test.has_key('heapSize') and (not recalcHeapSize or measureTime):
            if measureTime:
                rt = run(test["heapSize"],cfg["binary"],scripts)
                test["smallHeapTime"] = rt[1];
                rt = run(1024,cfg["binary"],scripts)
                test["largeHeapTime"] = rt[1];
            #mhs = findHeapCurve(cfg["binary"],scripts,test["heapSize"], 10);
            #staticPlot.save(mhs,"measurements/refined/"+test["alias"]+".png");
            pass
        else:
            mhs = findMinimumHeapBinSrc(cfg["binary"],scripts);
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
