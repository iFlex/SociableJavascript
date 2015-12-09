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

static std::string readInputTestFile(const char* path) {
  FILE* file = fopen(path, "rb");
  if (!file)
    return std::string("");
  fseek(file, 0, SEEK_END);
  long size = ftell(file);
  fseek(file, 0, SEEK_SET);
  std::string text;
  char* buffer = new char[size + 1];
  buffer[size] = 0;
  if (fread(buffer, 1, size, file) == (unsigned long)size)
    text = buffer;
  fclose(file);
  delete[] buffer;
  return text;
}

Json::Value decode(const char * str) {
  std::string err;
  Json::Value root;   // will contains the root value after parsing.
  Json::Reader reader;

  bool success = reader.parse(str,str+strlen(str),root);

  if(success){
    cout<<"Reading test property to check correct encoding"<<endl;
    cout<<root["test"]<<endl;
  } else {
    cout<<"error parsing"<<endl;
    cout<<reader.getFormattedErrorMessages()<<endl;
  }
  return root;
}

void encode(Json::Value root){
  Json::Reader reader;
  Json::StyledWriter writer;
  // Make a new JSON document for the configuration. Preserve original comments.
  root["subtree"] = "abc";
  std::string outputConfig = writer.write( root );

  // And you can write to a stream, using the StyledWriter automatically.
  std::cout << root << std::endl;
}

int main(){
  printf("JSON Tester\n");
  ControlProtocol::command cmd(5);//just one isolate
  ControlProtocol::action request;
  request.name = "get_isolates";

  ControlProtocol::details * m = request.getDetails();
  m->old_space = 123;

  cmd.setGlobalAction(request);
  std::cout<<"output:"<<cmd.serialise()<<endl;

  ControlProtocol::command dcmd(5);
  dcmd.deserialise(cmd.serialise());

  std::cout<<"after deserialisation::"<<dcmd.serialise()<<endl;
  std::cout<<"Say something"<<std::endl;
  char c[100];
  scanf("%s",c);
  encode(decode(c));
  return 0;
}
