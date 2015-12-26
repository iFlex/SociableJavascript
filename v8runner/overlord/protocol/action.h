#ifndef CP_ACTION
#define CP_ACTION

#include<string>
#include "error.h"
#include "details.h"
#include "../json/json.h"

namespace ControlProtocol{

  class action{
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
    Json::Value serialise();
    void deserialise(Json::Value v);
  };

}

#endif
