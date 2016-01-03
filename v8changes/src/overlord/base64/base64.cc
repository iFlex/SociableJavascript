#include "base64.h"
#include <stdio.h>

namespace base64{
	char _6to8(unsigned val){
		if( val < 26 )
			return val+'A';
		if( val > 25 && val < 52)
			return (val - 26) + 'a';
		if( val > 51 && val < 62 )
			return (val - 52) + '0';
		if( val == 62 )
			return '+';
		if( val == 63 )
			return '/';
		return '_';
	}
	
	unsigned _8to6(char val){
		if( val >= 'A' && val <= 'Z' )
			return val - 'A';
		if( val >= 'a' && val <= 'z')
			return 26 + (val - 'a');
		if( val >= '0' && val <= '9' )
			return 52 + (val - '0');
		if( val == '+' )
			return 62;
		if( val == '/')
			return 63;
		 return 0;	
	}

	char* encode(const char *in, int in_len){
		char *out = new char[(in_len*8/6*8) + (in_len % 3)+ 1];
		unsigned buffer = 0,mask;
		int index = 0;
		char bufferedBits = 0,shiftDist = 0;
		for( int i = 0; i < in_len; ++i ){
			buffer <<= 8;
			buffer |= in[i];
			bufferedBits += 8;
			
			while(bufferedBits > 6){
				shiftDist = bufferedBits - 6;
				mask = (1 << shiftDist) - 1;
				out[index++] = _6to8( buffer >> (shiftDist) );
				
				buffer &= mask;
				bufferedBits -= 6;
			}
		}
		//remaining bits to encode
		if( buffer )
			out[index++] = _6to8( buffer << ( 6 - bufferedBits ) );
		//padd
		in_len = (in_len*8)%3;
		if(in_len){
			out[index++] = '=';
			if( in_len > 1 )
				out[index++] = '=';
		}

		out[index] = 0;
		return out;
	}
	
	void encode(const char *in, int in_len, char* &out){
		out = encode(in,in_len);
	}

	bool decode(const char *in, int in_len, char* &out){
		if( (in_len*6) % 8)
			return false;

		out = new char[ in_len*6/8 + 1 ];
		unsigned buffer = 0,mask;
		int index = 0;
		char bufferedBits = 0,shiftDist = 0;
		for( int i = 0; i < in_len; ++i ){
			buffer <<= 6;
			buffer |= _8to6(in[i]);
			bufferedBits += 6;
			
			while(bufferedBits >= 8){
				shiftDist = bufferedBits - 8;
				mask = (1 << shiftDist) - 1;
				out[index++] = buffer >> (shiftDist);
				
				buffer &= mask;
				bufferedBits -= 8;
			}
		}
		
		out[index] = 0;
		return true;
	}
}