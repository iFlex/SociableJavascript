#ifndef CP_ACTION
#define CP_ACTION

#include "error.h"
#include "details.h"
#include "v8JSON.h"
#include <string>

namespace ControlProtocol{

  class action{
    v8JSON v8json;
    ControlProtocol::error  error;
    ControlProtocol::details detail;

  public:
    std::string name;

    //methods
    action();
    bool hasError();
    void setError(ControlProtocol::error e);
    ControlProtocol::error getError();
    ControlProtocol::details * getDetails();
    /////////////////////
    v8::Local<v8::Value> serialise();
    void deserialise(v8::Local<v8::Value> v);
  };

}

#endif
