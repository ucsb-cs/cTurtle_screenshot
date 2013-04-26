from .cTurtle import *
from turtlecapture import register, replaced_function


def canvas_callback():
    from . import cTurtle as _cTurtle  # Needed to get the _
    return _cTurtle._canvas


def register_callback():
    global mainloop
    # Monkey patch to allow for scripting
    Turtle.exitOnClick = replaced_function('exitOnClick')
    TurtleScreen.onTimer = replaced_function('onTimer')
    TurtleScreenBase._delay = replaced_function('_delay', display_once=True)
    mainloop = replaced_function('mainloop')


register(canvas_callback, register_callback)


# Cleanup namespace
del canvas_callback
del register
del register_callback
del replaced_function
