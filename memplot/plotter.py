import matplotlib.pyplot as plt

class Plotter:

    nrcoex = 0;
    xdata = [];
    history = [];
    plots = [];
    time = 0;
    ymin = 0;
    ymax = 0;

    def __init__(self,nr_of_coexisting_plots):
        self.nrcoex = nr_of_coexisting_plots;
        for i in range(0,self.nrcoex):
            self.history.append([]);
            self.plots.append( plt.plot([0])[0] );

        self.time = 0;
        plt.ion()

    def plot(self,string):
        #update history
        elements = string.split();
        for i in range(0,len(elements)):
            if i < len(self.plots):
                element = int(elements[i])
                self.history[i].append(element);
                if self.ymax < element:
                    self.ymax = element + 2;
                if self.ymin > element:
                    self.ymin = element - 1;

        #advance on time scale and reset
        self.xdata.append(self.time);
        plt.ylim([self.ymin,self.ymax])
        plt.xlim([0,self.time]);
        #plot
        for i in range(0,len(self.plots)):
            self.plots[i].set_xdata(self.xdata)
            self.plots[i].set_ydata(self.history[i])  # update the data

        plt.draw() # update the plot
        self.time += 1
