#ifndef CP_DETAILS
#define CP_DETAILS

#include "../json/json.h"
#include<string>

namespace ControlProtocol {

  class details {
  public:
    //properties
    int old_space,new_space,code_space,heap,available,maxHeapSize,suggestedHeapSize;
    double throughput;
    std::string path;
    //methods
    details();
    void deserialise(Json::Value obj);
    void serialise(Json::Value &obj);
  };

}

#endif
