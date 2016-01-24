#ifndef BASE64
#define BASE64
#include <string>
namespace base64 {
	void encode(std::string in, char out[]);
	void encode(const char *in, int in_len, char out[]);
	bool decode(const char *in, int in_len, char out[]);
}

#endif