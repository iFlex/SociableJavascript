#include "error.h"

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
  void error::deserialise( Json::Value v) {
    
    if(!v["error"].empty()){
      errorMessage = v["error"].asString();
      hasError = true;
    }

  }

  void error::serialise( Json::Value &v){
    if(hasError)
      v["error"] = errorMessage;
  }
}
