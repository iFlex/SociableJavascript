// Copyright 2015 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <assert.h>
#include <iostream>

#include "overlord/overlord.h"
#include "overlord/protocol/v8JSON.h"
#include "include/libplatform/libplatform.h"
#include "include/v8.h"
#include "src/api.h"

using namespace v8;
using namespace std;
//will these methods override the code that the isolate was executing before?
void * concur(void * data){
  //need to use locker to make it work concurrently
  char c[1000];
  cout<<"Input json to parse"<<endl;
  //cin>>c;
  scanf("%s",c);
  
  cout<<"Creating v8JSON"<<endl;
  v8JSON v8j;
  cout<<"Parsing:"<<c<<endl;
  Local<Value> root = v8j.decode(c);
  cout<<"Done"<<endl;
  /*cout<<"test:"<<v8j.getNumber(root,"test")<<endl;
  cout<<"str:"<<v8j.getString(root,"str")<<endl;
  Local<Value> inner = v8j.getValue(root,"inner");
  cout<<"inner::nr:"<<v8j.getNumber(inner,"nr")<<endl;
  cout<<"encoding test:"<<v8j.encode(&root)<<endl;*/
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

int main(int argc, char* argv[]) {
   // Initialize V8.
  V8::InitializeICU();
  V8::InitializeExternalStartupData(argv[0]);
  Platform* platform = platform::CreateDefaultPlatform();
  V8::InitializePlatform(platform);
  V8::Initialize();

  // Create a new Isolate and make it the current one.
  ArrayBufferAllocator allocator;
  Isolate::CreateParams create_params;
  create_params.array_buffer_allocator = &allocator;
  Isolate* isolate = Isolate::New(create_params);
  {
    //////////////////////////////////////////////
    Isolate::Scope isolate_scope(isolate);

    // Create a stack-allocated handle scope.
    HandleScope handle_scope(isolate);
    v8::Handle<v8::ObjectTemplate> global = v8::ObjectTemplate::New(isolate);
    // Create a new context.
    Local<Context> context = v8::Context::New(isolate, NULL, global);
    // Enter the context for compiling and running the hello world script.
    Context::Scope context_scope(context);
    concur(NULL);
    /*cout<<"Isolate ready for concurrency"<<endl;
    pthread_t tid;
    pthread_create(&tid,NULL,concur,NULL);
    while(true);*/
  }

  // Dispose the isolate and tear down V8.
  isolate->Dispose();
  V8::Dispose();
  V8::ShutdownPlatform();
  delete platform;
  return 0;
}