#include "details.h"
using namespace std;
using namespace v8;

namespace ControlProtocol {
  details::details(){
    old_space = new_space = code_space = heap = 0;
    path = "";
  }

  void details::deserialise(v8::Local<v8::Value> obj){
    old_space  = (int) v8json.getNumber(obj,"old_space");
    new_space  = (int) v8json.getNumber(obj,"new_space");
    code_space = (int) v8json.getNumber(obj,"code_space");
    heap       = (int) v8json.getNumber(obj,"heap");
    
    string p(v8json.getString(obj,"path"));
    path = p;
  }

  void details::serialise(v8::Local<v8::Value> &obj){
    v8json.setNumber(obj,"old_space",(double)old_space);
    v8json.setNumber(obj,"new_space",(double)new_space);
    v8json.setNumber(obj,"code_space",(double)code_space);
    v8json.setNumber(obj,"heap",(double)heap);
    v8json.setString(obj,"path",path.c_str());
  }
}
