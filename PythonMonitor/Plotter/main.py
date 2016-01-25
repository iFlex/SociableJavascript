from subprocess import *
import json
#TODO: need to use pipes for plotting

plotter1 = Popen(["python","-u","plotter.py"],stdin=PIPE,stdout=PIPE,stderr=PIPE);

plotter1.stdin.write('Title');
print plotter1.stdout.read();
data = {"values":[0,1,2],"labels":["heap","suggest","mega"]}
while True:
	plotter1.stdin.write(json.dumps(data));
	print plotter1.stdout.read();
	#w = raw_input("EXIT?")
	#if len(w)>1:
	#	break

print plotter1.stdin.write("close");