f = open("test.txt","r");

while True:
	for line in f:
		print line;

	kr = raw_input("keep reading?");
	if kr == "no":
		break;
		
f.close();
print "DONE";