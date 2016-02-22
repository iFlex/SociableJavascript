echo "installing git"
sudo apt-get install git

echo "installing depot tools"
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH=pwd/depot_tools:"$PATH"

echo "cloning JsonCpp"
git clone https://github.com/open-source-parsers/jsoncpp.git

echo "building JsonCpp"
cd jsoncpp-master
echo "NEED COMMAND HERE"
cd ..

echo "cloning SociableJavascript"
git clone https://github.com/iFlex/SociableJavascript.git

echo "Downloading Modified V8"
echo "NEED COMMAND HERE"
cd v8
echo "Building V8 ..."
make native -j8

echo "Building V8Wrapper..."
cd ../SociableJavascript/v8runner/
./build

echo "Installing MatPlotLib"
apt-get install python-matplotlib

echo "READY"