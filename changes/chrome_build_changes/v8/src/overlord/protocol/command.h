#ifndef CP_CMD
#define CP_CMD

#include "action.h"
#include "details.h"
#include "../json/json.h"
#include <string>

namespace ControlProtocol {
  class command {

  private:
    int nrIsolates;
    ControlProtocol::error overallError;
    ControlProtocol::action global;
    ControlProtocol::action *isolates;

  //methods
  public:
    void setNrIsolates(int);
    void setIsolateActions(ControlProtocol::action*);
    void setGlobalAction(ControlProtocol::action a);
    
    int getNrIsolates(){ return nrIsolates; }
    ControlProtocol::action * getIsolateActions(){ return isolates;} 
    ControlProtocol::action getGlobal() { return global; }
    ControlProtocol::error getError(){ return overallError; }

    std::string serialise();
    void deserialise(std::string);

    command();
    command(std::string);
  };

}

#endif
