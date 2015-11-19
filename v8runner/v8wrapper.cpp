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

#include "include/libplatform/libplatform.h"
#include "include/v8.h"
#include "src/api.h"
///////
//#include "src/libplatform/default-platform.h"

using namespace v8;

void Print(const v8::FunctionCallbackInfo<v8::Value>& args);
void ReportException(v8::Isolate* isolate, v8::TryCatch* handler);
bool ExecuteString(v8::Isolate* isolate,
                   v8::Handle<v8::String> source,
                   v8::Handle<v8::Value> name,
                   bool print_result,
                   bool report_exceptions);

v8::Handle<v8::String> ReadFile(v8::Isolate*, const char*);
void _load(char *, v8::Isolate*);
void Load(const v8::FunctionCallbackInfo<v8::Value>& args);

// functions to expose to JS environment for testing
void GetHeapAvailable(const v8::FunctionCallbackInfo<v8::Value>& args);
void GetHeapSize(const v8::FunctionCallbackInfo<v8::Value>& args);
void SetMaxHeapSize(const v8::FunctionCallbackInfo<v8::Value>& args);

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

//ARGUMENTS structure
// first argument is heap size in MB
// next arguments are scripts to be loaded
int main(int argc, char* argv[]) {
  if(argc < 2){
    printf("#NOT ENOUGH ARGUMENTS: Usage v8wrapper.bin <heap_size> <scrpit1> <script2> ...\nMandatory paramenters <heap_size> and at least one script to load!");
    return 0;
  }
  // Initialize V8.
  V8::InitializeICU();
  V8::InitializeExternalStartupData(argv[0]);
  Platform* platform = platform::CreateDefaultPlatform();
  V8::InitializePlatform(platform);
  V8::Initialize();
  //overlord(1500);

  int heapSize = atoi(argv[1]);
  printf("Running with heap size:%d\n",heapSize);
  // Create a new Isolate and make it the current one.
  ArrayBufferAllocator allocator;
  Isolate::CreateParams create_params;
  create_params.array_buffer_allocator = &allocator;
  //configure head size to a total of 2M
  create_params.constraints.set_max_old_space_size(heapSize);
  create_params.constraints.set_max_semi_space_size(1);

  Isolate* isolate = Isolate::New(create_params);
  {
    //////////////////////////////////////////////
    Isolate::Scope isolate_scope(isolate);

    // Create a stack-allocated handle scope.
    HandleScope handle_scope(isolate);

    v8::Handle<v8::ObjectTemplate> global = v8::ObjectTemplate::New(isolate);
    global->Set(v8::String::NewFromUtf8(isolate, "load"),
                v8::FunctionTemplate::New(isolate, Load));
                
    // Bind the global 'print' function to the C++ Print callback.
    global->Set(v8::String::NewFromUtf8(isolate, "print"),
                v8::FunctionTemplate::New(isolate, Print));

    // Bind a global '_getHeapSize' function to the C++ GetHeapSize callback.
    global->Set(v8::String::NewFromUtf8(isolate, "_getHeapSize"),
                v8::FunctionTemplate::New(isolate, GetHeapSize));

    // Bind a global '_setMaxHeapSize' function to the C++ SetMaxHeapSize callback.
    global->Set(v8::String::NewFromUtf8(isolate, "_setMaxHeapSize"),
                v8::FunctionTemplate::New(isolate, SetMaxHeapSize));

    // Bind a global '_setMaxHeapSize' function to the C++ SetMaxHeapSize callback.
    global->Set(v8::String::NewFromUtf8(isolate, "_getHeapAvailable"),
                v8::FunctionTemplate::New(isolate, GetHeapAvailable));

    // Create a new context.
    Local<Context> context = v8::Context::New(isolate, NULL, global);
    // Enter the context for compiling and running the hello world script.
    Context::Scope context_scope(context);

    for( int i=2; i < argc; ++i ){
      char before[10] = "load('";
      char command[255];
      char after[5] = "');";
      sprintf(command,"%s%s%s",before,argv[i],after);
      printf("commands:%s\n",command);
      // Create a string containing the JavaScript source code.
      Local<String> source =
          String::NewFromUtf8(isolate, command,
                              NewStringType::kNormal).ToLocalChecked();
      // Compile the source code.
      Local<Script> script = Script::Compile(context, source).ToLocalChecked();
      // Run the script to get the result.
      Local<Value> result = script->Run(context).ToLocalChecked();
    }
  }
  //printf("HEAP SIZE:%lld\n",);
  HeapStatistics hs;
  isolate-> GetHeapStatistics(&hs);
  // Dispose the isolate and tear down V8.
  isolate->Dispose();
  V8::Dispose();
  V8::ShutdownPlatform();
  delete platform;
  printf("\n :) Done (: \n");
  return 0;
}

