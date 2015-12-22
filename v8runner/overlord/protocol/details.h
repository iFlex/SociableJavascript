#ifndef CP_DETAILS
#define CP_DETAILS

#include<string>
#include "include/libplatform/libplatform.h"
#include "include/v8.h"
#include "src/api.h"
#include "v8JSON.h"

namespace ControlProtocol {

  class details {
  v8JSON v8json;
  public:
    //properties
    int old_space,new_space,code_space,heap;
    std::string path;
    //methods
    details();
    void deserialise(v8::Local<v8::Value> obj);
    void serialise(v8::Local<v8::Value> &obj);
  };

}

#endif
