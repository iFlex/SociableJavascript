#include "error.h"

using namespace std;
using namespace v8;

namespace ControlProtocol {
  error::error(){
    hasError = false;
  }

  error::error(std::string errorMsg){
    hasError = true;
    this->errorMessage = errorMsg;
  }

  std::string error::getMessage(){
    if(hasError)
      return errorMessage;

    return "";
  }

  void error::setMessage(std::string msg){
    hasError = true;
    errorMessage = msg;
  }

  bool error::exists(){
    return hasError;
  }
  /////////////////////////////////////////////
  void error::deserialise( v8::Local<v8::Value> v) {
    string str(v8json.getString(v,"error"));
    if(str.size() > 0) {
      errorMessage = str;
      hasError = true;
    } 
  }

  void error::serialise( v8::Local<v8::Value> &v){
    if(*v == NULL)
      return;
    
    if(hasError)
      v8json.setString(v,"error",errorMessage.c_str());
  }
}
