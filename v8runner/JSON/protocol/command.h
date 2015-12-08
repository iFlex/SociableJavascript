#ifndef CP_CMD
#define CP_CMD

#include "action.h"
#include "details.h"
#include "json/json.h"

namespace ControlProtocol {

  class command {

  private:

    int nrIsolates;
    ControlProtocol::action global;
    ControlProtocol::action * isolates;

  //methods
  public:
    command( int );
    void setGlobalAction(ControlProtocol::action a);
    std::string serialise();
  };

}

#endif
