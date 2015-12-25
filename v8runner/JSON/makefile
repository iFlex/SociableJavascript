inclink=-std=c++0x
lnk=-L ~/custom_libs -ljsoncpp
pfldr=protocol/

all: main

main: main.o details.o action.o error.o command.o
	g++ -o main main.o details.o action.o command.o error.o $(lnk)

main.o: main.cpp
	g++ -c main.cpp $(inclink)

action.o: $(pfldr)action.cpp
	g++ -c $(pfldr)action.cpp $(inclink)

command.o: $(pfldr)command.cpp
	g++ -c $(pfldr)command.cpp $(inclink)

error.o: $(pfldr)error.cpp
	g++ -c $(pfldr)error.cpp $(inclink)

details.o: $(pfldr)details.cpp
	g++ -c $(pfldr)details.cpp $(inclink)

clean:
	rm *o main
