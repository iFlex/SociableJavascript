import json
import math
import subprocess
import staticPlot
from datetime import datetime

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
        else:
            if maxFailing < size:
                maxFailing = size;
            size = size + math.ceil(( lastWorkingUpperLimit - size ) / 2.0)

    return report;

#read config file and start measuring
content = "";
with open("config.json", 'r') as content_file:
	content = content_file.read()
cfg = json.loads(content);

results = []
for test in cfg["tests"]:
    try:
        #add in the abs location of the scripts
        for i in range(0,len(test["script"])):
            test["script"][i] = cfg["location"] + test["script"][i];
        #execute test pack
        mhs = findMinimumHeapBinSrc(cfg["location"]+cfg["binary"],(" ").join(test["script"]));
        results.append([mhs,test["alias"]]);

        #staticPlot.plot(mhs);
        staticPlot.save(mhs,"measurements/"+test["alias"]+".png");

    except Exception as e:
        print "### Failed to process test"
        print test
        print "###:"+str(e)

print "Generating final report"

#save the report
f = file("measurements/report.json","w");
f.write(json.dumps(results));
f.close();

print "Done"
