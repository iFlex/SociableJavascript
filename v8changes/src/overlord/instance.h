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
#include <fstream>
#include "include/libplatform/libplatform.h"
#include "include/v8.h"
#include "src/api.h"

namespace instance {

	void Print(const v8::FunctionCallbackInfo<v8::Value>& args);
	void ReportException(v8::Isolate* isolate, v8::TryCatch* handler);
	bool ExecuteString(v8::Isolate* isolate,
	                   v8::Local<v8::String> source,
	                   v8::Local<v8::Value> name,
	                   bool print_result,
	                   bool report_exceptions);

	v8::Local<v8::String> ReadFile(v8::Isolate*, const char*);
	void _load(char *, v8::Isolate*);
	void Load(const v8::FunctionCallbackInfo<v8::Value>& args);
	void Read(const v8::FunctionCallbackInfo<v8::Value>& args);
	void Write(const v8::FunctionCallbackInfo<v8::Value>& args);

	// functions to expose to JS environment for testing
	void GetHeapAvailable(const v8::FunctionCallbackInfo<v8::Value>& args);
	void GetHeapSize(const v8::FunctionCallbackInfo<v8::Value>& args);
	void SetMaxHeapSize(const v8::FunctionCallbackInfo<v8::Value>& args);

	void executor(int max_heap, int nrScipts, const char *script[]);
	void * synchronousExec(void *);
	void parallelExec(const char *);

}