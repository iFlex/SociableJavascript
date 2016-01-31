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
        handleIsolateRequest(1,a,rsp);
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

void * Overlord::run(void * data){
    //overlordTestCli();
    int connFd;
    
    std::string line("127.0.0.1");
    int portNo = 15000;//*((int *)data);
    struct sockaddr_in svrAdd;
    struct hostent *serverId = gethostbyname(line.c_str());
    string ipaddr = line.c_str(); 
    //Read config file
    ifstream config("V8RemoteControlConfig.txt");
    if( config && config.is_open() ){
        for(int i = 0; i < 2 && std::getline(config, line); ++i ) {
            if(!i) {
                serverId = gethostbyname(line.c_str()); 
                ipaddr = line.c_str();
            } else
                portNo   = atoi(line.c_str());  
        }
        config.close();
    }

    cout << "Overlord: Connecting... "<<line<<":"<<portNo<<endl;
    //create socket
    connFd = socket(AF_INET, SOCK_STREAM, 0);
    
    if(connFd < 0)
    {
        cerr << "Overlord:: Cannot open socket" << endl;
        return 0;
    }
    
    if( serverId == NULL ){
        cerr <<"Overlord:: Could not resolve server address" << endl;
        return 0;
    }

    bzero((char*) &svrAdd, sizeof(svrAdd));
    
    svrAdd.sin_family = AF_INET;
    bcopy((char *)serverId->h_addr, 
         (char *)&svrAdd.sin_addr.s_addr,
         serverId->h_length);
    svrAdd.sin_port = htons(portNo);
    
    //serve
    while(true){
        //Keep trying to connect to Monitor
        while(connect(connFd, (struct sockaddr *)&svrAdd, sizeof(svrAdd)) < 0){
            cerr << "Overlord::Could not connect to Monitor "<<ipaddr<<":"<<portNo<<endl;
        }

        cout << "Overlord::connection successful. Awaiting commands..." << endl;
        //this is where client connects. svr will hang in this mode until client conn
   
        char jsonStr[5005],buffer[2002],strCmd[2002];
        bool loop = true;
        int strLen = 0,index = 0;
        
        strCmd[0] = 0;    
        while(loop)
        {
            strLen = (int) read(connFd, buffer, 1450);
            if( strLen < 1){
                loop = false;
                break;
            }
            for( int i = 0; i < strLen; ++i ) {
                if(buffer[i] != CMD_SEPARATOR) {
                    if(index < 2000)
                        strCmd[index++] = buffer[i];
                    else
                        cout<<"#PACKET TOO LARGE, len > 2000. Will truncate at 2000 and will not likely decode."<<endl;
                } else {
                    strCmd[index] = 0;
                    if(index != 0 && base64::decode(strCmd,(int) strlen(strCmd),jsonStr)) {
                        //cout<<"Request_JSON:"<<jsonStr<<endl;

                        string scommand(jsonStr);
                        command cmd(scommand);
                        command resp;
                        Overlord::handleRequest(cmd,resp);
                        string r = resp.serialise();
                        //cout<<"Response_JSON:"<<r<<endl;
                        
                        base64::encode(r,jsonStr);
                        int j=0;
                        for( j = (int) strlen(jsonStr); j < 2000 ; ++j )
                            jsonStr[j] = CMD_SEPARATOR;
                            
                        write(connFd, jsonStr, 1450);
                    }
                    index = 0;    
                }
            }
        }
    }
    cout << "\nClosing thread and conn" << endl;
    close(connFd);
    
    return 0;
}

Overlord::Overlord(int portNo, bool synchronous) {
    port = portNo;

    if(synchronous)
        Overlord::run((void *)(&port));
    else
        pthread_create(&tid,NULL,Overlord::run,((void *)(&port)));
}

void handleIsolateRequest(int i, action cmd, command &response){
    if(i > (int)response.getNrIsolates() || i < 1){
        cout<<"Invalid isolate ID"<<endl;
        return;
    }

    v8::internal::Isolate *isl = v8::internal::Isolate::getIsolate(i);
    if( isl == NULL ){//no such isolate
        cout<<"Isolate not found:"<<i<<endl;
        return;
    }
    
    //v8::Isolate *isol = reinterpret_cast<v8::Isolate *>(isl); 
    int actIndex = i-1;
    action  *actions    = response.getIsolateActions();
    details *detail     = actions[actIndex].getDetails();
    details *param      = cmd.getDetails();

    if(actions == NULL)
        return;
    //unsupported command
    //if( cmd.name == "terminate" ) {//terminate the isolate      
    //}

    if( cmd.name == "status" ){ //status report on idividual isolate 
        //v8::Locker l{isol}; - causes deadlock ...
        
        detail->heap       = (int) isl->getHeapSize();
        detail->throughput = isl->getThroughput();
        detail->available  = (int) isl->getAvailableHeapSize();  
        detail->maxHeapSize = (int) isl->getTargetHeapSize(); 
        actions[actIndex].name    = "update";
    }

    if( cmd.name == "set_max_heap_size" ){
        isl->heap()->setMaxOldGenerationSize(param->heap);
        actions[actIndex].name    = "max_heap_size_set";
    }

    if( cmd.name == "set_heap_size"){
        isl->setTargetHeapSize(param->heap);
        actions[actIndex].name    = "target_heap_size_set";
    }
}

void handleGlobalRequests(command &response, action command){
    if(command.name == "status"){

        int nrIsolates = (int) response.getNrIsolates();
        //cout<<"Performing request on "<<nrIsolates<<" isolates"<<endl;
        for( int i = 0; i < nrIsolates ; ++i )
            handleIsolateRequest(i+1,command,response);

    } else if (command.name == "execute"){
        cout<<"Executing script:"<<command.getDetails()->path.c_str()<<endl;
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
            //cout<<"Global Command "<<cmd.getGlobal().name<<endl;
            handleGlobalRequests(response,cmd.getGlobal());    
        }

        int len = (int) cmd.getNrIsolates();
        action * iactions = cmd.getIsolateActions();
        if(iactions != NULL){
            for( int i = 0; i < len; ++i ){
                handleIsolateRequest(i+1,iactions[i],response);
            }
        }
    }
}