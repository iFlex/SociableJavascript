#include "details.h"

namespace ControlProtocol {
  details::details(){
    old_space = new_space = code_space = heap = 0;
    path = "";
  }

  void details::deserialise(Json::Value obj){
    old_space  = obj["old_space"].asInt();
    new_space  = obj["new_space"].asInt();
    code_space = obj["code_space"].asInt();
    heap       = obj["heap"].asInt();
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

    if(path.length())
      obj["path"] = path;
  }
}
