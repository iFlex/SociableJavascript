#include "overlord.h"
#include <string.h>
#include <iostream>
using namespace std;
using namespace ControlProtocol;
using namespace v8;

void handleIsolateRequest(int, action, command &);

void onePageFreeTest(){
    v8::internal::Isolate *isl = v8::internal::Isolate::getIsolate(1);
    if(isl)
        isl->setTargetHeapSize((int)(isl->getHeapSize() - v8::internal::Page::kPageSize));
}

void overlordTestCli(){
    command rsp;
    while(1){
        action a;
        details *d = a.getDetails();
        action *ast = new action[1];
        rsp.setNrIsolates(1);
        rsp.setIsolateActions(ast);

        string s;
        cout<<">";
        cin>>s;
        if( s == "x" ){
            onePageFreeTest();
            continue;
        }

        if(s == "stats"){
            a.name = "status";
        }
        if(s == "kill"){
            a.name = "terminate";
        }
        if(s == "set"){
            a.name = "set_heap_size";
            cout<<"Heap size:"<<endl;
            cin>>d->heap;    
        }
        if(s == "setm"){
            a.name = "set_max_heap_size";
            cout<<"Heap size(MB):"<<endl;
            cin>>d->heap;    
        }
        if(s == "exit")
            return;
        handleIsolateRequest(0,a,rsp);
        cout<<"R:"<<rsp.serialise()<<endl;
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
    overlordTestCli();

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
        
    cout << "Overlord::Listening on port "<< portNo << endl;
    command resp;
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
        
        char test[2000];
        bool loop = false;
        char *jsonStr;
        while(!loop)
        {    
            bzero(test, 2000);
            if(read(connFd, test, 500) == -1)
                break;
            
            cout<<"Processing("<<strlen(test)<<")"<<test<<endl;
            if(base64::decode(test,strlen(test),jsonStr)) {
                
                string scommand(jsonStr);
                command cmd(scommand);
                Overlord::handleRequest(cmd,resp);

                string r = resp.serialise();
                cout<<"Response:"<<r<<endl;
                const char* data = r.c_str();
                cout<<"response len:"<<strlen(data)<<endl;
                
                delete[] jsonStr;
                base64::encode(data,strlen(data),jsonStr);
                bzero(test,2000);
                strcpy(test,jsonStr);
                write(connFd, test, 1450);
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
        Overlord::serve((void *)(&port));
    else
        pthread_create(&tid,NULL,Overlord::serve,((void *)(&port)));
}

void handleIsolateRequest(int i, action cmd, command &response){
    cout<<"NrIsolates:"<<(int)response.getNrIsolates();
    if(i >= (int)response.getNrIsolates())
        return;

    v8::internal::Isolate *isl = v8::internal::Isolate::getIsolate(i+1);
    if( isl == NULL ){//no such isolate
        cout<<"Isolate not found:"<<i<<endl;
        return;
    }
    
    action *actions = response.getIsolateActions();
    details *detail    = actions[i].getDetails();
    details *param     = cmd.getDetails();
    if( cmd.name == "terminate" ) {//terminate the isolate
        v8::Isolate *isol = reinterpret_cast<v8::Isolate *>(isl); 
        v8::Locker l(isol);
        //isol->Exit();
        isol->Dispose();
        v8::Unlocker u(isol);

        actions[i].name = "terminated";
    }

    if( cmd.name == "status" ){ //status report on idividual isolate 
        detail->heap       = (int) isl->getHeapSize();
        detail->throughput = isl->getThroughput();   
        actions[i].name    = "update";     
    }

    //TODO: lock if necessary
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

void handleGlobalReuqests(command &response, action command){
    if(command.name == "status"){

        int nrIsolates = (int) response.getNrIsolates();
        for( int i = 0; i < nrIsolates ; ++i )
            handleIsolateRequest(i,command,response);
    } else if (command.name == "execute"){
        ArrayBufferAllocator allocator;
        v8::Isolate::CreateParams create_params;
        create_params.array_buffer_allocator = &allocator;
        v8::Isolate* isolate = v8::Isolate::New(create_params);
        v8::Isolate::Scope isolate_scope(isolate);
        // Create a stack-allocated handle scope.
        v8::HandleScope handle_scope(isolate);
        v8::Handle<v8::ObjectTemplate> global = v8::ObjectTemplate::New(isolate);
        // Create a new context.
        v8::Local<v8::Context> context = v8::Context::New(isolate, NULL, global);
        // Enter the context for compiling and running the hello world script.
        v8::Context::Scope context_scope(context);
        //////////////////////////////////////////////////////////////////////
        v8::Local<v8::String> source = String::NewFromUtf8(isolate, command.getDetails()->path.c_str(), NewStringType::kNormal).ToLocalChecked();
        v8::Local<v8::Script> script = Script::Compile(context, source).ToLocalChecked();
        script->Run(context).ToLocalChecked();
        //isolate->Dispose();
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
            handleGlobalReuqests(response,cmd.getGlobal());    
        }

        cout<<"Nr isolates:"<<cmd.getNrIsolates()<<endl;
        int len = (int) cmd.getNrIsolates();
        action * actions = cmd.getIsolateActions();
        for( int i = 0; i < len; ++i )
            handleIsolateRequest(i,actions[i],response);
    }
}