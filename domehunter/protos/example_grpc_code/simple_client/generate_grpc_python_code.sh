#!/bin/bash

if [ "$1" == "clean" ]; then
	rm *pb2_grpc.py
	rm *pb2.py
else
	HDOME_PATH="$HOME/Documents/REPOS"
	PROTOS_PATH="$HDOME_PATH/huntsman-dome/domehunter/protos/proto_test/"
	PROTO_PATH1="/usr/local/include/google/protobuf/"
	PROTO_PATH2="$HDOME_PATH/huntsman-dome/domehunter/protos/proto_test/hx2dome.proto"

	echo -e "\nGenerating GRPC Python code\n"

	echo -e "python -m grpc_tools.protoc -I=$PROTOS_PATH --python_out=. --grpc_python_out=. --proto_path=$PROTO_PATH1 $PROTO_PATH2\n"

	python -m grpc_tools.protoc -I=$PROTOS_PATH --python_out=. --grpc_python_out=. --proto_path=$PROTO_PATH1 $PROTO_PATH2

	echo -e "Done.\n"
fi
