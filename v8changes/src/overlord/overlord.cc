#include "overlord.h"

using namespace std;

int connFd;

void * serve(void *){
	cout << "Overlord:: New controller connected - Thread No: " << pthread_self() << endl;
    char test[300];
    bzero(test, 301);
    bool loop = false;
    while(!loop)
    {    
        bzero(test, 301);
        
        
        read(connFd, test, 300);
        
        string tester (test);
        cout << tester << endl;
        
        
        if(tester == "exit")
            break;
    }
    cout << "\nClosing thread and conn" << endl;
    close(connFd);
}

char overlord(int portNo){

	int pId, listenFd;
	socklen_t len; //store size of the address
	bool loop = false;
	struct sockaddr_in svrAdd, clntAdd;
	    
	pthread_t threadA[3];
    
    //create socket
    listenFd = socket(AF_INET, SOCK_STREAM, 0);
    
    if(listenFd < 0)
    {
        cerr << "Overlord:: Cannot open socket" << endl;
        return 1;
    }
    
    bzero((char*) &svrAdd, sizeof(svrAdd));
    
    svrAdd.sin_family = AF_INET;
    svrAdd.sin_addr.s_addr = INADDR_ANY;
    svrAdd.sin_port = htons(portNo);
    
    //bind socket
    if(bind(listenFd, (struct sockaddr *)&svrAdd, sizeof(svrAdd)) < 0)
    {
        cerr << "Overlord::Cannot bind" << endl;
        return 2;
    }
    
    listen(listenFd, 5);
    
    len = sizeof(clntAdd);
    
    int noThread = 0;

    while (noThread < 3)
    {
        cout << "Overlord::Listening on port"<< portNo << endl;

        //this is where client connects. svr will hang in this mode until client conn
        connFd = accept(listenFd, (struct sockaddr *)&clntAdd, &len);

        if (connFd < 0)
        {
            cerr << "Overlord::Cannot accept connection" << endl;
            continue;
            //return 0;
        }
        else
        {
            cout << "Overlord::Connection successful" << endl;
        }
        
        pthread_create(&threadA[noThread], NULL, serve, NULL); 
        
        noThread++;
    }
    /*
    for(int i = 0; i < 3; i++)
    {
        pthread_join(threadA[i], NULL);
    }*/
    return 0;
}