// Extracts a C string from a V8 Utf8Value.
const char* ToCString(const v8::String::Utf8Value& value) {
  return *value ? *value : "<string conversion failed>";
}

// Reads a file into a v8 string.
v8::Handle<v8::String> ReadFile(v8::Isolate* isolate, const char* name) {
  FILE* file = fopen(name, "rb");
  if (file == NULL) return v8::Handle<v8::String>();

  fseek(file, 0, SEEK_END);
  int size = ftell(file);
  rewind(file);

  char* chars = new char[size + 1];
  chars[size] = '\0';
  for (int i = 0; i < size;) {
    int read = static_cast<int>(fread(&chars[i], 1, size - i, file));
    i += read;
  }
  fclose(file);
  v8::Handle<v8::String> result =
      v8::String::NewFromUtf8(isolate, chars, v8::String::kNormalString, size);
  delete[] chars;
  return result;
}

// The callback that is invoked by v8 whenever the JavaScript 'load'
// function is called.  Loads, compiles and executes its argument
// JavaScript file.
void Load(const v8::FunctionCallbackInfo<v8::Value>& args) {
  for (int i = 0; i < args.Length(); i++) {
    v8::HandleScope handle_scope(args.GetIsolate());
    v8::String::Utf8Value file(args[i]);
    if (*file == NULL) {
      args.GetIsolate()->ThrowException(
          v8::String::NewFromUtf8(args.GetIsolate(), "Error loading file"));
      return;
    }
    v8::Handle<v8::String> source = ReadFile(args.GetIsolate(), *file);
    if (source.IsEmpty()) {
      args.GetIsolate()->ThrowException(
           v8::String::NewFromUtf8(args.GetIsolate(), "Error loading file"));
      return;
    }
    if (!ExecuteString(args.GetIsolate(),
                       source,
                       v8::String::NewFromUtf8(args.GetIsolate(), *file),
                       false,
                       false)) {
      args.GetIsolate()->ThrowException(
          v8::String::NewFromUtf8(args.GetIsolate(), "Error executing file"));
      return;
    }
  }
}

// Executes a string within the current v8 context.
bool ExecuteString(v8::Isolate* isolate,
                   v8::Handle<v8::String> source,
                   v8::Handle<v8::Value> name,
                   bool print_result,
                   bool report_exceptions) {
  v8::HandleScope handle_scope(isolate);
  v8::TryCatch try_catch;
  v8::ScriptOrigin origin(name);
  v8::Handle<v8::Script> script = v8::Script::Compile(source, &origin);
  if (script.IsEmpty()) {
    // Print errors that happened during compilation.
    if (report_exceptions)
      ReportException(isolate, &try_catch);
    return false;
  } else {
    v8::Handle<v8::Value> result = script->Run();
    if (result.IsEmpty()) {
      assert(try_catch.HasCaught());
      // Print errors that happened during execution.
      if (report_exceptions)
        ReportException(isolate, &try_catch);
      return false;
    } else {
      assert(!try_catch.HasCaught());
      if (print_result && !result->IsUndefined()) {
        // If all went well and the result wasn't undefined then print
        // the returned value.
        v8::String::Utf8Value str(result);
        const char* cstr = ToCString(str);
        printf("%s\n", cstr);
      }
      return true;
    }
  }
}

