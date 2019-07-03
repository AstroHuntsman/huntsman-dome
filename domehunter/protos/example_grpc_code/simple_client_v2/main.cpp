#include "hx2dome.proto_client.h"


int main(int argc, char** argv) {
  // Instantiate the client. It requires a channel, out of which the actual RPCs
  // are created. This channel models a connection to an endpoint (in this case,
  // localhost at port 50051). We indicate that the channel isn't authenticated
  // (use of InsecureChannelCredentials()).
  HX2DomeClient hx2dome(grpc::CreateChannel(
      "localhost:50051", grpc::InsecureChannelCredentials()));
  int rc(1);
  double a(10);
  double e(20);
  int result;
  result = hx2dome.dapiGotoAzEl(rc, a, e);
  // int output(dynamic_cast<char>(result.return_code()));
  std::cout << "HX2Dome receiving: " << result << std::endl;

  return 0;
}
