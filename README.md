# SociableJavascript
Level 4 Individual Project @ University of Glasgow

This project aims to assess if a different heap size allocation alogrithm
would better suit the Google V8 JavaScript engine.

Setup ( UNIX based machine required )

1. sudo apt-get install python-matplotlib
2. apt-get install git
3. git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
4. export PATH=`pwd`/depot_tools:"$PATH"
5. fetch v8
6. change to v8 folder (cd v8)
7. make native
8. git clone https://github.com/iFlex/SociableJavascript.git
9. copy snapshot_blob.bin and natives_blob.bin from ./v8/out/native/ to ./SociableJavascript/v8runner


Programming Environment Setup:
Sublime Text 3
CTags + CTags plugin for Sublime
ymcd autocompletion server
YcmdCompletion Sublime plugin
