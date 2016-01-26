import json
packet_size = 1450;
separator = ";"
def sendTo(soc,data):
	global packet_size,separator

	try:
		data = json.dumps(data);
	except Exception as e:
		print "Could not encode to JSON:"+str(e)
		return 1;

	data = data + separator*(packet_size - len(data));
	
	try:
		soc.send(data);
	except Exception as e:
		print "Network error:"+str(e)
		return 0;