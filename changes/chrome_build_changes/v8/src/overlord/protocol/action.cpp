#include "action.h"

namespace ControlProtocol {
  action::action() {

  }

  bool action::hasError(){
    return error.exists();
  }

  void action::setError(ControlProtocol::error e){
    error = e;
  }

  ControlProtocol::error action::getError(){
    return error;
  }

  ControlProtocol::details* action::getDetails(){
    return &detail;
  }

  Json::Value action::serialise(){
    Json::Value v;
    v["action"] = name;

    if(error.exists())
      error.serialise(v);
    else
      detail.serialise(v);

    return v;
  }

  void action::deserialise(Json::Value v){
    if(v["action"].empty()){
      error.setMessage("missing global action tag");
    } else {
      name = v["action"].asString();
      error.deserialise(v);
      if(!error.exists())
        detail.deserialise(v);
    }
  }
}
