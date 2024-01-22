#!/usr/bin/python

from os import environ as env


""" Connection settings

    For ledhost: the hostname and port to listen to.
    For clients: the hostname and port to connect to.
"""
CONNECT_HOST = "localhost"
CONNECT_PORT = 5729

# Use environment variables instead, if available.
if "LEDHOST_HOST" in env:   CONNECT_HOST = env["LEDHOST_HOST"]
if "LEDHOST_PORT" in env:  CONNECT_PORT = int(env["LEDHOST_PORT"])

#  A tuple of the host and port, for convenience's sake.
CONNECT = (CONNECT_HOST, CONNECT_PORT)


""" Pimoroni Blinkt settings

    Default brightness in percentages, derived from blinkt.py
    which defines DEFAULT_BRIGHTNESS = 7, and then in set_brightness
    multiplies by 31 and bitwise-ands that with 0b11111:

        >>> (31*7) & 0b11111
        25
"""
BRIGHTNESS = 25


""" Frame settings

    FPS:
        Frames per settings

    FRAME_LENGTH:
        Convenience variable: length of 1 frame, in seconds.

    KEEP_ALIVE:
        Number of seconds to wait before expiring a led. When a led
        expires, the next planned frame will be shown.
        If there are no planned frames for this led, the topmost frame
        of the stack will be popped onto the led. If the stack is empty,
        the led will be turned off.

    MAX_KEEP_ALIVE:
        The highes allowed value for the `keepalive=...` key/value pair.

    KEEP_ALIVE_BLINK:
        Number of seconds to wait before expiring led set or planned with
        the &keepalive flag.

"""
FPS=24
FRAME_LENGTH=1/FPS

KEEP_ALIVE = 10
MAX_KEEP_ALIVE = 30

KEEP_ALIVE_BLINK = 0.3


# For ledhost: limit how many frames can be held in the stack, the plan, and
# the blink plan.
MAX_STACK_SIZE = 10
MAX_PLAN_SIZE = 1000


# For ledhost: what to do if a request would cause a stack or queue to exceed
# their maximum size?
# Valid values are:
ON_EXCEED_BYE   = 0xB00F    # Disconnect the 'offending' client
ON_EXCEED_CLEAR = 0xC00F    # Clear stacks or queues before adding frames
ON_EXCEED_DENY  = 0xD00F    # Don't add any more frames
ON_EXCEED_MAX_STACK_SIZE = ON_EXCEED_DENY
ON_EXCEED_MAX_QUEUE_SIZE = ON_EXCEED_DENY





""" Behaviour settings

    GREENHACK:
        Apply the hack for green's intensity?
        Blatantly stolen from 
        https://github.com/pimoroni/blinkt/blob/master/projects/mqtt/mqtt.py

        Can be changed with a `:config greenhack=TOGGLE` message, where
        TOGGLE is either `on` or `off`.

    SWAP:
        If False, `:set #0 ...` sets Blinkt pixel 0. If True, that same
        message sets Blinkt pixel 7. Useful if your Raspberry Pi is in an
        orientation where pixel 7 is logically the first led.
"""
GREENHACK = True
SWAP = True


# For ledhost: show a heartbeat every now and then on to indicate that
# ledhost is running.
# On which led to show the beartbeat? Set to None to disable this feature.
HEARTBEAT_LED = 7
# RGB values for the heartbeat pulses.
HEARTBEAT_RGB = (64,64,64)

# How many seconds between heartbeats?
HEARTBEAT_INTERVAL = 5


DBG_CONN_ACCEPT = 0b00000001
DBG_CONN_CLOSE  = 0b00000010
DBG_CONN_READ   = 0b00000100
DBG_CONN_WRITE  = 0b00001000
DBG_MSG_ERR     = 0b00010000
DBG_EXCEPTION   = 0b00100000

DEBUG = DBG_CONN_ACCEPT \
      | DBG_CONN_CLOSE  \
      | DBG_CONN_READ   \
      | DBG_CONN_WRITE  \
      | DBG_MSG_ERR     \
      | DBG_EXCEPTION

DEBUG_LED = 7
