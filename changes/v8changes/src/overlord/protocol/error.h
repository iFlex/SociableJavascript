#ifndef CP_ERROR
#define CP_ERROR

#include<string>
#include "../json/json.h"
namespace ControlProtocol {

  class error {
    bool hasError;
    std::string errorMessage;
    //methods
  public:
    error();
    error(std::string errorMsg);
    std::string getMessage();
    void setMessage(std::string msg);
    bool exists();
    //serialising
    void serialise(Json::Value &v);
    void deserialise(Json::Value v);
  };

}

#endif
