import argparse
import logging
import sys
import time
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
    """Remote Procedure Call (RPC) server object.

    Parameters
    ----------
    testing : bool
        Parameter to toggle testing (simulated hardware) mode.
    debug_lights : bool
        Parameter to toggle automationHAT status LEDs (automationHAT required).
    server_testing : bool
        Parameter to toggle server testing mode, to test communication between
        TheSkyX and the RPC server without needing any real or simulated
        hardware.

    Attributes
    ----------
    dome : Huntsman Dome object
        This the object that represents the Huntsman Dome as controlled via a
        raspberryPi and an automationHAT. It can also be initialised in a
        testing mode with simulated hardware.

    """

    def __init__(self, testing, debug_lights, server_testing):
        super(HX2DomeServer, self).__init__()
        # create the dome object that controls the dome hardware
        self.dome = Dome(testing=testing, debug_lights=debug_lights)
        self.server_testing = server_testing

    def dapiGetAzEl(self, request, context):
        """TheSkyX RPC to query the dome azimuth and slit position of the
        observatory.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        AzEl
            rpc response, a message of type 'AzEl' describing the dome's
            azimuth and slit elevation postions.

        """
        print(f'Receiving: GetAzEl request')
        # our cpp TheSkyX driver uses the dapiGetAzEl rpc to check link
        if self.server_testing:
            # if we just want to test communication between driver and server
            # we can just send back a dummy response
            response = hx2dome_pb2.AzEl(return_code=0, az=10.0, el=20.0)
            print(f'Sending: Az={response.az}, El={response.el}')
            return response
        else:
            return_code = 0
            try:
                dome_az = self.dome.getAz()
            except:
                # TODO: proper exception handling
                dome_az = None
            if dome_az is None:
                return_code = 1
            response = hx2dome_pb2.AzEl(return_code=return_code,
                                        az=dome_az,
                                        el=90.0)
            print(f'Sending: Az={response.az}, \
                  El={response.el}, \
                  ReturnCode={response.return_code}')
            return response

    def dapiGotoAzEl(self, request, context):
        """TheSkyX RPC to request a new dome azimuth and slit position for the
        observatory. Note observatory/dome slit control not implemented yet.

        Parameters
        ----------
        request : AzEl
            Incoming rpc request, a message of type 'AzEl' containing the
            desired Azimuth and Elevation positions for the observatory.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        ReturnCode
            rpc response, a message of type 'ReturnCode' that indicates the
            success/failure of the rpc request.

        """
        print(f'Receiving: GotoAzEl Az={request.az}, El={request.el}')
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            print(f'Sending: GotoAzEl complete,'
                  f' return code={response.return_code}\n')
            return response
        else:
            return_code = 0
            try:
                self.dome.GotoAz(request.az)
            except:
                # TODO: proper error handling
                return_code = 1
            response = hx2dome_pb2.ReturnCode(return_code=return_code)
            print(f'Sending: GotoAzEl complete,'
                  f' return code={response.return_code}\n')
            return response

    def dapiAbort(self, request, context):
        """TheSkyX RPC to abort any current dome movement.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        ReturnCode
            rpc response, a message of type 'ReturnCode' that indicates the
            success/failure of the rpc request.

        """
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            return response
        else:
            return_code = 0
            try:
                self.dome.abort()
            except:
                # TODO: proper error handling
                return_code = 1
            response = hx2dome_pb2.ReturnCode(return_code=return_code)
            return response

    def dapiOpen(self, request, context):
        """TheSkyX RPC to open dome slit.
        NOTE: this functionality isn't currently implemented.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        ReturnCode
            rpc response, a message of type 'ReturnCode' that indicates the
            success/failure of the rpc request.

        """
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            return response
        else:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            return response

    def dapiClose(self, request, context):
        """TheSkyX RPC to close dome slit.
        NOTE: this functionality isn't currently implemented.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        ReturnCode
            rpc response, a message of type 'ReturnCode' that indicates the
            success/failure of the rpc request.

        """
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            return response
        else:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            return response

    def dapiPark(self, request, context):
        """TheSkyX RPC to park the dome.
        NOTE: this functionality isn't currently implemented.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        ReturnCode
            rpc response, a message of type 'ReturnCode' that indicates the
            success/failure of the rpc request.

        """
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            return response
        else:
            # TODO: unsure what action to trigger in automationHAT for "Park"
            response = hx2dome_pb2.ReturnCode(return_code=0)
            return response

    def dapiUnpark(self, request, context):
        """TheSkyX RPC to unpark the dome.
        NOTE: this functionality isn't currently implemented.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        ReturnCode
            rpc response, a message of type 'ReturnCode' that indicates the
            success/failure of the rpc request.

        """
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            return response
        else:
            # TODO: unsure what action to trigger in automationHAT for "UnPark"
            response = hx2dome_pb2.ReturnCode(return_code=0)
            return response

    def dapiFindHome(self, request, context):
        """TheSkyX RPC to return dome to the home position.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        ReturnCode
            rpc response, a message of type 'ReturnCode' that indicates the
            success/failure of the rpc request.

        """
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            return response
        else:
            return_code = 0
            try:
                self.dome.find_home()
            except:
                # TODO: proper error handling
                return_code = 1
            response = hx2dome_pb2.ReturnCode(return_code=return_code)
            return response

    def dapiIsGotoComplete(self, request, context):
        """TheSkyX RPC to request the completetion status of dapiGotoAzEl.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        IsComplete
            rpc response, a message of type 'IsComplete' containing a
            return_code that indicates the success/failure of the rpc request.
            and a boolean is_complete that indicates if the relevant rpc
            has been completed.

        """
        print("      ITS DOING IT, ITS DOING IT    ")
        if self.server_testing:
            response = hx2dome_pb2.IsComplete(return_code=0, is_complete=True)
            return response
        else:
            is_dome_moving = self.dome.dome_in_motion
            # if dome is not moving lets just consider the command complete
            # TODO: better method of determine command completion
            is_complete = not is_dome_moving
            responnse = hx2dome_pb2.IsComplete(
                return_code=0, is_complete=is_dome_moving)

    def dapiIsOpenComplete(self, request, context):
        """TheSkyX RPC to request the completetion status of dapiOpen.
        NOTE: this functionality isn't currently implemented.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        IsComplete
            rpc response, a message of type 'IsComplete' containing a
            return_code that indicates the success/failure of the rpc request.
            and a boolean is_complete that indicates if the relevant rpc
            has been completed.

        """
        if self.server_testing:
            response = hx2dome_pb2.IsComplete(is_complete=True)
            return response
        else:
            # Shutter control is not implemented yet so no rpi code yet
            response = hx2dome_pb2.IsComplete(is_complete=True)
            return response
            pass

    def dapiIsCloseComplete(self, request, context):
        """TheSkyX RPC to request the completetion status of dapiClose.
        NOTE: this functionality isn't currently implemented.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        IsComplete
            rpc response, a message of type 'IsComplete' containing a
            return_code that indicates the success/failure of the rpc request.
            and a boolean is_complete that indicates if the relevant rpc
            has been completed.

        """
        if self.server_testing:
            response = hx2dome_pb2.IsComplete(is_complete=True)
            return response
        else:
            # Shutter control is not implemented yet so no rpi code yet
            response = hx2dome_pb2.IsComplete(is_complete=True)
            return response
            pass

    def dapiIsParkComplete(self, request, context):
        """TheSkyX RPC to request the completetion status of dapiPark.
        NOTE: this functionality isn't currently implemented.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        IsComplete
            rpc response, a message of type 'IsComplete' containing a
            return_code that indicates the success/failure of the rpc request.
            and a boolean is_complete that indicates if the relevant rpc
            has been completed.

        """
        if self.server_testing:
            response = hx2dome_pb2.IsComplete(is_complete=True)
            return response
        else:
            # TODO: unsure what action to trigger in automationHAT for "Park"
            # not really doing anything with park yet
            response = hx2dome_pb2.IsComplete(is_complete=True)
            return response
            pass

    def dapiIsUnparkComplete(self, request, context):
        """TheSkyX RPC to request the completetion status of dapiUnpark.
        NOTE: this functionality isn't currently implemented.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        IsComplete
            rpc response, a message of type 'IsComplete' containing a
            return_code that indicates the success/failure of the rpc request.
            and a boolean is_complete that indicates if the relevant rpc
            has been completed.

        """
        if self.server_testing:
            response = hx2dome_pb2.IsComplete(is_complete=True)
            return response
        else:
            # TODO: unsure what action to trigger in automationHAT for "Park"
            # not really doing anything with park yet
            response = hx2dome_pb2.IsComplete(is_complete=True)
            return response
            pass

    def dapiIsFindHomeComplete(self, request, context):
        """TheSkyX RPC to request the completetion status of dapiFindHome.

        Parameters
        ----------
        request : Empty
            Incoming rpc request, a message of type 'Empty'.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        IsComplete
            rpc response, a message of type 'IsComplete' containing a
            return_code that indicates the success/failure of the rpc request.
            and a boolean is_complete that indicates if the relevant rpc
            has been completed.

        """
        print("      PHONING HOME    ")
        if self.server_testing:
            response = hx2dome_pb2.IsComplete(is_complete=True)
            return response
        else:
            is_dome_moving = self.dome.dome_in_motion
            # if dome is not moving and dome.is_home returns True
            # lets just consider the command complete
            # TODO: better method of determine command completion
            is_complete = not is_dome_moving & self.dome.is_home
            responnse = hx2dome_pb2.IsComplete(is_complete=is_dome_moving)

    def dapiSync(self, request, context):
        """TheSkyX rpc to request a calibration of the dome followed by a new
        dome azimuth position.

        Parameters
        ----------
        request : AzEl
            Incoming rpc request, a message of type 'AzEl' containing the
            desired Azimuth and Elevation positions for the observatory.
        context : Dunno
            GRPC magic thingy.

        Returns
        -------
        ReturnCode
            rpc response, a message of type 'ReturnCode' that indicates the
            success/failure of the rpc request.

        """
        print("      IM SINKINGGGGGGGGG    ")
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            return response
        else:
            return_code = 0
            try:
                # First re calibrate dome encoder
                self.dome.calibrate_dome_encoder_counts()
                # after calibrating send dome to requested azimuth
                self.dome.GotoAz(request.az)
            except:
                # TODO: proper error handling
                return_code = 1
            response = hx2dome_pb2.ReturnCode(return_code=return_code)
            print(f'Sending: dapiSync complete,'
                  f' return code={response.return_code}\n')
            return response


