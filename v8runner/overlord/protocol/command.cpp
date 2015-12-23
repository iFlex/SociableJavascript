#include "command.h"
#include "action.h"

using namespace std;
using namespace v8;

namespace ControlProtocol {

  command::command(int i){
  }
  
  command::command(char *info){
    deserialise(info);
  }

  void command::setNrIsolates(int nrIsol){
    this->nrIsolates = nrIsol;
  }

  void command::setIsolateActions(ControlProtocol::action* actions){
    this->isolates = actions;
  }

  void command::setGlobalAction(ControlProtocol::action a){
      global = a;
  }

  char * command::serialise() {
    v8::Local<v8::Value> root = v8json.newEmptyObject();
    v8json.setValue(root,"global",global.serialise());

    if(this->nrIsolates > 0) {
      Local<Value> inner = v8json.newEmptyObject();
      char index[25];
    
      for( int i = 0; i < this->nrIsolates; ++i ) {
        sprintf(index,"%d",i); 
        v8json.setValue(inner,index,this->isolates[i].serialise());
      }

      v8json.setNumber(root,"TotalIsolates",(double)this->nrIsolates);
      v8json.setValue(root,"isolates",inner);
    }

    return v8json.encode(&root);
  }

  void command::deserialise(char *info){
    Local<Value> root = v8json.decode(info);

    if(*root == NULL){
      overallError.setMessage("BAD_FORMATTING");
    } else {
      global.deserialise(v8json.getValue(root,"global"));

      if(this->nrIsolates > 0)
        delete this->isolates;

      this->nrIsolates = (int)v8json.getNumber(root,"TotalIsolates");
      if(this->nrIsolates > 0) {
        Local<Value> inner = v8json.getValue(root,"isolates");
        this->isolates = new action[nrIsolates];
        char index[25];
  
        for( int i = 0; i < this->nrIsolates; ++i ) {
          sprintf(index,"%d",i);
          Local<Value> rawAction = v8json.getValue(inner,index);
          this->isolates[i].deserialise(rawAction);
        }
      }
    }

  }
}
