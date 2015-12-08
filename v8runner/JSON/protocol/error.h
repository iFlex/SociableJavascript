#ifndef CP_ERROR
#define CP_ERROR

#include<string>

namespace ControlProtocol {

  class error {
    bool hasError;
    std::string errorMessage;
    //methods
  public:
    error();
    error(std::string errorMsg);
    std::string getMessage();
    void setMessage(std::string msg);
    bool exists();
  };

}

#endif
