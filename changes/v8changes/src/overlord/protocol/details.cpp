#include "details.h"

namespace ControlProtocol {
  details::details(){
    old_space = new_space = code_space = heap = 0;
    path = "";
  }

  void details::deserialise(Json::Value obj){
    if(!obj["old_space"].empty())
      old_space  = obj["old_space"].asInt();

    if(!obj["new_space"].empty())
      new_space  = obj["new_space"].asInt();

    if(!obj["code_space"].empty())
      code_space = obj["code_space"].asInt();

    if(!obj["heap"].empty())
      heap       = obj["heap"].asInt();

    if(!obj["available"].empty())
      heap       = obj["available"].asInt();

    if(!obj["maxHeapSize"].empty())
      maxHeapSize = obj["maxHeapSize"].asInt();

    if(!obj["suggestedHeapSize"].empty())
      suggestedHeapSize = obj["suggestedHeapSize"].asInt();

    if(!obj["throughput"].empty())
      throughput       = obj["throughput"].asDouble();

    if(!obj["path"].empty())
      path       = obj["path"].asString();    
  }

  void details::serialise(Json::Value &obj){
    if(old_space)
      obj["old_space"] = old_space;

    if(new_space)
      obj["new_space"] = new_space;

    if(code_space)
      obj["code_space"] = code_space;

    if(heap)
      obj["heap"] = heap;

    if(maxHeapSize)
      obj["maxHeapSize"] = maxHeapSize;

    if(suggestedHeapSize)
      obj["suggestedHeapSize"] = suggestedHeapSize;

    if(available)
      obj["available"] = available;

    obj["throughput"] = throughput;
    
    if(path.length())
      obj["path"] = path;
  }
}
