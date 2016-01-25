import time;
import random;
from plotter import *

p = Plotter(1024,"Test");

i = 0;
data = {"values":[0,0,0],"labels":["heap","suggested","throughput"]}
while i < 100:
	data["values"][0] = random.randint(0,500);
	data["values"][1] = random.randint(0,500);
	data["values"][2] = random.randint(0,500);
	p.plot(data["values"],data["labels"]);
	time.sleep(0.02);
	i += 1
p.close();