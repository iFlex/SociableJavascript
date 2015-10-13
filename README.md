# SociableJavascript
Level 4 Individual Project @ University of Glasgow

This project aims to assess if a different heap size allocation alogrithm
would better suit the Google V8 JavaScript engine.

Setup ( UNIX based machine required )

1. apt-get install git
2. git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
3. export PATH=`pwd`/depot_tools:"$PATH"
4. fetch v8
5. change to v8 folder (cd v8)
6. make native
7. git clone https://github.com/iFlex/SociableJavascript.git
7. copy snapshot_blob.bin and natives_blob.bin from ./v8/out/native/ to ./SociableJavascript/memplot
