#include "command.h"
#include "action.h"

namespace ControlProtocol {

  command::command(int nrIsol){
    this->nrIsolates = nrIsol;
    this->isolates = new ControlProtocol::action[nrIsol];
  }

  void command::setGlobalAction(ControlProtocol::action a){
      global = a;
  }

  std::string command::serialise() {
    Json::Value root;
    Json::Value * isolates;

    root["global"] = global.toJson();

    if(this->nrIsolates > 0) {
      isolates = new Json::Value[this->nrIsolates];
      for( int i = 0; i < this->nrIsolates; ++i )
          isolates[i] = this->isolates[i].toJson();
      root["isolates"] = isolates;
    }

    Json::StyledWriter writer;
    return writer.write( root );
  }
}
