# Makefile for libHuntsmanDome

CXX = g++
CFLAGS = -fPIC  -O2 -g -DSB_LINUX_BUILD -I. -I./src/licensedinterfaces/\
         -L/usr/local/lib -lprotobuf -pthread -lgrpc++ -pthread -I/usr/local/include

CPPFLAGS = -fPIC -O2 -g -DSB_LINUX_BUILD -I. -I./src/licensedinterfaces/ -I/usr/local/include\
	   -L/usr/local/lib -lprotobuf -pthread -lgrpc++ -pthread

CXXFLAGS += -std=c++11

LDFLAGS = -shared -lstdc++ -L/usr/local/lib -lprotobuf -pthread -lgrpc++\
	   -lgrpc++_reflection -ldl 


RM = rm -f
STRIP = strip
TARGET_LIB = libHuntsmanDome.so

SRCS = src/main.cpp src/x2dome.cpp src/hx2dome.grpc.pb.cpp src/hx2dome.pb.cpp
OBJS = $(SRCS:.cpp=.o)

.PHONY: all
all: ${TARGET_LIB}

$(TARGET_LIB): $(OBJS)
	$(CXX) $^ ${LDFLAGS} -o $@
	$(STRIP) $@ >/dev/null 2>&1  || true

$(SRCS:.cpp=.d):%.d:%.cpp
	$(CXX) $(CFLAGS) $(CPPFLAGS) $(LDFLAGS) -MM $< >$@


.PHONY: clean
clean:
	${RM} ${TARGET_LIB} ${OBJS}
