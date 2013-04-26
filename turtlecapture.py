import atexit
import os

canvas_callback = None


def exit_callback():
    import sys
    image_name = os.getenv('SAVEIMAGE')
    script_dir = os.path.dirname(sys.argv[0])
    ps_path = os.path.join(script_dir, '{0}.ps'.format(image_name))
    png_path = os.path.join(script_dir, '{0}.png'.format(image_name))

    # Create PS image
    canvas = canvas_callback()
    canvas.update()
    canvas.postscript(file=ps_path, colormode='color')

    # Convert to PNG
    if os.system('convert {0} {1}'.format(ps_path, png_path)) == 0:
        os.unlink(ps_path)
        print('Saved PNG image to {0}'.format(png_path))
    else:
        print('Saved PS image to {0}'.format(ps_path))


def replaced_function(function_name, display_once=False):
    def wrap(*args, **kwargs):
        if not display_once or not displayed[0]:
            print('NOTICE: called replaced function {0}'.format(function_name))
            displayed[0] = True
    displayed = [False]  # Use list in order to mutate
    return wrap


def register(canvas_cb, register_cb=None):
    global canvas_callback
    # Only modify when the environment variable is set
    if os.getenv('SAVEIMAGE'):
        canvas_callback = canvas_cb
        # Register exit callback
        atexit.register(exit_callback)
        if register_cb:
            register_cb()
