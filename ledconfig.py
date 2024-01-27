#!/usr/bin/python

from os import environ as env
import ledutil


""" Connection settings
    ===================

    The settings in this section pertain to establishing a connection between
    ledhost and clients: which hostname and port will ledhost listen to, and
    thus which hostname and port should clients connect to?

    CONNECT_HOST:
    CONNECT_PORT:
        For ledhost: the hostname and port to listen to.
        For clients: the hostname and port to connect to.

    If the environment variables LEDHOST_HOST and LEDHOST_PORT are defined,
    the values of those will be used instead of the default values listed here.

    CONNECT:
        For convenience's sake. A tuple of host and port.
"""
CONNECT_HOST = "localhost"
CONNECT_PORT = 5729
if "LEDHOST_HOST" in env: CONNECT_HOST = env["LEDHOST_HOST"]
if "LEDHOST_PORT" in env: CONNECT_PORT = int(env["LEDHOST_PORT"])
CONNECT = (CONNECT_HOST, CONNECT_PORT)


""" Pimoroni Blinkt settings
    ========================

    BRIGHTNESS:
        Default brightness in percentages, derived from blinkt.py
        which defines DEFAULT_BRIGHTNESS = 7, and then in set_brightness
        multiplies by 31 and bitwise-ands that with 0b11111:

        >>> (31*7) & 0b11111
        25

        TODO: Implement using this setting.
"""
BRIGHTNESS = 25


""" Frame settings
    ==============

    FPS:
        Frames per second. Notably, fade effects use the FPS settings to
        determine the number of frames to use for their gradients.

    FRAME_LENGTH:
        Convenience variable: length of 1 frame, in seconds, rounded to
        two decimals.

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
        the &blink flag.

    FADEIN_DURATION:
        Number of seconds it takes for a fade-in effect to come to completion.
        Use the &fadein flag with the :led message to have a fade-in effect.

    FADEOUT_DURATION:
        Number of seconds it takes for a fade-out effect to come to completion.
        Fade-out effects happen automatically when a led expires. To disable
        this, supply your :led message with a !fadeout flag.
        Blinky leds (i.e., :led messages with the &blink flag) don't normally
        fade out. Explicitly specify the &fadeout flag along with the &blink
        flag to have &blink leds fade-out too.
"""
FPS=24
FRAME_LENGTH=round(1/FPS, 2)
KEEP_ALIVE = 10
MAX_KEEP_ALIVE = 30
KEEP_ALIVE_BLINK = 0.3
FADEIN_DURATION = 1
FADEOUT_DURATION = 1


""" Stack and plan settings
    =======================

    MAX_STACK_SIZE:
        The maximum number of frames to be stored on the stack.
        Each led has its own separate stack. These stacks are useful to
        remember the currently active frame for when a client briefly wants
        to display another frame on a led.

        For example, internally, blinky frames work by stacking the active
        frame, then displaying the blinky frame, and then reactivating the
        topmost frame of the stack again.

        When a frame is stacked, the current plan is stacked along with it,
        meaing that when a led reverts to a previously stacked frame, it will
        continue with the plan it had for that specific frame.

        Use the &stack flag in your :led message to to stack the active frame
        before displaying your  new frame.

        TODO: Implement using this setting.

    MAX_PLAN_SIZE:
        The maximum number of planned frames, albeit with the sidenote that
        blinky frames and fade-in and fade-out effects use the plan is a
        somewhat hackish manner. Blinkies and fade effects might cause a plan
        to grow beyond its maximum size without trouble, possibly blocking
        clients from  planning any more frames.

        Use the &plan flag to append your frame to the plan (as opposed to
        showing your frame immediately).

        TODO: Implement using this setting.

    ON_EXCEED_MAX_STACK_SIZE:
    ON_EXCEED_MAX_PLAN_SIZE:
        How to react when a `:led &stack ...` or `:led &plan ...` message would
        cause a stack or plan to grow beyond its maximum size.
        See ledutil.py for the defined actions.

        TODO: Implement using these settings.


"""
MAX_STACK_SIZE = 10
MAX_PLAN_SIZE = 1000
ON_EXCEED_MAX_STACK_SIZE = ledutil.ON_EXCEED_DENY
ON_EXCEED_MAX_PLAN_SIZE = ledutil.ON_EXCEED_DENY


""" Behaviour settings
    ==================

    GREENHACK:
        Apply the hack for green's intensity?
        Blatantly stolen from 
        https://github.com/pimoroni/blinkt/blob/master/projects/mqtt/mqtt.py

    SWAP:
        If False, `:led #0 ...` sets Blinkt pixel 0. If True, that same
        message sets Blinkt pixel 7. Useful if your Raspberry Pi is in an
        orientation where pixel 7 is logically the first led.
"""
GREENHACK = True
SWAP = True


""" Heartbeat settings
    ==================

    If desired, ledhost can show a 'heartbeat pulse' every now and then to
    indicate that it is up and running. The settings in this section pertain
    to that feature.

    HEARTBEAT_LED:
        On which Pimoroni Blinkt pixel will the heartbeat be shown?
        Set to None to disable the feature.
        Note that the value of the SWAP setting affects the meaning of this
        number: with SWAP==True, HEARTBEAT_LED==7 will actually be Blinkt
        pixel 0.

    HEARTBEAT_RGB:
        The RGB value of the heartbeat.

    HEARTBEAT_INTERVAL:
        The number of seconds between the start of one pulse to the next.

    HEARTBEAT_FADEIN:
    HEARTBEAT_FADEOUT:
        Set to 0 to disable heartbeat fade-in or fade-out effects.
        Set to 1 to enable fade effect on first half of the pulse.
        Set to 2 to enable fade effect on second half of the pulse.
        Set to 3 to enable fade effect on both halves of the pulse
"""

HEARTBEAT_LED = 7
HEARTBEAT_RGB = (64, 64, 64)
HEARTBEAT_INTERVAL = 15
HEARTBEAT_FADEIN = 3
HEARTBEAT_FADEOUT = 3

# TODO: Remove all that debug stuff -- it ain't working as envisioned.

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
