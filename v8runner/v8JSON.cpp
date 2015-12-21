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

/*
Handle<String> toJson(Handle<Value> object)
{
    HandleScope scope;

    Handle<Context> context = Context::GetCurrent();
    Handle<Object> global = context->Global();

    Handle<Object> JSON = global->Get(String::New("JSON"))->ToObject();
    Handle<Function> JSON_stringify = Handle<Function>::Cast(JSON->Get(String::New("stringify")));

    return scope.Close(JSON_stringify->Call(JSON, 1, object));
}

Handle<Value> fromJson(Handle<Value> object)
{
    HandleScope scope;

    Handle<Context> context = Context::GetCurrent();
    Handle<Object> global = context->Global();

    Handle<Object> JSON = global->Get(String::New("JSON"))->ToObject();
    Handle<Function> JSON_stringify = Handle<Function>::Cast(JSON->Get(String::New("parse")));

    return scope.Close(JSON_stringify->Call(JSON, 1, object));
}
*/

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
      //v8::Value r = (v8::Value)root;//reinterpret_cast<v8::Value>(root);
      //root.Get(context,v8::String::New(isolate,"test"));
      printf("is: %d\n",root->IsObject());
    }

  }

  // Dispose the isolate and tear down V8.
  isolate->Dispose();
  V8::Dispose();
  V8::ShutdownPlatform();
  delete platform;
  return 0;
}