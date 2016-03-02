import imp
import os
import sys, traceback
import types
from os import listdir
from os.path import isfile, join

def __loadModule(filepath):
    filepath = "../Policies/"+filepath
    mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])

    py_mod = 0;
    try:

        if file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, filepath)
        else:
            if not file_ext.lower() == '.py':
                filepath += '.py';
            py_mod = imp.load_source(mod_name, filepath)
    except Exception as e:
        print "Error loading policy "+filepath+" "+str(e)
        py_mod = 0;

    return py_mod

memory = 0;
pname = "?"

rte = ("runToEnd" in sys.argv)
if rte:
    if "policy" in sys.argv and "memory" in sys.argv:
        for i in range(0,len(sys.argv)):
            if sys.argv[i] == "policy":
                pname = sys.argv[i+1]
            if sys.argv[i] == "memory":
                memory = int(float(sys.argv[i+1])*1024*1024)
    else:
        print "# Manually Stepped Automated Simulation"
        print "For a completely automated simulation provide the policy name and amount of memory in command line arguments:"
        print "python test <path_to_output_folder> runToEnd policy <policy_name> memory <amount of memory in MB>"
        pname = raw_input("Policy Name:");
        rte = False
else:
    pname = raw_input("Policy Name:");
            
policy = __loadModule(pname)

def generateIsolates(nris):
    isl = []
    while nris > 0:
        isl.append({"heap":0,"throughput":1,"footPrint":0})
        nris -= 1
    return isl

def getFiles(path,ext):
    allcsvs = []

    try:
        for f in listdir(path):
            if isfile(join(path, f)) and ext in f:
                allcsvs.append(join(path,f));
            else:
                allcsvs += getFiles(join(path,f),ext)
    except Exception as e:
        print "Error while finding csv:"+str(e)
        pass

    return allcsvs;

def runAutomated(path,runToEnd):
    global memory
    if memory == 0:
        memory = input("Maximum Machine Memory (MB):")*1024*1024
    
    allcsvsf = getFiles(path,".csv")
    #open files
    allcsvs = []
    for csvf in allcsvsf:
        allcsvs.append(open(csvf,"r"))

    schema = []

    line = ""
    for csv in allcsvs:
        line = csv.readline()

    isl = generateIsolates(len(allcsvs))
    schema = line.split(",")
    schema = schema[:-1]
    
    if not runToEnd:
        print "Schema:"+str(schema)
    
    ctx = {}
    policy.init(ctx)

    while len(allcsvs) > 0:
        index = 0;
        for csv in allcsvs:
            line = csv.readline()
            if len(line) == 0:#isolate died
                csv.close()
                allcsvs.remove(csv)
                del isl[index]
                index -= 1
            else:
                line = line.split(",")[:-1]
                for i in range(0,len(line)):
                    isl[index][schema[i]] = float(line[i])

            index += 1
        
        isl = policy.calculate(memory,isl,ctx);
        for o in isl:
            print o

        if not runToEnd:
            cont = raw_input("(x to exit)");
            if cont == "no" or cont == "n" or cont == "x":
                return;
        else:
            print "_"*80
def runManual(keys):
    keys = keys.split(",")
    nrritr = input("Nr Reiterations:")
    nrisl = input("Nr Isolates:")
    isl = generateIsolates(nrisl)
    
    for i in range(0,nrritr):
        for i in range(0,nrisl):
            for key in keys:
                isl[i][key] = input(key+" Isolate("+str(i+1)+"):")

        isl = policy.calculate(100,isl,{});
        for o in isl:
            print o

print "Testing:"+policy.name()
if len(sys.argv) > 1:
    runAutomated(sys.argv[1],rte)
else:
    print "No CSV files path provided for simulation, input will be done manually"
    keys = raw_input("Coma separated list of properties to control:");
    runManual(keys)