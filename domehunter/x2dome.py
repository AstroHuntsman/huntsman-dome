"""Main class to interface to X2Dome TSX driver."""


class X2Dome():
    """Interface to X2Driver from TSX.

    I think this will look like this:
    http://www.bisque.com/x2standard/class_x2_dome.html
    as it must monitor for these calls and take appropriate
    action based upon the call.
    """

    def __init__(self, *args, **kwargs):
        """Establish X2 connection."""
        pass

    def connect(self):
        print("Connecting to X2Driver")

    def disconnect(self):
        print("Disconnecting X2Driver")
