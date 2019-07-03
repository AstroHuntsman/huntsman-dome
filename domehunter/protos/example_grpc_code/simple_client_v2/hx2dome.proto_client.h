#include <iostream>
#include <memory>
#include <string>

#include <grpcpp/grpcpp.h>

#ifdef BAZEL_BUILD
#include "/home/fergus/Documents/REPOS/huntsman-dome/domehunter/protos/example_grpc_code/simple_client_v2/hx2dome.grpc.pb.h"
#else
#include "hx2dome.grpc.pb.h"
#endif

using grpc::Channel;
using grpc::ClientContext;
using grpc::Status;
using hx2dome::ReturnCode;
using hx2dome::AzEl;
using hx2dome::IsComplete;
using hx2dome::BasicString;
using hx2dome::HX2Dome;


class HX2DomeClient {
 public:
  HX2DomeClient(std::shared_ptr<Channel> channel)
      : stub_(HX2Dome::NewStub(channel)) {}

  virtual int dapiGotoAzEl(int rc, double az, double el);

 private:
  std::unique_ptr<HX2Dome::Stub> stub_;
};
