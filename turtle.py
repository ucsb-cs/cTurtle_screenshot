import imp
from turtlecapture import register, replaced_function
# Load the real cTurtle

turtle = imp.load_source('turtle', '/usr/lib64/python3.3/turtle.py')


def register_callback():
    # Monkey patch to allow for scripting
    turtle.Screen.exitonclick = replaced_function('exitonclick')
    turtle.TurtleScreen.ontimer = replaced_function('ontimer')
    turtle.TurtleScreenBase._delay = replaced_function('_delay',
                                                       display_once=True)
    turtle.mainloop = replaced_function('mainloop')


def canvas_callback():
    return turtle.Screen()._canvas


register(canvas_callback, register_callback)


# Cleanup namespace
del canvas_callback
del register
del register_callback
del replaced_function
