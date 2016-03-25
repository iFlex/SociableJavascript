import sys
from os import listdir
from os.path import isfile, join

def getFileAvgNmax(path):
	f = open(path,"r")

	f.readline()

	avg = 0
	lines = 0
	mx = 0
	while True:
		line = f.readline()

		if len(line) == 0:
			break

		items = line.split(',')[:-1]

		fp = 0
		for i in items:
			if len(i) > 0:
				fp += float(i)

		avg += fp

		if mx < fp:
			mx = fp

		lines += 1
		
	if lines == 0:
		lines = 1
	return (int(float(avg)/lines),int(mx))

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

def perPolicy(path):
	avg = 0
	mx = 0 
	nr = 0
	for f in listdir(path):
		if not isfile(join(path, f)):
			files = getFiles(join(path,f),"aggregate.csv")
			for fpts in files:
				r = getFileAvgNmax(fpts)
				if mx < r[1]:
					mx = r[1];
				avg += r[0];
				nr += 1
				#print str(r) + " " + fpts
	
	if nr == 0:
		nr = 1
	avg = float(avg)/nr
	return (avg,mx)

def perRun(path):
	for f in listdir(path):
		if not isfile(join(path, f)):
			results = perPolicy(join(path, f))
			print str(results)+" "+str(f)

def perEval(path):
	for f in listdir(path):
		if not isfile(join(path, f)):
			print f
			perRun(join(path, f))
			print "_"*80

print perPolicy(sys.argv[1])
#perRun(sys.argv[1])