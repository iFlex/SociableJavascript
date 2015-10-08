// Copyright 2015 the V8 project authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

#include "include/libplatform/libplatform.h"
#include "include/v8.h"

using namespace v8;

class ArrayBufferAllocator : public v8::ArrayBuffer::Allocator {
 public:
  virtual void* Allocate(size_t length) {
    void* data = AllocateUninitialized(length);
    return data == NULL ? data : memset(data, 0, length);
  }
  virtual void* AllocateUninitialized(size_t length) { return malloc(length); }
  virtual void Free(void* data, size_t) { free(data); }
};

char * readSourceScript(char * file){
        char * source = 0;
	long long index = 0;
	struct stat fileInfo;
        if(!lstat(file,&fileInfo)){
		printf("Source size %lld\n",fileInfo.st_size);
		source = new char[fileInfo.st_size+1];
		char chrBuff;		
		FILE * fileH = fopen(file,"rb");
		if(fileH){	
			while(fread(&chrBuff,sizeof(char),1,fileH)) source[index++]=chrBuff;
			fclose(fileH);		
		}
	}
	return source;
}

int main(int argc, char* argv[]) {
  char * sourceScript = 0;
  if(argc > 1)
	sourceScript = readSourceScript(argv[1]);
  
  if(!sourceScript)
	return 0;

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
    Isolate::Scope isolate_scope(isolate);

    // Create a stack-allocated handle scope.
    HandleScope handle_scope(isolate);
    
    // Create a template for the global object and set the
    // built-in global functions.
    Local<ObjectTemplate> global = ObjectTemplate::New(isolate);
    
    // Create a new context.
    Local<Context> context = Context::New(isolate,NULL,global);
 
    // Enter the context for compiling and running the hello world script.
    Context::Scope context_scope(context);
    
    // Create a string containing the JavaScript source code.
    Local<String> source =
        String::NewFromUtf8(isolate, sourceScript,
                            NewStringType::kNormal).ToLocalChecked();

    // Compile the source code.
    Local<Script> script = Script::Compile(context, source).ToLocalChecked();

    // Run the script to get the result.
    Local<Value> result = script->Run(context).ToLocalChecked();

    // Convert the result to an UTF8 string and print it.
    String::Utf8Value utf8(result);
    //printf("%s\n", *utf8);
  }

  // Dispose the isolate and tear down V8.
  isolate->Dispose();
  V8::Dispose();
  V8::ShutdownPlatform();
  delete platform;
  delete sourceScript;
  printf("\nDone\n");
  return 0;
}

