#!/bin/bash
# Regenerate the gRPC Python stubs (hx2dome_pb2*.py) from the shared
# ../gRPC-TheSkyX-driver/hx2dome.proto. Requires grpcio-tools.
set -e
cd "$(dirname "$0")"

if [ "$1" == "clean" ]; then
	rm -f hx2dome_pb2.py hx2dome_pb2_grpc.py
else
	echo "Generating gRPC Python code"
	python -m grpc_tools.protoc -I../gRPC-TheSkyX-driver --python_out=. \
		--grpc_python_out=. ../gRPC-TheSkyX-driver/hx2dome.proto
	echo "Done."
fi
