#requires the following binary files to be in the same directory:
#natives_blob.bin snapshot_blob.bin
g++ -I../../v8/ -c overlord/protocol/v8JSON.cpp -std=c++0x
g++             -c overlord/overlord.cc -std=c++0x
g++ -I../../v8/ -c v8JSON.cpp -o main.o -std=c++0x
g++ -o v8JSON.bin overlord.o v8JSON.o main.o  -Wl,--start-group ../../v8/out/native/obj.target/{tools/gyp/libv8_{base,libbase,external_snapshot,libplatform},third_party/icu/libicu{uc,i18n,data}}.a -Wl,--end-group -lrt -ldl -pthread -std=c++0x
