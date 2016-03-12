import sys
from os import listdir
from os.path import isfile, join

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

schemas = []
def loadSchemas(files):
	global schemas
	for f in files:
		try:
			fhndl = open(f,"r")
			schema = fhndl.readline()
			schema = schema.split(",")
			schemas.append({"file":fhndl,"fname":f,"schema":schema});
		except Exception as e:
			print "Failed to read schema for file:"+f+" > "+str(e)

def merge(keys,output):
	global schemas
	try:
		w = open(output,"w")
	except Exception as e:
		print "Could not create output file > "+str(e)
		return

	print "Printing schema..."
	schemout = ""
	for k in keys:
		schemout += k+","
	w.write(schemout*len(schemas)+"\n");
	print "Merging..."

	scln = len(schemas)
	emptyCount = 0
	while emptyCount < scln:
		emptyCount = 0
		for s in schemas:
			line = s["file"].readline()
			if len(line) == 0:
				emptyCount += 1
				for k in keys:
					w.write("0,")
			else:
				line = line.split(",")
				
				keyswritten = 0
				for k in keys:
					ln = len(s["schema"])
					for i in range(0,ln):
						if s["schema"][i] == k:
							try:
								w.write(line[i]+",")
							except Exception as e:
								print "ERROR reading file:"+s["fname"]
								print line
								print "missing key:"+k+" @ "+str(i)
								w.write("0,")
							keyswritten += 1

				if keyswritten < len(keys):
					print "missing keys..."
					w.write("0,"*len(keys) - keyswritten);

		w.write("\n");
	
	for s in schemas:
		s["file"].close()
	w.close()

if len(sys.argv) < 4:
	print "Usage: csvjoin.py search_path comma_separated_merge_keys output_path"
	quit()

files = getFiles(sys.argv[1],".csv")
loadSchemas(files)
merge(sys.argv[2].split(","),sys.argv[3]);
print "COMPLETE"