#ifndef CP_CMD
#define CP_CMD

#include "include/libplatform/libplatform.h"
#include "include/v8.h"
#include "src/api.h"
#include "v8JSON.h"

#include "action.h"
#include "details.h"
#include <string>

namespace ControlProtocol {
  class command {

  private:
    v8JSON v8json;
    int nrIsolates;
    ControlProtocol::error overallError;
    ControlProtocol::action global;
    ControlProtocol::action * isolates;

  //methods
  public:
    command( int );
    void setGlobalAction(ControlProtocol::action a);
    ControlProtocol::action getGlobal();

    char * serialise();
    void deserialise(char *info);
  };

}

#endif
