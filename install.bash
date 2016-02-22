installdr=$1
echo "INSTALL_DIR:"$installdr
cd $installdr
echo "-- Installing required software tools..."
echo "Installing git"
sudo apt-get install git
echo "Installing wget"
apt-get install wget
echo "installing cmake"
sudo apt-get install cmake
echo "Installing MatPlotLib"
apt-get install python-matplotlib
echo "installing depot tools"
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH=pwd/depot_tools:"$PATH"

echo "-- Cloning necessary repositories..."
echo "cloning JsonCpp"
git clone https://github.com/open-source-parsers/jsoncpp.git
echo "cloning SociableJavascript"
git clone https://github.com/iFlex/SociableJavascript.git

echo "-- Building dependencies"
echo "> Building JsonCpp"
cd jsoncpp
mkdir -p build/release
cd build/release
cmake -DCMAKE_BUILD_TYPE=release -DBUILD_STATIC_LIBS=ON -DBUILD_SHARED_LIBS=OFF -DARCHIVE_INSTALL_DIR=. -G "Unix Makefiles" ../..
make
echo "Moving JsonCpp library in the right place for the V8 build process... ($installdr/custom_libs/)"
mkdir $installdr/custom_libs
cp ./src/lib_json/libjsoncpp.a $installdr/custom_libs/

cd $installdr
echo "-- Downloading Modified V8"
wget  -O $installdr/v8.zip "http://linktov8zipfile"
unzip v8.zip
cd v8
echo "-- Building V8 ..."
make native -j8

cd $installdr
echo "Building V8Wrapper..."
cd SociableJavascript/v8runner/
./build.bash
echo "-- DONE --"
