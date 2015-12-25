#include <string.h>
#include <cstring>
#include <unistd.h>
#include <stdio.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <strings.h>
#include <stdlib.h>
#include <string>
#include <time.h>
#include <vector>

#include "json/json.h"
#include "protocol/command.h"

using namespace std;

int main(){
  printf("JSON Tester\n");
  ControlProtocol::action isl[2];
  ControlProtocol::command cmd;//just one isolate
  ControlProtocol::action request;
  request.name = "set_old_space";
  cmd.setNrIsolates(2);
  cmd.setIsolateActions(isl);
  
  ControlProtocol::details * m = request.getDetails();
  m->old_space = 123;

  cmd.setGlobalAction(request);
  std::cout<<"output:"<<cmd.serialise()<<endl;

  ControlProtocol::command dcmd;
  dcmd.deserialise(cmd.serialise());

  std::cout<<"after deserialisation::"<<dcmd.serialise()<<endl;
  std::cout<<"Say something"<<std::endl;

  return 0;
}
