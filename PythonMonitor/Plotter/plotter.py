import matplotlib.pyplot as plt
import pylab
import numpy 
import copy

SINGLETON = 0
class Plotter:

    def __init__(self,width,title):
        global SINGLETON
        if SINGLETON != 0:
            print "#ERROR: Plotter is a singleton class, can't instantiate more than one instance of it! It is because of the way matplotlib was built"
            return;
        
        SINGLETON = 1;       
        self.title = title;
        self.graphs   = [];
        self.Xdata    = numpy.arange(0,width);
        self.Ydata    = [];
        self.defaultY = numpy.arange(0,width);
        self.labels   = []
        for i in range(0,width):
            self.defaultY[i] = 0;

        fig = pylab.gcf()
        fig.canvas.set_window_title(title)
        plt.ion()
        pylab.ylim([0,1000])

    def plot(self,elements,tlabels):
        index = 0;
        for e in elements:
            if index == len(self.Ydata):
                self.Ydata.append(copy.deepcopy(self.defaultY))
            
            self.Ydata[index] = numpy.roll(self.Ydata[index],-1);
            self.Ydata[index][len(self.Ydata[index]) - 1] = e;
            index += 1

        ln = len(self.Ydata)
        for index in range(0,ln):
            if index == len(self.graphs):
                graph = plt.plot(self.Xdata,self.Ydata[index])[0]
                self.graphs.append(graph)
                self.labels.append(tlabels[index]);
                
                plt.legend(self.labels, ncol=4, loc='upper center', 
                    bbox_to_anchor=[0.5, 1.1], 
                    columnspacing=1.0, labelspacing=0.0,
                    handletextpad=0.0, handlelength=1.5,
                    fancybox=True, shadow=True)
            else:
                self.graphs[index].set_ydata(self.Ydata[index]);

        try:
            plt.show() # update the plot
            plt.pause(0.01);
        except Exception as e:
            print "CAN'T PLOT - ISSUES WITH DATA MOST LIKELY"
            print e;

    def save(self,fname):
        plt.savefig(fname);

    def close(self):
        self.save(self.title+"png");
        plt.close();