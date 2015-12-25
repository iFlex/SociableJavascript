from requestbuilder import *
import time;

class Policy:
    def __init__(self,communicator,monitor):
        self.comm = communicator;
        self.monitor = monitor;
        self.interval = 1;#seconds
        self.requestBldr = RequestBuilder(monitor);

    def run(self):
        //get an initial status report
        self.comm.send(self.requestBldr.statusReport(1));
        //keep calculating
        while(True):
            time.sleep(self.interval);
            self.comm.send(self.requestBldr.statusReport(1));
