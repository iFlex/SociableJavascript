import time
import plotter

p = plotter.Plotter(2);

for i in range(0,10):
    p.plot("10 15 20");
    time.sleep(0.05);

print "done"
raw_input("Press any key to exit");
