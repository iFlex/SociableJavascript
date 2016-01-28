#include "command.h"
#include "action.h"
#include <string.h>

using namespace std;

namespace ControlProtocol {

  command::command(){
    nrIsolates = 0;
    isolates = NULL;
  }

  command::command(string info){
    nrIsolates = 0;
    isolates = NULL;
    deserialise(info);
  }

  void command::setNrIsolates(int nrIsol){
    nrIsolates = nrIsol;
  }
    
  void command::setGlobalAction(ControlProtocol::action a){
      global = a;
  }

  void command::setIsolateActions(ControlProtocol::action* actions){
    isolates = actions;
  }

  string command::serialise() {
    Json::Value root;
    root["global"] = global.serialise();

    if(this->nrIsolates > 0) {
      Json::Value inner;
      char index[25]; 
      for( int i = 0; i < this->nrIsolates; ++i ) {
        sprintf(index,"%d",i+1); 
        inner[index] = this->isolates[i].serialise();
      }
      root["TotalIsolates"] = this->nrIsolates;
      root["isolates"] = inner;
    }

    Json::StyledWriter writer;
    return writer.write( root );
  }

  void command::deserialise(string info){
    Json::Value root;   // will contains the root value after parsing.
    Json::Reader reader;

    bool success = reader.parse(info,root);

    if(success){
      if(!root["global"].empty())
        global.deserialise(root["global"]);
        
      //if(this->nrIsolates > 0 && this->isolates != NULL)
      //  delete this->isolates;
      
      this->nrIsolates = root["TotalIsolates"].asInt();
      if(this->nrIsolates > 0) {
        Json::Value inner = root["isolates"];
        
        this->isolates = new action[nrIsolates];
        char index[25];
        for( int i = 0; i < this->nrIsolates; ++i ) {
          sprintf(index,"%d",i+1);
          this->isolates[i].deserialise(inner[index]);
        }
      }
    } else {
      overallError.setMessage("Bad protocol formatting");
    }
  }
}