HOST_SYSTEM = $(shell uname | cut -f 1 -d_)
SYSTEM ?= $(HOST_SYSTEM)
CXX = g++
CPPFLAGS += `pkg-config --cflags protobuf grpc`
CXXFLAGS += -std=c++11

LDFLAGS += -L/usr/local/lib `pkg-config --libs protobuf grpc++`\
           -Wl,--no-as-needed -lgrpc++_reflection -Wl,--as-needed\
           -ldl

PROTOC = protoc
GRPC_CPP_PLUGIN = grpc_cpp_plugin
GRPC_CPP_PLUGIN_PATH ?= `which $(GRPC_CPP_PLUGIN)`
PROTO_PATH1 = /usr/local/include/google/protobuf/
PROTO_PATH2 = /home/fergus/Documents/REPOS/huntsman-dome/domehunter/protos/example_grpc_code/simple_client_v2/hx2dome.proto

# PROTOS_PATH = ../../protos
PROTOS_PATH = /home/fergus/Documents/REPOS/huntsman-dome/domehunter/protos/example_grpc_code/simple_client_v2/

vpath %.proto $(PROTOS_PATH)

all: main

main: main.o hx2dome.proto_client.o hx2dome.pb.o hx2dome.grpc.pb.o
	$(CXX) $^ $(LDFLAGS) -o $@

main.o: main.cpp
	$(CXX) $^ $(LDFLAGS) -c

hx2dome.proto_client.o: hx2dome.proto_client.cc
	$(CXX) $^ $(LDFLAGS) -c

hx2dome.grpc.pb.o: hx2dome.grpc.pb.cc
	$(CXX) $^ $(LDFLAGS) -c

hx2dome.pb.o: hx2dome.pb.cc
	$(CXX) $^ $(LDFLAGS) -c


.PRECIOUS: %.grpc.pb.cc
hx2dome.grpc.pb.cc: hx2dome.proto
	$(PROTOC) -I $(PROTOS_PATH) --grpc_out=. --proto_path=$(PROTO_PATH1) $(PROTO_PATH2) --plugin=protoc-gen-grpc=$(GRPC_CPP_PLUGIN_PATH)

.PRECIOUS: %.pb.cc
hx2dome.pb.cc: hx2dome.proto
	$(PROTOC) -I $(PROTOS_PATH) --cpp_out=. $<

clean:
	rm -f *.o main
