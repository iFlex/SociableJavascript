import matplotlib.pyplot as plt
import pylab
import numpy 
import copy
import os
import time

SINGLETON = 0
class Plotter:

    def __init__(self,width,title):
        global SINGLETON
        if SINGLETON != 0:
            print "#ERROR: Plotter is a singleton class, can't instantiate more than one instance of it! It is because of the way matplotlib was built"
            return

        SINGLETON = 1

        self.imgWritePath = "./plots/"
        self.rawWritePath = "./plotdata/"
        
        if not os.path.exists(self.imgWritePath):
            os.makedirs(self.imgWritePath)
        if not os.path.exists(self.rawWritePath):
            os.makedirs(self.rawWritePath)

        self.title = title
        self.graphs   = []
        self.Xdata    = numpy.arange(0,width)
        self.Ydata    = []
        self.defaultY = numpy.arange(0,width)
        self.labels   = []
        self.maxY = 0
        self.fullHistory = 0

        for i in range(0,width):
            self.defaultY[i] = 0

        xpixels = 1499
        ypixels = 900
        # get the size in inches
        dpi = 85
        xinch = xpixels / dpi
        yinch = ypixels / dpi

        #fig = pylab.gcf()

        fig = plt.figure(figsize=(xinch,yinch))
        fig.canvas.set_window_title(title)
        plt.ion()
        
        pylab.ylim([0,800])
        pylab.xlim([0,width])

    #TODO
    def reset(self):
        pass

    def startFullHistoryLog(self,lebels):
        self.fullHistory = open(self.str(time.asctime( time.localtime(time.time()) ))+self.title+".csv","r")
        for label in labels:
            self.fullHistory.write(label)
    
    def endFullHistoryLog(self):
        if self.fullHistory == 0:
            return
        self.fullHistory.close()

    def plot(self,elements,tlabels):
        index = 0
        
        if self.fullHistory == 0:
            startFullHistoryLog(tlables)

        for e in elements:
            if index == len(self.Ydata):
                self.Ydata.append(copy.deepcopy(self.defaultY))
            
            self.Ydata[index] = numpy.roll(self.Ydata[index],-1)
            self.Ydata[index][len(self.Ydata[index]) - 1] = e
        
            if self.fullHistory:
                self.fullHistory.write(str(e)+",")

            index += 1

        if self.fullHistory:
            self.fullHistory.write("\n")
        
        ln = len(self.Ydata)
        for index in range(0,ln):
            if index == len(self.graphs):
                graph = plt.plot(self.Xdata,self.Ydata[index])[0]
                self.graphs.append(graph)
                self.labels.append(tlabels[index])
                
                plt.legend(self.labels, ncol=4, loc='upper center', 
                    bbox_to_anchor=[0.5, 1.1], 
                    columnspacing=1.0, labelspacing=0.0,
                    handletextpad=0.0, handlelength=1.5,
                    fancybox=True, shadow=True)
            else:
                self.graphs[index].set_ydata(self.Ydata[index])

        try:
            plt.draw() # update the plot
        except Exception as e:
            print "CAN'T PLOT - ISSUES WITH DATA MOST LIKELY"
            print e

    def save(self,prepend):
        name = prepend + self.title
        plt.savefig(self.imgWritePath+name+".png")

    def close(self):
        self.save("")
        plt.close()

    def setTitle(self,title):
        fig = pylab.gcf()
        fig.canvas.set_window_title(title)
        self.title = title