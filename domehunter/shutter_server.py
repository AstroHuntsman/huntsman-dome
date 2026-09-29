"""gRPC shutter server for the Huntsman dome Musca controller.

Runs on the Ubuntu control box (where the Bluetooth dongle lives) and
exposes shutter open/close via the same hx2dome.proto used by the X2 driver.
Listens on localhost:50052 by default.

Usage:
    python shutter_server.py [--config shutter_config.yml]
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from concurrent import futures

import grpc
import yaml

# The generated stubs live alongside the gRPC-server directory
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "gRPC-server")
)
import hx2dome_pb2
import hx2dome_pb2_grpc

from domehunter.musca import MuscaConfig, MuscaController

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s][%(levelname)-8s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class ShutterServer(hx2dome_pb2_grpc.HX2DomeServicer):
    """gRPC servicer that handles dome shutter open/close via the Musca.

    Only implements the four shutter-related RPCs. All other RPCs return
    UNIMPLEMENTED (the X2 driver never routes them here).
    """

    def __init__(self, musca: MuscaController):
        super().__init__()
        self.musca = musca

    def dapiOpen(self, request, context):
        logger.info("Receiving: dapiOpen (shutter)")
        try:
            self.musca.open_shutter()
            return hx2dome_pb2.ReturnCode(return_code=0)
        except RuntimeError as e:
            logger.warning("dapiOpen refused: %s", e)
            return hx2dome_pb2.ReturnCode(
                return_code=1, error_message=str(e)
            )
        except Exception as e:
            logger.error("dapiOpen failed: %s", e)
            return hx2dome_pb2.ReturnCode(
                return_code=1, error_message=f"Shutter open failed: {e}"
            )

    def dapiClose(self, request, context):
        logger.info("Receiving: dapiClose (shutter)")
        try:
            self.musca.close_shutter()
            return hx2dome_pb2.ReturnCode(return_code=0)
        except Exception as e:
            logger.error("dapiClose failed: %s", e)
            return hx2dome_pb2.ReturnCode(
                return_code=1, error_message=f"Shutter close failed: {e}"
            )

    def dapiIsOpenComplete(self, request, context):
        logger.debug("Receiving: dapiIsOpenComplete (shutter)")

        # If BT dropped and watchdog has likely fired, report error
        if self.musca.shutter_assumed_closed:
            logger.warning(
                "BT dropout exceeded watchdog timeout — "
                "Musca has likely auto-closed the shutter"
            )
            return hx2dome_pb2.IsComplete(return_code=1, is_complete=False)

        # Poll fresh status from Musca
        try:
            status = self.musca.request_status()
        except Exception:
            # If we can't get status, report not complete
            return hx2dome_pb2.IsComplete(return_code=0, is_complete=False)

        is_complete = status.shutter == "Open"
        return hx2dome_pb2.IsComplete(return_code=0, is_complete=is_complete)

    def dapiIsCloseComplete(self, request, context):
        logger.debug("Receiving: dapiIsCloseComplete (shutter)")

        # If BT dropped and watchdog fired, Musca auto-closed — report complete
        if self.musca.shutter_assumed_closed:
            logger.info(
                "BT dropout exceeded watchdog — "
                "assuming Musca auto-closed the shutter"
            )
            return hx2dome_pb2.IsComplete(return_code=0, is_complete=True)

        try:
            status = self.musca.request_status()
        except Exception:
            return hx2dome_pb2.IsComplete(return_code=0, is_complete=False)

        is_complete = status.shutter == "Closed"
        return hx2dome_pb2.IsComplete(return_code=0, is_complete=is_complete)


def load_shutter_config(config_path: str) -> MuscaConfig:
    """Load shutter configuration from a YAML file."""
    with open(config_path, "r") as f:
        data = yaml.safe_load(f) or {}
    return MuscaConfig(**data)


def serve(musca: MuscaController, port: int = 50052):
    """Start the gRPC server and block until interrupted."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    hx2dome_pb2_grpc.add_HX2DomeServicer_to_server(
        ShutterServer(musca), server
    )
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    logger.info("Shutter gRPC server listening on port %d", port)
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        logger.info("Shutting down shutter server")
        musca.close_shutter()
        musca.disconnect()
        server.stop(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="gRPC shutter server for Huntsman Musca dome controller"
    )
    parser.add_argument(
        "-c", "--config",
        dest="config",
        help="YAML config file for the shutter controller",
    )
    default_config = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "gRPC-server", "shutter_config.yml",
    )
    parser.set_defaults(config=default_config)

    parser.add_argument(
        "-p", "--port",
        dest="port",
        type=int,
        default=50052,
        help="gRPC listen port (default: 50052)",
    )

    flags = parser.parse_args()

    config = load_shutter_config(flags.config)
    musca = MuscaController(config)

    logger.info("Connecting to Musca on %s ...", config.serial_port)
    try:
        musca.connect()
    except ConnectionError as e:
        logger.error("Initial connection failed: %s", e)
        logger.info("Server will start anyway — Musca will reconnect when available")

    serve(musca, port=flags.port)
