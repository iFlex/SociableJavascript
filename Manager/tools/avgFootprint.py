import sys
f = open(sys.argv[1],"r")

f.readline()

avg = 0
lines = 0
mx = 0
mn = 999999999
while True:
	line = f.readline()

	if len(line) == 0:
		break

	items = line.split(',')

	fp = 0
	for i in items:
		fp += int(i)

	avg += fp

	if mx < fp:
		mx = fp

	if mn > fp:
		mn = fp

	lines += 1

print "Average Footprint:"
print str(float(avg)/lines)+"MB"
print "Max Footprint:"
print str(mx)+" MB"
print "Min Footprint:"
print str(mn)+" MB"