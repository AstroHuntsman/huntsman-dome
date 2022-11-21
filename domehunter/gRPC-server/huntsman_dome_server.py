import argparse
import time
import os.path
from concurrent import futures

import grpc

import hx2dome_pb2
import hx2dome_pb2_grpc
from domehunter.dome_control import Dome, load_dome_config
from domehunter.logging import set_up_logger

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

    def __init__(self, home_az, logger, **kwargs):
        super(HX2DomeServer, self).__init__()
        # create the dome object that controls the dome hardware
        self.dome = Dome(home_az, **kwargs)
        self.logger = logger
        self.server_testing = kwargs['server_testing']
        self.logger.notice('Dome server initialised.')

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
        self.logger.notice('Receiving: GetAzEl request')
        # our cpp TheSkyX driver uses the dapiGetAzEl rpc to check link
        if self.server_testing:
            # if we just want to test communication between driver and server
            # we can just send back a dummy response
            response = hx2dome_pb2.AzEl(return_code=0, az=10.0, el=20.0)
            self.logger.notice(
                (f'Sending: Az={response.az:.2f}'
                 f', El={response.el:.2f}'))
        else:
            return_code = 0
            try:
                dome_az = self.dome.dome_az.degree
            except Exception:
                # TODO: proper exception handling
                dome_az = None
            if dome_az is None:
                return_code = 1
            response = hx2dome_pb2.AzEl(return_code=return_code,
                                        az=dome_az,
                                        el=90.0)
            self.logger.notice((f'Sending: Az={response.az:.2f}, '
                                f'El={response.el:.2f}, '
                                f'ReturnCode={response.return_code}'))
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
        self.logger.notice(
            f'Receiving: GotoAzEl Az={request.az:.2f}, El={request.el:.2f}'
        )
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            self.logger.notice(
                (f'Sending: GotoAzEl complete,'
                 f' return code={response.return_code}\n')
            )
        else:
            return_code = 0
            try:
                self.dome.goto_az(request.az)
            except Exception:
                # TODO: proper error handling
                return_code = 1
            response = hx2dome_pb2.ReturnCode(return_code=return_code)
            self.logger.notice(
                (f'Sending: GotoAzEl complete,'
                 f' return code={response.return_code}\n')
            )
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
        else:
            return_code = 0
            try:
                self.dome.abort()
            except Exception:
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
        self.logger.notice('Receiving: Park Dome.')
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            self.logger.notice(f'Sending: Park Dome complete,'
                               f' return code={response.return_code}\n')
        else:
            try:
                return_code = self.dome.park()
            except Exception:
                # TODO: proper error handling
                return_code = 1
            response = hx2dome_pb2.ReturnCode(return_code=return_code)
            self.logger.notice(f'Sending: Park Dome complete,'
                               f' return code={response.return_code}\n')
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
        self.logger.notice('Receiving: Unpark Dome.')
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
            self.logger.notice(f'Sending: Unpark Dome complete,'
                               f' return code={response.return_code}\n')
        else:
            try:
                return_code = self.dome.unpark()
            except Exception:
                # TODO: proper error handling
                return_code = 1
            response = hx2dome_pb2.ReturnCode(return_code=return_code)
            self.logger.notice(f'Sending: Unpark Dome complete,'
                               f' return code={response.return_code}\n')
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
        else:
            return_code = 0
            try:
                self.dome.find_home()
            except Exception:
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
        self.logger.info("GotoAzEl successfully completed.")
        if self.server_testing:
            response = hx2dome_pb2.IsComplete(return_code=0, is_complete=True)
        else:
            is_dome_moving = self.dome.dome_in_motion
            # if dome is not moving lets just consider the command complete
            # TODO: better method of determine command completion
            is_complete = not is_dome_moving
            response = hx2dome_pb2.IsComplete(
                return_code=0, is_complete=is_complete)
        return response

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
            response = hx2dome_pb2.IsComplete(return_code=0, is_complete=True)
        else:
            # Shutter control is not implemented yet so no rpi code yet
            response = hx2dome_pb2.IsComplete(return_code=0, is_complete=True)
        return response

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
            response = hx2dome_pb2.IsComplete(return_code=0, is_complete=True)
        else:
            # Shutter control is not implemented yet so no rpi code yet
            response = hx2dome_pb2.IsComplete(return_code=0, is_complete=True)
        return response

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
            response = hx2dome_pb2.IsComplete(return_code=0, is_complete=True)
        else:
            is_complete = self.dome.is_parked
            response = hx2dome_pb2.IsComplete(return_code=0, is_complete=is_complete)
        return response

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
            response = hx2dome_pb2.IsComplete(return_code=0, is_complete=True)
        else:
            is_complete = not self.dome.is_parked
            response = hx2dome_pb2.IsComplete(return_code=0, is_complete=is_complete)
        return response

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
        self.logger.info("FindHome successfully completed.")
        if self.server_testing:
            response = hx2dome_pb2.IsComplete(return_code=0, is_complete=True)
        else:
            is_dome_moving = self.dome.dome_in_motion
            # if dome is not moving and dome.at_home returns True
            # lets just consider the command complete
            # TODO: better method of determine command completion
            is_complete = not is_dome_moving and not self.dome._unhomed
            response = hx2dome_pb2.IsComplete(
                return_code=0, is_complete=is_complete)
        return response

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
        self.logger.info("Sync successfully completed.")
        if self.server_testing:
            response = hx2dome_pb2.ReturnCode(return_code=0)
        else:
            return_code = 0
            try:
                # First sync TheSkyX azimuth with dome encoder counts
                self.dome.sync(request.az)
            except Exception:
                # TODO: proper error handling
                return_code = 1
            response = hx2dome_pb2.ReturnCode(return_code=return_code)
            self.logger.notice(
                (f'Sending: dapiSync complete,'
                 f' return code={response.return_code}\n')
            )
        return response


