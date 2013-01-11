import atexit
import os
import sys
from original import cTurtle as _cTurtle  # Needed to get the _canvas attr
from original.cTurtle import *


def exit_callback():
    script_dir = os.path.dirname(sys.argv[0])
    ps_path = os.path.join(script_dir, 'output.ps')
    png_path = os.path.join(script_dir, 'output.png')

    # Fetch PS image
    _cTurtle._canvas.update()
    _cTurtle._canvas.postscript(file=ps_path, colormode='color')

    # Convert to PNG
    if os.system('convert {0} {1}'.format(ps_path, png_path)) == 0:
        os.unlink(ps_path)

    # Convert
    print('Saved image to {0}'.format(png_path))


def replaced_function(function_name, display_once=False):
    displayed = [False]  # Use list in order to mutate
    def wrap(*args, **kwargs):
        if not display_once or not displayed[0]:
            print('NOTICE: called replaced function {0}'.format(function_name))
            displayed[0] = True
    return wrap


# Register exit callback when we need to save the image
if os.getenv('SAVEIMAGE'):
    atexit.register(exit_callback)


# Monkey patch to allow for scripting
Turtle.exitOnClick = replaced_function('exitOnClick')
TurtleScreen.onTimer = replaced_function('onTimer')
TurtleScreenBase._delay = replaced_function('_delay', display_once=True)
mainloop = replaced_function('mainloop')
