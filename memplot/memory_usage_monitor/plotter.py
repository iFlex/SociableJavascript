import matplotlib.pyplot as plt
import numpy as np

class Plotter:

    nrcoex = 0;
    history = [];
    plots = [];
    time = 0;
    ymin = 0;
    ymax = 0;

    def __preInit(self):
        self.history = [];
        self.plots = [];
        self.time = 0;
        self.ymin = 0;
        self.ymax = 0;

    def __init__(self,nr_of_coexisting_plots):
        self.nrcoex = nr_of_coexisting_plots;
        for i in range(0,self.nrcoex):
            if len(self.history) > i:
                self.history[i] = [];
            else:
                self.history.append([]);

            if len(self.plots) <= i:
                self.plots.append( plt.plot([0])[0] );

        self.time = 0;
        plt.ion()

    def plot(self,string):
        #update history
        #print "plotter:"+str(len(self.history[0]))
        elements = string.split();
        for i in range(0,len(elements)):
            if i < self.nrcoex:
                element = int(elements[i])
                self.history[i].append(element);
                if self.ymax < element:
                    self.ymax = element * 1.2;
                if self.ymin > element:
                    self.ymin = element;

        #rescale
        plt.ylim([self.ymin,self.ymax])
        plt.xlim([0,self.time]);

        #plot
        for i in range(0,self.nrcoex):
            self.plots[i].set_xdata(np.arange(len(self.history[i])))
            self.plots[i].set_ydata(self.history[i])  # update the data
        try:
            plt.draw() # update the plot
        except Exception as e:
            print "CAN'T PLOT - ISSUES WITH DATA MOST LIKELY"
            print e;
        self.time += 1

    def save(self,fname):
        plt.savefig(fname);
        plt.show();

        self.time = 0;
        self.ymin = 0;
        self.ymax = 0;