void ReportException(v8::Isolate* isolate, v8::TryCatch* try_catch) {
  v8::HandleScope handle_scope(isolate);
  v8::String::Utf8Value exception(try_catch->Exception());
  const char* exception_string = ToCString(exception);
  v8::Handle<v8::Message> message = try_catch->Message();
  if (message.IsEmpty()) {
    // V8 didn't provide any extra information about this error; just
    // print the exception.
    fprintf(stderr, "%s\n", exception_string);
  } else {
    // Print (filename):(line number): (message).
    v8::String::Utf8Value filename(message->GetScriptOrigin().ResourceName());
    const char* filename_string = ToCString(filename);
    int linenum = message->GetLineNumber();
    fprintf(stderr, "%s:%i: %s\n", filename_string, linenum, exception_string);
    // Print line of source code.
    v8::String::Utf8Value sourceline(message->GetSourceLine());
    const char* sourceline_string = ToCString(sourceline);
    fprintf(stderr, "%s\n", sourceline_string);
    // Print wavy underline (GetUnderline is deprecated).
    int start = message->GetStartColumn();
    for (int i = 0; i < start; i++) {
      fprintf(stderr, " ");
    }
    int end = message->GetEndColumn();
    for (int i = start; i < end; i++) {
      fprintf(stderr, "^");
    }
    fprintf(stderr, "\n");
    v8::String::Utf8Value stack_trace(try_catch->StackTrace());
    if (stack_trace.length() > 0) {
      const char* stack_trace_string = ToCString(stack_trace);
      fprintf(stderr, "%s\n", stack_trace_string);
    }
  }
}

// The callback that is invoked by v8 whenever the JavaScript 'print'
// function is called.  Prints its arguments on stdout separated by
// spaces and ending with a newline.
void Print(const v8::FunctionCallbackInfo<v8::Value>& args) {
  bool first = true;
  for (int i = 0; i < args.Length(); i++) {
    v8::HandleScope handle_scope(args.GetIsolate());
    if (first) {
      first = false;
    } else {
      printf(" ");
    }
    v8::String::Utf8Value str(args[i]);
    const char* cstr = ToCString(str);
    printf("%s", cstr);
  }
  printf("\n");
  fflush(stdout);
}

///TESTER FUNCTIONS
//TODO: Expose the old_space_ expansion function and test how it works
void GetHeapSize(const v8::FunctionCallbackInfo<v8::Value>& args){
  
  Local<ObjectTemplate> result = ObjectTemplate::New(args.GetIsolate());
  
  /*HeapStatistics hs;
  args.GetIsolate()->GetHeapStatistics(&hs);
  unsigned sz = hs.total_heap_size();
  */
  v8::internal::Heap * heap = reinterpret_cast<v8::internal::Isolate*>(args.GetIsolate())->heap();
  unsigned u = heap->old_space()->Capacity();

  args.GetReturnValue().Set(v8::Integer::NewFromUnsigned(args.GetIsolate(), u));
}

void SetMaxHeapSize(const v8::FunctionCallbackInfo<v8::Value>& args){
  int size = 0;
  if( args.Length() == 1 ){
    //TODO: figure out how to pass integer
  
    v8::HandleScope handle_scope(args.GetIsolate());
    v8::String::Utf8Value str(args[0]);
    const char* cstr = ToCString(str);
    
    size = atoi(cstr);
  }

  printf("Setting heap maximum to:%d\n",size);
  v8::internal::Heap * heap = reinterpret_cast<v8::internal::Isolate*>(args.GetIsolate())->heap();
  //heap->old_space()->IncreaseCapacity(size); - nope
  //heap->ConfigureHeap(1,size,0,0); - nope
  heap->setMaxOldGenerationSize(size);
}

void GetHeapAvailable(const v8::FunctionCallbackInfo<v8::Value>& args){
  v8::internal::Heap * heap = reinterpret_cast<v8::internal::Isolate*>(args.GetIsolate())->heap();
  unsigned size = (heap->old_space()->Available());
  args.GetReturnValue().Set(v8::Integer::NewFromUnsigned(args.GetIsolate(), size)); 
}