f = open("test.txt","w");

while True:
	cmd = input("no lines:")
	bfr = "a"*80
	if cmd == 0:
		break

	while cmd > 0:
		f.write(bfr);
		cmd -= 1


raw_input("CLOSE");
f.close();
print "DONE";