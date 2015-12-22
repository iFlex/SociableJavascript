#ifndef CP_ERROR
#define CP_ERROR

#include "include/libplatform/libplatform.h"
#include "include/v8.h"
#include "src/api.h"
#include "v8JSON.h"

#include<string>

namespace ControlProtocol {
  class error {
    v8JSON v8json;
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
    void serialise(v8::Local<v8::Value> &v);
    void deserialise(v8::Local<v8::Value> v);
  };

}

#endif
