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
# dapiGotoComplete        (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiOpenComplete        (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiCloseComplete       (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiParkComplete        (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiUnparkComplete      (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiFindHomeComplete    (google.protobuf.Empty)   returns   (IsComplete) {};
# dapiSync                (AzEl)                    returns   (ReturnCode) {};


class HX2DomeServer(hx2dome_pb2_grpc.HX2DomeServicer):

    def dapiGetAzEl(self, request, context):
        print(f'Receiving: GetAzEl request')
        time.sleep(1)
        # send back a made up AzEl
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
        response = hx2dome_pb2.ReturnCode(return_code=request.return_code+1)
        print(f'Sending: GotoAzEl complete,'
              ' return code={response.return_code}\n')
        time.sleep(1)
        return response

    def dapiAbort(self, request, context):
        return None

    def dapiOpen(self, request, context):
        return None

    def dapiClose(self, request, context):
        return None

    def dapiPark(self, request, context):
        return None

    def dapiUnpark(self, request, context):
        return None

    def dapiFindHome(self, request, context):
        return None

    def dapiGotoComplete(self, request, context):
        return None

    def dapiOpenComplete(self, request, context):
        return None

    def dapiCloseComplete(self, request, context):
        return None

    def dapiParkComplete(self, request, context):
        return None

    def dapiUnparkComplete(self, request, context):
        return None

    def dapiFindHomeComplete(self, request, context):
        return None

    def dapiSync(self, request, context):
        return None


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
