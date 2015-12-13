#include<stdio.h>
#include<iostream>
#include "protocol/command.h"

using namespace std;

int main(){
  std::string address;
  int portNo;

  cout<<"V8 Overlor commander. CLI interface"<<std::endl;
  cout<<"Input the V8's address"<<std::endl;
  cin>>address>>std::endl;
  cout<<"Port:"<<std::endl;
  cin>>port>>std::endl;

  int listenFd, portNo;
  struct sockaddr_in svrAdd;
  struct hostent *server;

  if((portNo > 65535) || (portNo < 2000))
  {
      cerr<<"Please enter port number between 2000 - 65535"<<std::endl;
      return 0;
  }

  cout<<"Connecting to "<<address<<":"<<portNo<<std::endl;
  //create client skt
  listenFd = socket(AF_INET, SOCK_STREAM, 0);

  if(listenFd < 0)
  {
      cerr << "Cannot open socket" << std::endl;
      return 0;
  }

  server = gethostbyname(address);

  if(server == NULL)
  {
      cerr << "Host does not exist" << std::endl;
      return 0;
  }

  bzero((char *) &svrAdd, sizeof(svrAdd));
  svrAdd.sin_family = AF_INET;

  bcopy((char *) server -> h_addr, (char *) &svrAdd.sin_addr.s_addr, server -> h_length);

  svrAdd.sin_port = htons(portNo);

  int checker = connect(listenFd,(struct sockaddr *) &svrAdd, sizeof(svrAdd));

  if (checker < 0)
  {
      cerr << "Cannot connect!" << std::endl;
      return 0;
  }

  //send stuff to server
  for(;;)
  {
      std::string cmd;
      cin>>cmd>>std::endl;

      write(listenFd, s, strlen(s));
  }
  return 0;
}
