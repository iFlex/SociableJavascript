#include "overlord.h"
#include "instance.h"

#include <string.h>
#include <iostream>

using namespace std;
using namespace ControlProtocol;
using namespace v8;

#define CMD_SEPARATOR ';'

void handleIsolateRequest(int, action, command &);
void handleGlobalRequests(command &response, action command);

void overlordTestCli(){
    cout<<"Overlord cli tester"<<endl;
    command rsp;
    while(1){
        action a;
        details *d = a.getDetails();

        int nris = v8::internal::Isolate::getActiveIsolatesCount();
        action *ast = new action[nris];
        rsp.setNrIsolates(nris);
        rsp.setIsolateActions(ast);

        string s;
        cout<<"*>";
        cin>>s;

        if(s == "stats"){
            a.name = "status";
            handleGlobalRequests(rsp,a);
            cout<<"*R:"<<rsp.serialise()<<endl;
            delete[] ast;
            continue;
        }

        else if(s == "kill"){
            a.name = "terminate";
        }

        else if(s == "set"){
            a.name = "set_heap_size";
            cout<<"*Heap size:"<<endl;
            cin>>d->heap;    
        }
        
        else if(s == "setm"){
            a.name = "set_max_heap_size";
            cout<<"*Heap size(MB):"<<endl;
            cin>>d->heap;    
        }
        
        else if(s == "exec"){
            string script;
            cout<<"*Input path to script:";
            cin>>script;
            cout<<endl;

            instance::parallelExec(script.c_str());
            delete[] ast;
            continue;
        }

        else if(s == "exit")
            return;
        else 
            cout<<"*Unknown command!";
        handleIsolateRequest(0,a,rsp);
        cout<<"*R:"<<rsp.serialise()<<endl;
        delete[] ast;
    }
}

class ArrayBufferAllocator : public v8::ArrayBuffer::Allocator {
 public:
  virtual void* Allocate(size_t length) {
    void* data = AllocateUninitialized(length);
    return data == NULL ? data : memset(data, 0, length);
  }
  virtual void* AllocateUninitialized(size_t length) { return malloc(length); }
  virtual void Free(void* data, size_t) { free(data); }
};

void * Overlord::serve(void * data){
    //overlordTestCli();

    int portNo = 15000;//*((int *)data);
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
        
    command resp;
    while(true){
        cout << "Overlord::Listening on port "<< portNo << endl;
        //this is where client connects. svr will hang in this mode until client conn
        connFd = accept(listenFd, (struct sockaddr *)&clntAdd, &len);

        if (connFd < 0) {
          cerr << "Overlord::Cannot accept connection" << endl;
          return 0;
        } else {
          cout << "Overlord::Connection successful" << endl;
        }
        
        cout << "Overlord:: New controller connected - Thread No: " << pthread_self() << endl;
        
        char buffer[2000],strCmd[2000];
        char c,*jsonStr,*cmdend;
        bool loop = true;
        int strLen = 0;
        
        c = ' ';
        strCmd[0] = 0;    
        while(loop)
        {
            cmdend = &c;
            while(*cmdend){
                strLen = (int) read(connFd, buffer, 2000);
                if( strLen < 1){
                    loop = false;
                    break;
                }
                buffer[strLen] = 0;
                //cout<<"Part str:"<<buffer<<endl;

                cmdend = strchr(buffer,CMD_SEPARATOR);
                *cmdend = 0;
                //overflow vulnerable code
                strcpy(strCmd,buffer);
            }
            
            if(!loop)
                break;

            if(base64::decode(strCmd,(int) strlen(strCmd),jsonStr)) {
                cout<<"Request_JSON:"<<jsonStr<<endl;

                string scommand(jsonStr);
                command cmd(scommand);
                Overlord::handleRequest(cmd,resp);
                cout<<"Responding..."<<endl;
                string r = resp.serialise();
                cout<<"Response_JSON:"<<r<<endl;
                const char* data = r.c_str();
                
                delete[] jsonStr;
                base64::encode(data,(int) strlen(data),jsonStr);
                
                buffer[0] = 0;
                for(int i = 1; i < 2000; ++i )
                    buffer[i] = CMD_SEPARATOR;
                strcpy(buffer,jsonStr);
                buffer[strlen(jsonStr)] = CMD_SEPARATOR;
                write(connFd, buffer, 1450);
            }
            
            strCmd[0] = 0;
            char *start;
            do {

                strLen = (int) read(connFd, buffer, 2000);
                if( strLen < 1){
                    loop = false;
                    break;
                }
                buffer[strLen] = 0;
                //cout<<"Scavenging:"<<buffer<<endl;
                
                start = 0;
                for( int i = 0 ; i < strLen; ++i ) {
                    if( buffer[i] != CMD_SEPARATOR ) {
                        if(!start)
                            start = buffer+i;
                    } else {
                        buffer[i] = 0;
                        if(start)
                            break;
                    }
                }
            }while(!start);
            //overflow vulnerable code
            strcpy(strCmd,start);
            //cout<<"Remaining str:"<<strCmd<<endl;
        }
    }
    cout << "\nClosing thread and conn" << endl;
    close(connFd);
    
    return 0;
}

