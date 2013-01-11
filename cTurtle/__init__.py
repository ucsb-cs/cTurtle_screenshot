import atexit
import os
from .cTurtle import *


def exit_callback():
    import sys
    from . import cTurtle as _cTurtle  # Needed to get the _canvas attr

    image_name = os.getenv('SAVEIMAGE')
    script_dir = os.path.dirname(sys.argv[0])
    ps_path = os.path.join(script_dir, '{0}.ps'.format(image_name))
    png_path = os.path.join(script_dir, '{0}.png'.format(image_name))

    # Create PS image
    _cTurtle._canvas.update()
    _cTurtle._canvas.postscript(file=ps_path, colormode='color')

    # Convert to PNG
    if os.system('convert {0} {1}'.format(ps_path, png_path)) == 0:
        os.unlink(ps_path)
        print('Saved PNG image to {0}'.format(png_path))
    else:
        print('Saved PS image to {0}'.format(ps_path))


def replaced_function(function_name, display_once=False):
    displayed = [False]  # Use list in order to mutate
    def wrap(*args, **kwargs):
        if not display_once or not displayed[0]:
            print('NOTICE: called replaced function {0}'.format(function_name))
            displayed[0] = True
    return wrap


# Only modify when the environment variable is set
if os.getenv('SAVEIMAGE'):
    # Register exit callback
    atexit.register(exit_callback)

    # Monkey patch to allow for scripting
    Turtle.exitOnClick = replaced_function('exitOnClick')
    TurtleScreen.onTimer = replaced_function('onTimer')
    TurtleScreenBase._delay = replaced_function('_delay', display_once=True)
    mainloop = replaced_function('mainloop')

# Cleanup namespace
del exit_callback
del replaced_function
