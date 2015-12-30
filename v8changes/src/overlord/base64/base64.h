#ifndef BASE64
#define BASE64

namespace base64 {
	char* encode(const char *in, int in_len);
	bool decode(const char *in, int in_len, char* &out);
}

#endif