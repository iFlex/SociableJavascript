#include "command.h"
#include "action.h"

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

  std::string command::serialise() {
    Json::Value root;
    Json::Value * isolates;

    root["global"] = global.serialise();

    if(this->nrIsolates > 0) {
      isolates = new Json::Value[this->nrIsolates];
      for( int i = 0; i < this->nrIsolates; ++i )
          isolates[i] = this->isolates[i].serialise();
      root["isolates"] = isolates;
    }

    Json::StyledWriter writer;
    return writer.write( root );
  }

  void command::deserialise(std::string str){
    Json::Value root;   // will contains the root value after parsing.
    Json::Reader reader;

    //bool success = reader.parse(str,str+strlen(str),root);
    bool success = reader.parse(str,root);

    if(success){
      if(!root["global"].empty())
        global.deserialise(root["global"]);
    } else {
      overallError.setMessage("Bad protocol formatting");
    }
  }
}
