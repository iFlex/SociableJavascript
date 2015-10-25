import numpy as np
import matplotlib.pyplot as plt

plt.axis([0, 1000, 0, 1])
plt.ion()
plt.show()
timeAxis = 0;

def plot(string):
        global timeAxis;
        #plot
        
        #increment time
        timeAxis += 1
