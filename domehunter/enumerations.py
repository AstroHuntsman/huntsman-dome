from enum import IntFlag, IntEnum, Enum


class Direction(IntEnum):
    CW = +1
    CCW = -1
    NONE = 0


class LED_light(IntFlag):
    POWER = 0b100000000000000000
    COMMS = 0b010000000000000000
    WARN = 0b001000000000000000
    INPUT_1 = 0b000100000000000000
    INPUT_2 = 0b000010000000000000
    INPUT_3 = 0b000001000000000000
    RELAY_3_NC = 0b000000100000000000
    RELAY_3_NO = 0b000000010000000000
    RELAY_2_NC = 0b000000001000000000
    RELAY_2_NO = 0b000000000100000000
    RELAY_1_NC = 0b000000000010000000
    RELAY_1_NO = 0b000000000001000000
    OUTPUT_3 = 0b000000000000100000
    OUTPUT_2 = 0b000000000000010000
    OUTPUT_1 = 0b000000000000001000
    ADC_3 = 0b000000000000000100
    ADC_2 = 0b000000000000000010
    ADC_1 = 0b000000000000000001


class ReturnCode(Enum):
    # No error.
    SB_OK = 0

    # |No error.|
    ERR_NOERROR = 0

    # |The operation failed because there is no connection to the device.|
    ERR_COMMNOLINK = 200

    # |Could not open communications port.  The port is either in use by
    # another application or not recognized by the system.|
    ERR_COMMOPENING = 201

    # |The communications port could not support the specified settings.|
    ERR_COMMSETTINGS = 202

    # |No response from the device.|
    ERR_NORESPONSE = 203

    # |Error: memory error.|
    ERR_MEMORY = 205

    # |Error: command failed.|
    ERR_CMDFAILED = 206

    # |Transmit time-out.|
    ERR_DATAOUT = 207

    # |Transmission time-out.|
    ERR_TXTIMEOUT = 208

    # |Receive time-out.|
    ERR_RXTIMEOUT = 209

    # |Process aborted.|
    ERR_ABORTEDPROCESS = 212

    # |Error, poor communication, connection automatically terminated.|
    ERR_AUTOTERMINATE = 213

    # |Error, cannot connect to host.|
    ERR_INTERNETSETTINGS = 214

    # |No connection to the device.|
    ERR_NOLINK = 215

    # |Error, the device is parked and must be unparked using the Unpark
    # command before roceeding.|
    ERR_DEVICEPARKED = 216

    # |A necessary driver was not found.|
    ERR_DRIVERNOTFOUND = 217

    # |Limits exceeded.|
    ERR_LIMITSEXCEEDED = 218

    # |Command in progress.|
    ERR_COMMANDINPROGRESS = 219

    # |A Dome command is already in progress.|
    ERR_CMD_IN_PROGRESS_DOME = 123

    # |Error, no park position has been set.|
    ERR_NOPARKPOSITION = 234

    # |Unknown response.|
    ERR_UNKNOWNRESPONSE = 302

    # |Unknown command.|
    ERR_UNKNOWNCMD = 303
