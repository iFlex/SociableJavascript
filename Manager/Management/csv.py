#needs throwig exceptions
class CSV:
	def __init__(self,filename):
		self.file = open(filename,"w");
		self.stage = 0;
		self.length = 0;

	def commitSchema(self,schema):
		if self.stage != 0:
			return

		for s in schema:
			self.file.write(str(s)+",")
		self.file.write("\n");

		self.length = len(schema)
		self.stage = 1

	def commitLine(self,line):
		if self.stage != 1:
			return

		for s in line:
			self.file.write(str(s)+",")
		self.file.write("\n");


	def close(self):
		self.file.close()
		self.stage = 2