import matplotlib.pyplot as plt
import numpy as np

def compare(a,b):
    return int(a[0] - b[0])

def _plot(data):
    data.sort(cmp=compare)

    xdata = []
    ydata = []
    ymax = 0
    xmax = 0
    for item in data:
        xdata.append(item[0]);
        ydata.append(item[1]);

        if item[1] > ymax:
            ymax = item[1]

        if item[0] > xmax:
            xmax = item[0]

    ax = plt.plot([0])[0];
    ax.set_xdata(xdata)
    ax.set_ydata(ydata)

    plt.ylim([-2,ymax*1.2])
    plt.xlim([0,xmax]);

def plot(data):
    _plot(data);
    plt.show();

def save(data,fname):
    _plot(data);
    plt.savefig(fname);
    plt.close();