def serve(home_az, logger, **kwargs):
    """Set up the RPC server to run for a day or until interrupted.

    Parameters
    ----------
    kwargs_dict : dict
        Dictionary of boolean keyword args to pass to rpc server object.

    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    hx2dome_pb2_grpc.add_HX2DomeServicer_to_server(
        HX2DomeServer(home_az, logger, **kwargs), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logger.critical('Keyboard Interrupt, closing up shop.')
        server.stop(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=("Remote Procedure Call server for issuing observatory "
                     "dome rotation commands.")
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-r', '--real',
                       dest='testing',
                       action='store_false',
                       help="Run server with real hardware.")

    group.add_argument('-s', '--simulated',
                       dest='testing',
                       action='store_true',
                       help="Run server with simulated hardware.")

    parser.set_defaults(testing=True)

    parser.add_argument('-l', '--lights',
                        dest='debug_lights',
                        action='store_true',
                        help="Enable debug lights on automationHAT")

    parser.set_defaults(debug_lights=False)

    parser.add_argument('-d', '--dummyserver',
                        dest='server_testing',
                        action='store_true',
                        help=("Mode for testing TheSkyX driver to server "
                              "communication. Server will return dummy "
                              "messages to the TheSkyX.")
                        )
    parser.set_defaults(server_testing=False)

    parser.add_argument('-c', '--config',
                        dest='config',
                        help=("YAML file containing cofiguration details for "
                              "the dome controller.")
                        )
    default_config = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                  'dome_controller_config.yml')
    parser.set_defaults(config=default_config)

    flags = parser.parse_args()

    # TODO: have some way of running dome with the defaults defined in the init
    # rather than running from a specified or default yaml file
    if flags.config is None:
        # if we don't want to use a yaml file, pass an empty dictionary though
        config = dict()
    else:
        config = load_dome_config(config_path=flags.config)

    kwargs = {**vars(flags), **config}

    # extract home_az from dictionary to pass it through to serve as an arg
    home_az = kwargs.pop('home_azimuth', None)
    # extract the logfile and stderr log levels from kwargs, default to 'DEBUG'
    server_log_file_level = kwargs.pop('server_log_file_level', 'DEBUG')
    server_log_stderr_level = kwargs.pop('server_log_stderr_level', 'DEBUG')
    if home_az is None:
        raise ValueError(
            "Dome instance requires a home azimuth, none provided.")

    logger = set_up_logger(__name__,
                           'server_log.log',
                           log_file_level=server_log_file_level,
                           log_stderr_level=server_log_stderr_level,
                           logo=False)
    logger.notice('Serving up some dome pi.')
    serve(home_az, logger, **kwargs)
