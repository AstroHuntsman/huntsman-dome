from concurrent import futures
import time
import logging

import grpc

import hx2dome_pb2
import hx2dome_pb2_grpc

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

    def dapiGetAzEl(self, request, context):
        print(f'Receiving: GetAzEl request')
        time.sleep(1)

        # our cpp TheSkyX driver uses the dapiGetAzEl rpc to check link
        # need to add code to get az and el from rpi
        # for now just give dummy numbers
        # if something wrong with rpi and no response change return code
        response = hx2dome_pb2.AzEl(return_code=1, az=10.0, el=20.0)
        print(f'Sending: Az={response.az}, El={response.el}')
        time.sleep(1)
        return response

    def dapiGotoAzEl(self, request, context):
        # print something for debugging
        # so I know python server is actually getting a request from client
        print(f'Receiving: GotoAzEl Az={request.az}, El={request.el}')
        time.sleep(1)
        # increment the return code by 1 so I can see the client/server
        # communication is working
        response = hx2dome_pb2.ReturnCode(return_code=request.return_code)
        print(f'Sending: GotoAzEl complete,'
              f' return code={response.return_code}\n')
        time.sleep(1)
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


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hx2dome_pb2_grpc.add_HX2DomeServicer_to_server(HX2DomeServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig()
    serve()
