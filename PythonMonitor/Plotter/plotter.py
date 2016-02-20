import matplotlib.pyplot as plt
import pylab
import numpy 
import copy
import os
import time
import collections
import timeit
import time
import math

SINGLETON = 0
class Plotter:

    def setFPS(self,fps):
        self.desiredFPS = 32;
        self.period     = 1.0/self.desiredFPS;
    
    def resetPlotPaths(self):
        if not self.makeFolders:
            return

        self.startDateTime = str(time.strftime("%Y_%d_%m_%H_%M")) #str(time.asctime( time.localtime(time.time())))
        self.writePath = self.rootStore+self.startDateTime+"/"+self.title+"/"
        
        if not os.path.exists(self.writePath):
            os.makedirs(self.writePath)

    def configure(self,config):    
        if "makeCSV" in config:
            self.makeCSV = config["makeCSV"]

        if "makePNG" in config:
            self.makePNG = config["makePNG"]
        
        if "makeLiveDrawing" in config:
            self.makeLiveDrawing = config["makeLiveDrawing"];

        if "fps" in config:
            self.setFPS(config["fps"])

        if "path" in config:
            self.rootStore = config["path"]
        
        self.makeFolders = self.makeCSV or self.makePNG
 
    def __init__(self,width,title,config):
        global SINGLETON
        if SINGLETON != 0:
            print "#ERROR: Plotter is a singleton class, can't instantiate more than one instance of it! It is because of the way matplotlib was built"
            return

        SINGLETON = 1

        self.makeCSV = True;
        self.makePNG = True;
        self.makeFolders = True;
        self.makeLiveDrawing = True;
        self.rootStore = "./out/plots/"
        self.configure(config);

        self.width = width
        self.plotProgress = 0
        self.setFPS(30)
        self.skipDraw   = 0;

        self.title = title
        self.graphs   = []
        self.Xdata    = numpy.arange(0,width)
        self.Ydata    = []
        self.defaultY = collections.deque(maxlen=width) 
        self.labels   = []
        self.maxY = 0
        self.fullHistory = 0

        for i in range(0,width):
            self.defaultY.append(0)

        self.resetPlotPaths();

        xpixels = 1499
        ypixels = 900
        # get the size in inches
        dpi = 85
        xinch = xpixels / dpi
        yinch = ypixels / dpi

        if self.makeLiveDrawing:
            self.fig = plt.figure(figsize=(xinch,yinch))
            self.fig.canvas.set_window_title(title)
            self.ax = self.fig.add_subplot(111);

            self.fig.show()
            self.fig.canvas.draw()
            
            pylab.ylim([0,100])
            pylab.xlim([0,width])

    def reset(self,title):
        self.save();
        self.endFullHistoryLog();
        self.Ydata = []
        self.plotProgress = 0
        self.maxY = 0;

        self.setTitle(title)
        self.resetPlotPaths()

    def startFullHistoryLog(self,labels):
        if not self.makeCSV:
            return 0;

        self.fullHistory = open(self.writePath+self.title+".csv","w")
        for label in labels:
            self.fullHistory.write(label+",")
        self.fullHistory.write("\n");

    def endFullHistoryLog(self):
        if self.fullHistory == 0:
            return
        self.fullHistory.close()
        self.fullHistory = 0

    def plot(self,elements,tlabels):
        index = 0
        if self.fullHistory == 0:
            self.startFullHistoryLog(tlabels)

        #for e in elements:
        ln = len(tlabels)
        lnn = len(elements)
        for i in range(0,ln):
            e = 0
            if i < lnn:
                e = elements[i]
                
            if index == len(self.Ydata):
                self.Ydata.append(copy.deepcopy(self.defaultY))
            self.Ydata[index].append(e)
            
            if self.fullHistory != 0:
                self.fullHistory.write(str(e)+",")
            
            if self.maxY < e:
                self.maxY = e

            index += 1
        
        if self.fullHistory != 0:
            self.fullHistory.write("\n")
        
        time1 = time.time()
        
        self.plotProgress += 1
        if self.skipDraw > 0 and (self.plotProgress % self.width > 0):
            self.skipDraw -=1 
            return

        if self.makeLiveDrawing:
            ln = len(self.Ydata)
            for index in range(0,ln):
                if index == len(self.graphs):
                    graph = self.ax.plot(self.Xdata,self.Ydata[index])[0]
                    self.graphs.append(graph)
                    self.labels.append(tlabels[index])
                    
                    plt.legend(self.labels, ncol=4, loc='upper center', 
                        bbox_to_anchor=[0.5, 1.1], 
                        columnspacing=1.0, labelspacing=0.0,
                        handletextpad=0.0, handlelength=1.5,
                        fancybox=True, shadow=True)
                else:
                    self.graphs[index].set_ydata(self.Ydata[index])
            
            pylab.ylim([0,self.maxY])
            try:
                self.fig.canvas.draw() # update the plot
            except Exception as e:
                print "CAN'T PLOT - ISSUES WITH DATA MOST LIKELY"
                print e

            if self.plotProgress % self.width == 0:
                self.save();

        time2 = time.time()
        self.drawPeriod = time2-time1
        self.skipDraw   = math.floor(self.drawPeriod / self.period)

    def save(self):
        if not self.makePNG or not self.makeLiveDrawing:
            return;

        plt.savefig(self.writePath+str(self.plotProgress)+".png")

    def close(self):
        self.endFullHistoryLog()
        self.save()
        plt.close()

    def setTitle(self,title):
        if not self.makeLiveDrawing:
            return;

        self.fig.canvas.set_window_title(title)
        self.title = title