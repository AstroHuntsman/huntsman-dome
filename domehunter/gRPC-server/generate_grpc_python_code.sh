#!/bin/bash

if [ "$1" == "clean" ]; then
	rm src/*pb2_grpc.py
	rm src/*pb2.py
else
	HDOME_PATH="$HOME/Documents/REPOS"
	PROTOS_PATH="$HDOME_PATH/huntsman-dome/domehunter/gRPC-TheSkyX-driver/"
	PROTO_FILE="$HDOME_PATH/huntsman-dome/domehunter/gRPC-TheSkyX-driver/hx2dome.proto"

	echo -e "\nGenerating GRPC Python code\n"

	echo -e "python -m grpc_tools.protoc -I=$PROTOS_PATH --python_out=. --grpc_python_out=. $PROTO_FILE\n"

	python -m grpc_tools.protoc -I=$PROTOS_PATH --python_out=. --grpc_python_out=. $PROTO_FILE

	#echo -e "Moving generated GRPC Python code to src/\n"
	#mv *pb2* src/

	echo -e "Done.\n"
fi