def serve(kwargs_dict):
    """Set up the RPC server to run for a day or until interrupted.

    Parameters
    ----------
    kwargs_dict : dict
        Dictionary of boolean keyword args to pass to rpc server object.

    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hx2dome_pb2_grpc.add_HX2DomeServicer_to_server(
        HX2DomeServer(**kwargs_dict), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Remote Procedure Call server \
        for issuing observatory dome rotation commands.")

    parser.add_argument('-rh', '--run-with-real-hardware',
                        dest='testing',
                        action='store_false',
                        help="Run server with real hardware.")

    parser.add_argument('-sh', '--run-with-simulated-hardware',
                        dest='testing',
                        action='store_true',
                        help="Run server with simulated hardware.")

    parser.set_defaults(testing=True)

    parser.add_argument('-rdbl', '--run-with-debug-lights',
                        dest='debug_lights',
                        action='store_true',
                        help="Enable debug lights on automationHAT")

    parser.set_defaults(debug_lights=False)

    parser.add_argument('-rst', '--run-in-server-test-mode',
                        dest='server_testing',
                        action='store_true',
                        help="Mode for testing TheSkyX driver to server \
                        communication. Server will return dummy messages \
                        to the TheSkyX.")
    parser.set_defaults(server_testing=False)

    kwargs_dict = vars(parser.parse_args())

    logging.basicConfig()
    serve(kwargs_dict)
