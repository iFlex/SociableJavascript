#include "command.h"
#include "action.h"
using namespace std;
using namespace v8;

namespace ControlProtocol {

  command::command(int nrIsol){
    this->nrIsolates = nrIsol;
    this->isolates = new ControlProtocol::action[nrIsol];
  }

  ControlProtocol::action command::getGlobal(){
    return global;
  }

  void command::setGlobalAction(ControlProtocol::action a){
      global = a;
  }

  char * command::serialise() {
    v8::Local<v8::Value> root = v8json.newEmptyObject();
    v8json.setValue(root,"global",global.serialise());

    /*if(this->nrIsolates > 0) {
      isolates = new v8::Local<v8::Value>[this->nrIsolates];
      for( int i = 0; i < this->nrIsolates; ++i )
          isolates[i] = this->isolates[i].serialise();
      root["isolates"] = isolates;
    }*/

    return v8json.encode(&root);
  }

  void command::deserialise(char *info){
    Local<Value> root = v8json.decode(info);

    if(root->IsNull()){
      overallError.setMessage("Bad protocol formatting");
    } else {
      global.deserialise(v8json.getValue(root,"global"));
    }
  }
}
