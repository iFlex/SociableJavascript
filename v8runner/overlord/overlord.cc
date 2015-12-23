#include "overlord.h"

using namespace std;
using namespace ControlProtocol;

void * Overlord::serve(void * data){
    int portNo = *((int *)data);
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
    svrAdd.sin_port = htons(portNo);
    
    //bind socket
    if(bind(listenFd, (struct sockaddr *)&svrAdd, sizeof(svrAdd)) < 0)
    {
        cerr << "Overlord::Cannot bind" << endl;
        return 0;
    }
    
    listen(listenFd, 5);
    
    len = sizeof(clntAdd);
    
    cout << "Overlord::Listening on port "<< portNo << endl;
    while(true){
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

        command resp(1);
        while(!loop)
        {    
            bzero(test, 301);
            if(read(connFd, test, 300) == -1)
                break;
            
            string tester (test);
            cout<<"Processing("<<strlen(test)<<")"<<tester<<endl;
            if(tester == "exit")
                break;

            command cmd(test);
            handleRequest(cmd,resp);

            char *data = resp.serialise();
            write(connFd, data, strlen(data));
            delete data;
        }
    }
    cout << "\nClosing thread and conn" << endl;
    close(connFd);
    
    return 0;
}

Overlord::Overlord(int portNo, bool synchronous) {
    port = portNo;

    if(synchronous)
        Overlord::serve((void *)&port);
    else
        pthread_create(&tid,NULL,Overlord::serve,(void *)&port);
}

void handleIsolateRequest(int i, action a){
    v8::internal::Isolate *isl = v8::internal::Isolate::getIsolate(i);
    if( isl == NULL )//no such isolate
        return;

}

void handleGlobalReuqests(command &response, string command){
    if(command == "status"){
        v8::internal::Isolate *isolate;
        action *actions = response.getIsolateActions();
        details *detail;
        
        int nrIsolates = response.getNrIsolates();
        for( int i = 0; i < nrIsolates ; ++i ){
            isolate = v8::internal::Isolate::getIsolate(i);
            detail = actions[i].getDetails();
            detail->heap = isolate->getHeapSize();
            detail->throughput = isolate->getThroughput();
        }
    }
}

void Overlord::handleRequest(command &cmd, command &response){
    int nrIsolates = v8::internal::Isolate::getActiveIsolatesCount();
    cout<<"Active isolates:"<<nrIsolates<<endl;
    response.setNrIsolates(nrIsolates);
    action *actions = new action[nrIsolates];
    response.setIsolateActions(actions);

    if(cmd.getError().exists()) {//there's an error or there is no global action
        cout<<"Error:"<<cmd.getError().getMessage()<<endl;
    } else {
        if(cmd.getGlobal().getError().exists())
            cout<<"Global action error:"<<cmd.getGlobal().getError().getMessage()<<endl;
        else {
            cout<<"Global Command "<<cmd.getGlobal().name<<endl;
            handleGlobalReuqests(response,cmd.getGlobal().name);    
        }

        cout<<"Nr isolates:"<<cmd.getNrIsolates()<<endl;
        int len = cmd.getNrIsolates();
        action * actions = cmd.getIsolateActions();
        for( int i=0; i<cmd.getNrIsolates(); ++i )
            handleIsolateRequest(i,actions[i]);
    }
}