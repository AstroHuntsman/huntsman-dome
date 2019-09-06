import logging
import time
import sys
from concurrent import futures

import grpc

import hx2dome_pb2
import hx2dome_pb2_grpc
from domehunter import Dome

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

# list of RPCs defined in the proto file
# dapiGetAzEl             (google.protobuf.Empty)   returns   (AzEl)       {};
# dapiGotoAzEl            (AzEl)                    returns   (ReturnCode) {};
# dapiAbort               (google.protobuf.Empty)   returns   (ReturnCode) {};
# dapiOpen                (google.protobuf.Empty)   returns   (ReturnCode) {};
# dapiClose               (google.protobuf.Empty)   returns   (ReturnCode) {};
# dapiPark                (google.protobuf.Empty)   returns   (ReturnCode) {};
# dapiUnpark              (google.protobuf.Empty)   returns   (ReturnCode) {};
# dapiFindHome            (google.protobuf.Empty)   returns   (ReturnCode) {};
# dapiIsGotoComplete      (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiIsOpenComplete      (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiIsCloseComplete     (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiIsParkComplete      (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiIsUnparkComplete    (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiIsFindHomeComplete  (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiSync                (AzEl)                    returns   (ReturnCode) {};


class HX2DomeServer(hx2dome_pb2_grpc.HX2DomeServicer):

    def __init__(self, testing, debug_lights):
        super(HX2DomeServer, self).__init__()
        self.dome = Dome(testing=testing, debug_lights=debug_lights)

    def dapiGetAzEl(self, request, context):
        print(f'Receiving: GetAzEl request')
        # our cpp TheSkyX driver uses the dapiGetAzEl rpc to check link
        # need to add code to get az and el from rpi
        # for now just give dummy numbers
        # if something wrong with rpi and no response change return code
        response = hx2dome_pb2.AzEl(return_code=1, az=10.0, el=20.0)
        print(f'Sending: Az={response.az}, El={response.el}')
        return response

    def dapiGotoAzEl(self, request, context):
        # print something for debugging
        # so I know python server is actually getting a request from client
        print(f'Receiving: GotoAzEl Az={request.az}, El={request.el}')
        # increment the return code by 1 so I can see the client/server
        # communication is working
        response = hx2dome_pb2.ReturnCode(return_code=request.return_code)
        print(f'Sending: GotoAzEl complete,'
              f' return code={response.return_code}\n')
        return response

    def dapiAbort(self, request, context):
        # add in rpi code to stop all dome operations
        # maybe print to console/any rpi side logging
        response = hx2dome_pb2.ReturnCode(return_code=0)
        return response

    def dapiOpen(self, request, context):
        response = hx2dome_pb2.ReturnCode(return_code=0)
        return response

    def dapiClose(self, request, context):
        response = hx2dome_pb2.ReturnCode(return_code=0)
        return response

    def dapiPark(self, request, context):
        response = hx2dome_pb2.ReturnCode(return_code=0)
        return response

    def dapiUnpark(self, request, context):
        response = hx2dome_pb2.ReturnCode(return_code=0)
        return response

    def dapiFindHome(self, request, context):
        response = hx2dome_pb2.ReturnCode(return_code=0)
        return response

    def dapiIsGotoComplete(self, request, context):
        print("      ITS DOING IT, ITS DOING IT    ")
        response = hx2dome_pb2.IsComplete(is_complete=True)
        return response

    def dapiIsOpenComplete(self, request, context):
        response = hx2dome_pb2.IsComplete(is_complete=True)
        return response

    def dapiIsCloseComplete(self, request, context):
        response = hx2dome_pb2.IsComplete(is_complete=True)
        return response

    def dapiIsParkComplete(self, request, context):
        response = hx2dome_pb2.IsComplete(is_complete=True)
        return response

    def dapiIsUnparkComplete(self, request, context):
        response = hx2dome_pb2.IsComplete(is_complete=True)
        return response

    def dapiIsFindHomeComplete(self, request, context):
        print("      PHONING HOME    ")
        response = hx2dome_pb2.IsComplete(is_complete=True)
        return response

    def dapiSync(self, request, context):
        print("      IM SINKINGGGGGGGGG    ")
        response = hx2dome_pb2.ReturnCode(return_code=0)
        return response


def serve(testing, debug_lights):
    # TODO add shell arguments for testing and debug_lights mode
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hx2dome_pb2_grpc.add_HX2DomeServicer_to_server(
        HX2DomeServer(testing, debug_lights), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) == 3:
            testing = str_to_bool(sys.argv[1])
            debug_lights = str_to_bool(sys.argv[2])
        else:
            print("""Incorrect number of command line parameters supplied.\n
                  To run server with defaults try:\n
                  $ python hx2dome.proto_server.py\n
                  To toggle testing and debug_lights on try:\n
                  $ python hx2dome.proto_server.py True True""")
            sys.exit(1)
    else:
        testing = True
        debug_lights = True

    logging.basicConfig()
    serve(testing, debug_lights)


def str_to_bool(string):
    if string.lower() == 'true':
        return True
    elif string.lower() == 'false':
        return False
    else:
        raise ValueError('Command line parameters must be True or False')
