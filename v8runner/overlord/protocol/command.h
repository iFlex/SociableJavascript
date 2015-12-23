#ifndef CP_CMD
#define CP_CMD

#include "include/libplatform/libplatform.h"
#include "include/v8.h"
#include "src/api.h"
#include "v8JSON.h"

#include "action.h"
#include "details.h"
#include <string>

//WARANING: program seems to crash if two command objects are in the same scope. Could have to do with Local<Value>
namespace ControlProtocol {
  class command {

  private:
    v8JSON v8json;
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

    char * serialise();
    void deserialise(char *info);

    command(int);
    command(char *);
  };

}

#endif
