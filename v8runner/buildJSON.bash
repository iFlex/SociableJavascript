#requires the following binary files to be in the same directory:
#natives_blob.bin snapshot_blob.bin
g++ -c overlord/protocol/action.cpp -std=c++0x
g++ -c overlord/protocol/command.cpp -std=c++0x
g++ -c overlord/protocol/details.cpp -std=c++0x
g++ -c overlord/protocol/error.cpp -std=c++0x

g++ -I./overlord -c overlord/json/jsoncpp.cpp -std=c++0x
g++ -I../../v8/ -c overlord/overlord.cc -std=c++0x
g++ -I../../v8/ -c v8JSON.cpp -o main.o -std=c++0x
g++ -o v8JSON.bin details.o action.o command.o error.o overlord.o jsoncpp.o main.o  -Wl,--start-group ../../v8/out/native/obj.target/{tools/gyp/libv8_{base,libbase,external_snapshot,libplatform},third_party/icu/libicu{uc,i18n,data}}.a -Wl,--end-group -lrt -ldl -pthread -L ~/custom_libs -ljsoncpp -std=c++0x