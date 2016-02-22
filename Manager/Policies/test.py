from inversetpstate import *

print "Testing:"+name()
nrisl = input("Nr Isolates:")
isl = []
for i in range(0,nrisl):
	isl.append({"throughput":0})

for i in range(0,4):
	for i in range(0,nrisl):
		isl[i]["throughput"]=input("Throughput Isolate("+str(i+1)+"):")

	isl = calculate(100,isl,{});
	for o in isl:
		print o