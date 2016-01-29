echo "installing git"
apt-get install git

echo "installing depot tools"
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH=pwd/depot_tools:"$PATH"

echo "cloning SociableJavascript"
git clone https://github.com/iFlex/SociableJavascript.git
cd SociableJavascript
fetch v8
cd v8
echo "Make V8"
make native -j8

