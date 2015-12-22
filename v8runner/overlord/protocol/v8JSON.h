#include "include/libplatform/libplatform.h"
#include "include/v8.h"
#include "src/api.h"

#ifndef CP_JSON
#define CP_JSON

using namespace v8;
//handle parsing errors somehow
class v8JSON {    
public:
	v8::Local<v8::Value> decode(char *); //working
	char* encode(v8::Local<v8::Value> *);//working
	//getters - working
	double                getNumber(v8::Local<v8::Value> &root, char * key);
	const char*           getString(v8::Local<v8::Value> &root, char * key);
	v8::Local<v8::Value>  getValue (v8::Local<v8::Value> &root, char * key);
	//setters
	void setNumber(v8::Local<v8::Value> &root, char * key, double value);
	void setString(v8::Local<v8::Value> &root, char * key, char *value);
	void setValue (v8::Local<v8::Value> &root, char * key, v8::Local<v8::Value> value);

};

#endif