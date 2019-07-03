#
# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

HOST_SYSTEM = $(shell uname | cut -f 1 -d_)
SYSTEM ?= $(HOST_SYSTEM)
CXX = g++
CPPFLAGS += `pkg-config --cflags protobuf grpc`
CXXFLAGS += -std=c++11
ifeq ($(SYSTEM),Darwin)
LDFLAGS += -L/usr/local/lib `pkg-config --libs protobuf grpc++`\
           -lgrpc++_reflection\
           -ldl
else
LDFLAGS += -L/usr/local/lib `pkg-config --libs protobuf grpc++`\
           -Wl,--no-as-needed -lgrpc++_reflection -Wl,--as-needed\
           -ldl
endif
PROTOC = protoc
GRPC_CPP_PLUGIN = grpc_cpp_plugin
GRPC_CPP_PLUGIN_PATH ?= `which $(GRPC_CPP_PLUGIN)`
PROTO_PATH1 = /usr/local/include/google/protobuf/
PROTO_PATH2 = /home/fergus/Documents/REPOS/huntsman-dome/domehunter/protos/example_grpc_code/simple_client/hx2dome.proto

# PROTOS_PATH = ../../protos
PROTOS_PATH = /home/fergus/Documents/REPOS/huntsman-dome/domehunter/protos/example_grpc_code/simple_client/

vpath %.proto $(PROTOS_PATH)


all: test

test: hx2dome.pb.o hx2dome.grpc.pb.o x2dome.o test.o
	$(CXX) $^ $(LDFLAGS) -o $@

hx2dome.grpc.pb.o: ../../src/hx2dome.grpc.pb.cpp
	$(CXX) $^ $(LDFLAGS) -c

hx2dome.pb.o: ../../src/hx2dome.pb.cpp
	$(CXX) $^ $(LDFLAGS) -c

x2dome.o: ../../src/x2dome.cpp
	$(CXX) $^ $(LDFLAGS) -c

test.o: test.cpp
	$(CXX) $^ $(LDFLAGS) -c


clean:
	rm -f *.o test
