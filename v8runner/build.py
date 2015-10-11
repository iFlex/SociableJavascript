#!/usr/bin
import sys
import subprocess

def checkPrerequisites():
	req = ["snapshot_blob.bin","natives_blob.bin"];
	for r in req:
		try:
			f = open(r,"rb");
			f.close();
		except Exception as e:
			print "Missing prerequisite in current folder:"+r;
			print e;			
			return False;
	return True;
	

source = "v8wrapper"
if  len(sys.argv)>1:
	source = sys.argv[1];
print "Building "+source;

build_command = [
"g++",
"-I~/level4/v8/",
str(source)+".cpp",
"-o",
str(source)+".bin",
"-Wl,",
"--start-group",
"~/level4/v8/out/native/obj.target/{tools/gyp/libv8_{base,libbase,external_snapshot,libplatform},third_party/icu/libicu{uc,i18n,data}}.a",
"--end-group",
"-lrt",
"-ldl",
"-pthread",
"-std=c++0x"
]

if checkPrerequisites():
	subprocess.call(build_command)

