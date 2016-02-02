import json

class Configuration:
	def __init__(self):
		self.config = {}
		try:
			f = open("MonitorConfig.txt");
			self.config = json.loads(f)
		except Exception as e:
			print "Failed to read configuration";

	def configure(self,name,object):
		if name in self.config:
			for cfg in self.config[name]:
				try:
					methodToCall = getattr(object, cfg[0]);
					methodToCall(cfg[1])
				except Exception as e:
					print "Failed to configure "+str(name)+" > "+str(cfg)