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
"""The Python implementation of the GRPC helloworld.Greeter client."""

from __future__ import print_function
import logging

import grpc

import hx2dome_pb2
import hx2dome_pb2_grpc

# Just using this as a way to test the python server without having to use/debug the c++ client
def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = hx2dome_pb2_grpc.HX2DomeStub(channel)
        response = stub.dapiGotoAzEl(hx2dome_pb2.AzEl(return_code=1, az=10, el=20))
    print(type(response))
    print(f"HX2Dome client received: return_code={response.return_code}")


if __name__ == '__main__':
    logging.basicConfig()
    run()
