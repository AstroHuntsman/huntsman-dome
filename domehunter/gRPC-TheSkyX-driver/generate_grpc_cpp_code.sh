#!/bin/bash
# Regenerate the gRPC C++ stubs in src/ from hx2dome.proto.
# Run after any change to hx2dome.proto; protoc and grpc_cpp_plugin must match
# the protobuf/gRPC versions the driver is linked against.
set -e
cd "$(dirname "$0")"

if [ "$1" == "clean" ]; then
	rm -f src/*.pb.cc src/*.pb.h
else
	echo "Generating gRPC C++ code in src/"
	protoc -I. --cpp_out=src --grpc_out=src \
		--plugin=protoc-gen-grpc="$(which grpc_cpp_plugin)" hx2dome.proto
	echo "Done."
fi
