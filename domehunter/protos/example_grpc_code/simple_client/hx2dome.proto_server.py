from concurrent import futures
import time
import logging

import grpc

import hx2dome_pb2
import hx2dome_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class HX2DomeServer(hx2dome_pb2_grpc.HX2DomeServicer):

    def dapiGotoAzEl(self, request, context):
        # print something for debugging, so I know python server is actually getting a request from client
        print(f'Receiving: {request.return_code}')
        time.sleep(1)
        # increment the return code by 1 so I can see the client/server communication is working
        response = hx2dome_pb2.ReturnCode(return_code=request.return_code+1)
        print(f'Sending: {response.return_code}\n')
        time.sleep(1)
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
