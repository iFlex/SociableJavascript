#!/usr/bin
import sys
import os

source = "v8wrapper"
if  len(sys.argv)>1:
	source = sys.argv[1];
print "Building "+source;

#print os.system("g++ -I../../v8/ " + source + ".cpp -o " + source + ".bin -Wl,--start-group "  +
#"../../v8/out/native/obj.target/{tools/gyp/libv8_{base,libbase,external_snapshot,libplatform}" +
#",third_party/icu/libicu{uc,i18n,data}}.a -Wl,--end-group -lrt -ldl -pthread -std=c++0x");

print os.system("g++ -I../../v8/ v8wrapper.cpp -o v8wrapper.bin -Wl,--start-group ../../v8/out/native/obj.target/{tools/gyp/libv8_{base,libbase,external_snapshot,libplatform},third_party/icu/libicu{uc,i18n,data}}.a -Wl,--end-group -lrt -ldl -pthread -std=c++0x");
