import json
class communicator:

    def __init__(self,socket,monitor):
        global id;
        self.socket = socket;
        self.monitor = monitor;
        self.packetSize = 1450;
        self.id = monitor.addMachine(socket);

    def send(request):
        if(self.id == 0):
            return 0;

        toSend = json.dumps(request);
        padding = " "*(self.packetSize - len(request));
        response = "";

        try:
            self.socket.send(toSend+padding);
            response = self.socket.recv(self.packetSize);
        except Exception as e:
            self.monitor.removeMachine(self.id);
            self.id = 0;
            return 0;

        try:
            response = json.loads(response);
            monitor.update(id,response);
            return 1;
        except Exception as e:
            return 0;
