"""Importable access to the generated hx2dome gRPC stubs.

The stubs live in ``gRPC-server/`` (not a Python package), next to the server
that imports them as top-level modules. Other code that installs domehunter,
such as the observatory automation's rotation-policy client, uses::

    from domehunter.hx2dome import pb2, pb2_grpc

This loads the same generated files; nothing is copied or regenerated.
"""
import importlib.util
import sys
from pathlib import Path

_SERVER_DIR = Path(__file__).parent / 'gRPC-server'


def _load(name):
    # hx2dome_pb2_grpc does `import hx2dome_pb2`, so register under the
    # top-level names the generated code expects.
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, _SERVER_DIR / f'{name}.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


pb2 = _load('hx2dome_pb2')
pb2_grpc = _load('hx2dome_pb2_grpc')
