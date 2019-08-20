#!/bin/bash

if [ "$1" == "clean" ]; then
	rm libhuntsmandome*
	rm src/*.grpc.pb.*
	rm src/*.pb.*
	rm *.o
	rm .qmake.stash
else
	HDOME_PATH="$HOME/Documents/REPOS"
	PROTOS_PATH="$HDOME_PATH/huntsman-dome/domehunter/protos/src/"
	PROTO_FILE="$HDOME_PATH/huntsman-dome/domehunter/protos/src/hx2dome.proto"
	GRPC_CPP_PLUGIN_PATH="$(which grpc_cpp_plugin)"

	echo -e "Generating GRPC C++ code\n"

	echo -e "protoc -I $PROTOS_PATH --cpp_out=. src/hx2dome.proto\n"
	protoc -I "$PROTOS_PATH" --cpp_out=. hx2dome.proto

	echo -e "protoc -I $PROTOS_PATH --grpc_out=. $PROTO_FILE --plugin=protoc-gen-grpc=$GRPC_CPP_PLUGIN_PATH\n"
	protoc -I "$PROTOS_PATH" --grpc_out=. "$PROTO_FILE" --plugin=protoc-gen-grpc="$GRPC_CPP_PLUGIN_PATH"

	echo -e "Moving generated GRPC C++ code to src/\n"
	mv hx2dome.grpc.pb.cc src/hx2dome.grpc.pb.cpp
	mv hx2dome.pb.cc src/hx2dome.pb.cpp
	mv *.pb.h src/

	#echo -e "Generating Makefile from project file.\n"
	#qmake

	#echo -e "Running Generated Makefile.\n"
	#make

	#echo -e "Cleaning out object files.\n"
	#rm *.o
	
	echo -e "Done.\n"
fi
