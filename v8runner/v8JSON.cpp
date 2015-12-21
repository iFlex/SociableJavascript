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

#include "include/libplatform/libplatform.h"
#include "include/v8.h"
#include "src/api.h"
///////
//#include "src/libplatform/default-platform.h"

using namespace v8;
using namespace std;

//because Google engineers like to wrap their shit in weird ass classes with no eplanation
char* toJson(Isolate *i, Local<Context> context, Local<Value> *object)
{
    Handle<Object> global = (*context)->Global();

    Handle<Object> JSON = global->Get(String::NewFromUtf8(i,"JSON"))->ToObject();
    Handle<Function> JSON_stringify = Handle<Function>::Cast(JSON->Get(String::NewFromUtf8(i,"stringify")));
    Handle<Value> result = JSON_stringify->Call(JSON, 1, object);
    
    Local<String> r;
    if(result->ToString(context).ToLocal(&r)){
      char * cr = new char[r->Utf8Length()+1];
      r->WriteUtf8 (cr);

      return cr;
    }

    return 0;
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

//ARGUMENTS structure
// first argument is heap size in MB
// next arguments are scripts to be loaded
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

  char in[1000];

  cout<<"JSON Input:";
  cin>>in;
  
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
  
    v8::Local<v8::String> s = v8::String::NewFromUtf8(isolate,in);// = v8::String::New( in );
    v8::Local<v8::Value> root = v8::JSON::Parse(s);

    printf("Done\n");
    if(root.IsEmpty())
      printf("Is empty!\n");
    else {
      printf("Contains stuff\n");
      Local<v8::Object> obj;
      bool success = root->ToObject(context).ToLocal(&obj);

      v8::Local<v8::String> key = v8::String::NewFromUtf8(isolate,"test");
      
      Local<v8::Value> test;
      success = obj->Get(context,key).ToLocal(&test);
      
      Local<v8::Number> nr;
      success = test->ToNumber(context).ToLocal(&nr);

      printf("is: %d\n",root->IsObject());
      printf("test:%f\n",nr->Value());
      printf("OBJ2JSON:%s\n",toJson(isolate,context,&root));
    }

  }

  // Dispose the isolate and tear down V8.
  isolate->Dispose();
  V8::Dispose();
  V8::ShutdownPlatform();
  delete platform;
  return 0;
}