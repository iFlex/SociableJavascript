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

  Json::Value action::toJson(){
    Json::Value v;
    v["action"] = name;

    detail.serialise(v);

    return v;
  }

  void action::fromJson(Json::Value v){
    name = v["action"].asString();

  }
}
