# FMSPy - Copyright (c) 2009 Andrey Smirnov.
#
# See COPYRIGHT for details.

"""
RTMP protocol constants.
"""

HANDSHAKE_SIZE =            1536
DEFAULT_CHUNK_SIZE =        128

# RTMP packet kinds
CHUNK_SIZE =                0x01
# Unknown:                  0x02
BYTES_READ =                0x03
PING =                      0x04
SERVER_BW =                 0x05
CLIENT_BW =                 0x06
# Unknown:                  0x07
AUDIO_DATA  =               0x08
VIDEO_DATA  =               0x09
# Unknown:                  0x0A ... 0x0E
FLEX_STREAM =               0x0F
FLEX_SHARED_OBJECT =        0x10
FLEX_MESSAGE =              0x11
NOTIFY =                    0x12
STREAM_METADATA =           0x12
SO =                        0x13
INVOKE =                    0x14

DEFAULT_INVOKE_OBJECT_ID =  0x03
#
ACTION_CONNECT =            "connect"
ACTION_DISCONNECT =         "disconnect"
ACTION_CREATE_STREAM =      "createStream"
ACTION_DELETE_STREAM =      "deleteStream"
ACTION_CLOSE_STREAM =       "closeStream"
ACTION_RELEASE_STREAM =     "releaseStream"
ACTION_PUBLISH =            "publish"
ACTION_PAUSE =              "pause"
ACTION_SEEK =               "seek"
ACTION_PLAY =               "play"
ACTION_STOP =               "disconnect"
ACTION_RECEIVE_VIDEO =      "receiveVideo"
ACTION_RECEIVE_AUDIO =      "receiveAudio"
