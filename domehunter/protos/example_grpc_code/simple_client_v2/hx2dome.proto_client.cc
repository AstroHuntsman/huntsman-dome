#include "hx2dome.proto_client.h"


int HX2DomeClient::dapiGotoAzEl(int rc, double az, double el)
{
  // Data we are sending to the server.
  AzEl request;
  request.set_return_code(rc);
  request.set_az(az);
  request.set_el(el);
  std::cout << "HX2Dome sending: " << request.return_code() << std::endl;

  // Container for the data we expect from the server.
  ReturnCode reply;

  // Context for the client. It could be used to convey extra information to
  // the server and/or tweak certain RPC behaviors.
  ClientContext context;

  // The actual RPC.
  Status status = stub_->dapiGotoAzEl(&context, request, &reply);

  // std::cout << status.ok() << std::endl;

  // Act upon its status.
  if (status.ok()) {
    return reply.return_code();
  } else {
    std::cout << status.error_code() << ": " << status.error_message()
              << std::endl;
    int fail(666);
    return fail;
  }
}
