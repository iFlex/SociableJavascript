#requires the following binary files to be in the same directory:
#natives_blob.bin snapshot_blob.bin
g++ -I../../v8/ v8JSON.cpp -o v8JSON.bin -Wl,--start-group ../../v8/out/native/obj.target/{tools/gyp/libv8_{base,libbase,external_snapshot,libplatform},third_party/icu/libicu{uc,i18n,data}}.a -Wl,--end-group -lrt -ldl -pthread -std=c++0x