Overlord::Overlord(int portNo, bool synchronous) {
    port = portNo;

    if(synchronous)
        Overlord::serve((void *)(&port));
    else
        pthread_create(&tid,NULL,Overlord::serve,((void *)(&port)));
}

void handleIsolateRequest(int i, action cmd, command &response){
    cout<<"Working on isolate:"<<i<<endl;
    if(i >= (int)response.getNrIsolates()){
        cout<<"Invalid isolate ID"<<endl;
        return;
    }

    v8::internal::Isolate *isl = v8::internal::Isolate::getIsolate(i+1);
    if( isl == NULL ){//no such isolate
        cout<<"Isolate not found:"<<i<<endl;
        return;
    }
    
    v8::Isolate *isol = reinterpret_cast<v8::Isolate *>(isl); 

    action *actions    = response.getIsolateActions();
    details *detail    = actions[i].getDetails();
    details *param     = cmd.getDetails();

    //unsupported command
    //if( cmd.name == "terminate" ) {//terminate the isolate      
    //}

    if( cmd.name == "status" ){ //status report on idividual isolate 
        //v8::Locker l{isol}; - causes deadlock ...
        
        detail->heap       = (int) isl->getHeapSize();
        detail->throughput = isl->getThroughput();   
        actions[i].name    = "update";
    }

    if( cmd.name == "set_max_heap_size" ){
        isl->heap()->setMaxOldGenerationSize(param->heap);
        actions[i].name    = "max_heap_size_set";
    }

    if( cmd.name == "set_heap_size"){
        isl->setTargetHeapSize(param->heap);
        actions[i].name    = "target_heap_size_set";
    }

    //TODO: execute
    if( cmd.name == "execute"){
        //using parameter path
    }

    //TODO: load
    if(cmd.name == "load"){
        //using path parameter
    }
}

void handleGlobalRequests(command &response, action command){
    if(command.name == "status"){

        int nrIsolates = (int) response.getNrIsolates();
        cout<<"Performing request on "<<nrIsolates<<" isolates"<<endl;
        for( int i = 0; i < nrIsolates ; ++i )
            handleIsolateRequest(i,command,response);

    } else if (command.name == "execute"){
        instance::parallelExec(command.getDetails()->path.c_str());
    }
}

void Overlord::handleRequest(command &cmd, command &response){
    int nrIsolates = v8::internal::Isolate::getActiveIsolatesCount();
    //cout<<"Active isolates:"<<nrIsolates<<endl;
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
            handleGlobalRequests(response,cmd.getGlobal());    
        }

        int len = (int) cmd.getNrIsolates();
        action * actions = cmd.getIsolateActions();
        for( int i = 0; i < len; ++i )
            handleIsolateRequest(i,actions[i],response);
    }
}