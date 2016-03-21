import sys
from os import listdir
from os.path import isfile, join

APPLY_WEIGHTS = False
scores = {
	"400_aFasta"    :1,
	"400_crypto"    :1,
	"400_binarytree":1,
	"400_splay"     :1,
	"400_heavy"     :3,
	"400_all"       :2,
	"400_light"     :4,
	"AVM400_heavy"  :3,
	"AVM400_heavy2" :2,
	"AVM400_light"  :4,
	"ACM400_heavy"  :3,
	"ACM400_light"  :4,
}

def hasError(fpath):
	try:
		f = open(fpath)
		l = f.readline()
		f.close()
		if len(l) == 0:
			return 0
		return 1
	except:
		return 0

def getFiles(path,ext):
	allcsvs = []
	try:
		for f in listdir(path):
			if isfile(join(path, f)) and ext in f:
				allcsvs.append(join(path,f));
			else:
				allcsvs += getFiles(join(path,f),ext)
	except:
		pass

	return allcsvs;

def countErrors(path,withAvg):
	try:
		avg = 0
		nr = 0
		for f in listdir(path):
			if not isfile(join(path, f)):
				files = getFiles(join(path,f),".stderr")
				errors = 0
				for e in files:
					errors += hasError(e)
				nr += 1
				valout = int((1 - float(errors)/len(files))*100)
				avg += valout
				print str(valout)+" "+str(f)
		
		if withAvg:
			print "*"*3 + " AVG"
			print str(float(avg)/nr)
	
	except Exception as e:
		print e

def countErrorsPerRun(path):
	for f in listdir(path):
		if not isfile(join(path, f)):
			print f
			countErrors(join(path, f),"avg" in sys.argv)
			print "_"*80

def countErrorsAll(path):
	paths = []
	for f in listdir(path):
		if not isfile(join(path, f)):
			paths.append(join(path, f))
	
	paths.sort()
	for p in paths:
		print p
		countErrorsPerRun(p)	

if "count_run" in sys.argv: 
	countErrorsPerRun(sys.argv[1])
elif "count_all" in sys.argv:
	countErrorsAll(sys.argv[1])
else:
	countErrors(sys.argv[1],"avg" in sys.argv)