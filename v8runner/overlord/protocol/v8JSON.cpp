#include "v8JSON.h"

#include "include/v8.h"
#include "include/libplatform/libplatform.h"
#include "src/api.h"

using namespace v8;
//WARNING: Integrate your own context and scope_handle so that other working scripts are not influenced
char* v8JSON::encode(Local<Value> *object)
{
  Isolate *isolate = Isolate::GetCurrent();
  v8::Locker locker{isolate};
  Local<Context> context = isolate->GetCurrentContext();

  Handle<Object> global = (*context)->Global();
  Handle<Object> JSON = global->Get(String::NewFromUtf8(isolate,"JSON"))->ToObject();
  Handle<Function> JSON_stringify = Handle<Function>::Cast(JSON->Get(String::NewFromUtf8(isolate,"stringify")));
  Handle<Value> result = JSON_stringify->Call(JSON, 1, object);
    
  Local<String> r;
  if(result->ToString(context).ToLocal(&r)){
    char * cr = new char[r->Utf8Length()+1];
    r->WriteUtf8 (cr);
    
    return cr;
  }
  return 0;
}

v8::Local<v8::Value> v8JSON::decode(char *input) {
  Isolate *isolate = Isolate::GetCurrent();
  v8::Locker locker{isolate};
  EscapableHandleScope handle_scope(isolate);
  Local<Context> context = isolate->GetCurrentContext();

  Handle<String> jsondata(String::NewFromUtf8(isolate,input));
  Handle<Value> object = v8::StringObject::New(jsondata);
  Handle<Object> global = (*context)->Global();
  Handle<Object> JSON = global->Get(String::NewFromUtf8(isolate,"JSON"))->ToObject();
  Handle<Function> JSON_op = Handle<Function>::Cast(JSON->Get(String::NewFromUtf8(isolate,"parse")));
  Handle<Value> result = JSON_op->Call(JSON, 1, &object);
  
  return handle_scope.Escape(result);
}

double v8JSON::getNumber(v8::Local<v8::Value> &_root, char *_key){

  Isolate *isolate = Isolate::GetCurrent();
  v8::Locker locker{isolate};
  Local<Context> context = isolate->GetCurrentContext();
  //EscapableHandleScope handle_scope(isolate);
  //create and enter separate context
  //Local<Context> context = v8::Context::New(isolate);
  //Context::Scope context_scope(context);
  //do operations
	
  v8::Local<v8::String> key = v8::String::NewFromUtf8(isolate,_key);
  
  Local<Object> root;
  if(! _root->ToObject(context).ToLocal(&root))
    return 0.0;

  Local<v8::Number> nr;  
  Local<v8::Value> inter;
  if(!root->Get(context,key).ToLocal(&inter))
    return 0.0;

  ////////////////////////////////////////////////
  if(!inter->IsNumber() || !inter->ToNumber(context).ToLocal(&nr))
    return 0.0;

  double result = nr->Value();
  return result;
}

const char* v8JSON::getString(v8::Local<v8::Value> &_root, char *_key) {
	Isolate *isolate = Isolate::GetCurrent();
  v8::Locker locker{isolate};
  Local<Context> context = isolate->GetCurrentContext();

  v8::Local<v8::String> key = v8::String::NewFromUtf8(isolate,_key);
  
  Local<Object> root;
  if(!_root->ToObject(context).ToLocal(&root))
    return "";

  Local<v8::Value> inter;
  if(!root->Get(context,key).ToLocal(&inter))
    return "";

  Local<v8::String> nr;
  ////////////////////////////////////////////////
  if(!inter->IsString() || !inter->ToString(context).ToLocal(&nr))
    return "";

  char *cr = new char[nr->Utf8Length()+1];
  nr->WriteUtf8 (cr);
  return cr;
}

v8::Local<v8::Value> v8JSON::getValue(v8::Local<v8::Value> &_root, char *_key) {
  Isolate *isolate = Isolate::GetCurrent();
  v8::Locker locker{isolate};
  Local<Context> context = isolate->GetCurrentContext();
  EscapableHandleScope handle_scope(isolate);

  v8::Local<v8::String> key = v8::String::NewFromUtf8(isolate,_key);
  Local<Object> root;
  Local<v8::Value> inter;
  
  bool success = !_root->ToObject(context).ToLocal(&root);
       success = root->Get(context,key).ToLocal(&inter);

  return handle_scope.Escape(inter);
}
//setters
/*
void setNumber(v8::Local<v8::Value> &root, char * key, double value) {

}
void setString(v8::Local<v8::Value> &root, char * key, char *value) {

}
void setValue (v8::Local<v8::Value> &root, char * key, v8::Local<v8::Value> value){

}
*/
