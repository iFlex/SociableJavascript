#include "overlord.h"

using namespace std;
using namespace ControlProtocol;

void * Overlord::serve(void * data){
    Overlord *overlord = (Overlord *) data;
    
    int connFd,listenFd;
    socklen_t len; //store size of the address
  
    struct sockaddr_in svrAdd, clntAdd;
  
    //create socket
    listenFd = socket(AF_INET, SOCK_STREAM, 0);
    
    if(listenFd < 0)
    {
        cerr << "Overlord:: Cannot open socket" << endl;
        return 0;
    }
    
    bzero((char*) &svrAdd, sizeof(svrAdd));
    
    svrAdd.sin_family = AF_INET;
    svrAdd.sin_addr.s_addr = INADDR_ANY;
    svrAdd.sin_port = htons(overlord->port);
    
    //bind socket
    if(bind(listenFd, (struct sockaddr *)&svrAdd, sizeof(svrAdd)) < 0)
    {
        cerr << "Overlord::Cannot bind" << endl;
        return 0;
    }
    
    listen(listenFd, 5);
    
    len = sizeof(clntAdd);
    
    cout << "Overlord::Listening on port "<< overlord->port << endl;
    //this is where client connects. svr will hang in this mode until client conn
    connFd = accept(listenFd, (struct sockaddr *)&clntAdd, &len);

    if (connFd < 0) {
      cerr << "Overlord::Cannot accept connection" << endl;
      return 0;
    } else {
      cout << "Overlord::Connection successful" << endl;
    }
    
    cout << "Overlord:: New controller connected - Thread No: " << pthread_self() << endl;
    
    char test[300];
    bzero(test, 301);
    bool loop = false;
    
    command cmd(1);
    while(!loop)
    {    
        bzero(test, 301);
        
        
        read(connFd, test, 300);
        
        string tester (test);
        if(tester == "exit")
            break;

        cmd.deserialise(test);
        
    }
    cout << "\nClosing thread and conn" << endl;
    close(connFd);
    
    return 0;
}

Overlord::Overlord(int portNo, bool synchronous) {
    port = portNo;

    if(synchronous)
        serve(NULL);
    else
        pthread_create(&tid,NULL,Overlord::serve,(void *)this);
}