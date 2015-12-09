#include<stdio.h>
#include<iostream>
#include "protocol/command.h"

int main(){
  str::string address;
  int portNo;

  cout<<"V8 Overlor commander. CLI interface"<<endl;
  cout<<"Input the V8's address"<<endl;
  cin>>address>>endl;
  cout<<"Port:"<<endl;
  cin>>port>>endl;

  int listenFd, portNo;
  struct sockaddr_in svrAdd;
  struct hostent *server;

  if((portNo > 65535) || (portNo < 2000))
  {
      cerr<<"Please enter port number between 2000 - 65535"<<endl;
      return 0;
  }

  cout<<"Connecting to "<<address<<":"<<port<<endl;
  //create client skt
  listenFd = socket(AF_INET, SOCK_STREAM, 0);

  if(listenFd < 0)
  {
      cerr << "Cannot open socket" << endl;
      return 0;
  }

  server = gethostbyname(address);

  if(server == NULL)
  {
      cerr << "Host does not exist" << endl;
      return 0;
  }

  bzero((char *) &svrAdd, sizeof(svrAdd));
  svrAdd.sin_family = AF_INET;

  bcopy((char *) server -> h_addr, (char *) &svrAdd.sin_addr.s_addr, server -> h_length);

  svrAdd.sin_port = htons(portNo);

  int checker = connect(listenFd,(struct sockaddr *) &svrAdd, sizeof(svrAdd));

  if (checker < 0)
  {
      cerr << "Cannot connect!" << endl;
      return 0;
  }

  //send stuff to server
  for(;;)
  {
      std::string cmd;
      cin>>cmd>>endl;

      write(listenFd, s, strlen(s));
  }
  return 0;
}
