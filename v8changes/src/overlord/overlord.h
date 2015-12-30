#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <iostream>
#include <fstream>
#include <strings.h>
#include <stdlib.h>
#include <string>
#include <pthread.h>

#include "include/libplatform/libplatform.h"
#include "include/v8.h"
#include "src/api.h"
#include "base64/base64.h"
#include "protocol/command.h"

class Overlord {
	pthread_t tid;
	int port;
public:
	Overlord(int,bool);
	static void * serve(void *);
	static void handleRequest(ControlProtocol::command &, ControlProtocol::command &);
};
