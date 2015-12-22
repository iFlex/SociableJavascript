#include "action.h"
#include "error.h"
#include "details.h"
#include "command.h"
#include "v8JSON.h"
#include <string>

using namespace std;
using namespace v8;

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

  Local<Value> action::serialise(){
    Local<Value> v = v8json.newEmptyObject();
    v8json.setString(v,"action",name.c_str());
    
    if(error.exists())
      error.serialise(v);
    else
      detail.serialise(v);

    return v;
  }

  void action::deserialise(Local<Value> v){
    string str(v8json.getString(v,"action"));

    if(str.size() == 0){
      error.setMessage("missing global action tag");
    } else {
      name = str;
      error.deserialise(v);
      if(!error.exists())
        detail.deserialise(v);
    }
  }
}
