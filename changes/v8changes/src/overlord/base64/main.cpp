#include <stdio.h>
#include <iostream>
#include <string.h>
#include "base64.h"

using namespace std;
//TODO: UNITTEST
int main(){

	char in[2048];
	char* out;
	char* out2;
	printf("Input data to encode:");
	scanf("%s",in);
	out = base64::encode(in,strlen(in));
	printf("Result:%s\n",out);
	base64::decode(out,strlen(out),out2);
	printf("Now decoding:%s\n",out2);
}
