#ifndef CP_CMD
#define CP_CMD

#include "action.h"
#include "details.h"
#include "json/json.h"
#include <string>
namespace ControlProtocol {

  class command {

  private:

    int nrIsolates;
    ControlProtocol::error overallError;
    ControlProtocol::action global;
    ControlProtocol::action * isolates;

  //methods
  public:
    command( int );
    void setGlobalAction(ControlProtocol::action a);
    ControlProtocol::action getGlobal();

    std::string serialise();
    void deserialise(std::string info);
  };

}

#endif
