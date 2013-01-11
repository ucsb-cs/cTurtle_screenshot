The `cTurtle` python package contained within this directory provides a drop-in
replacement for the original cTurtle.py module with the addition of providing a
transparent ability to save PNG images of the final canvas state.

To use this package simply replace your existing cTurtle.py with the directory
cTurtl. You will also need to have the `convert` program provided by
imagemagick on your system's path in order for the PNG to be saved.

By default, the modified cTurtle package will behave exactly as
before. However, when the environment variable SAVEIMAGE is set, an PNG image
will be saved to the same location as whatever python program you run is
contained. The image name will be whatever value you set to the SAVEIMAGE
environment variable with `.png` appended.

For instance, if you want to save a snapshot as `example_output.png` of the
window resulting from the program `example.py`, you need only set the
environment variable SAVEIMAGE to `example_output`. The following is one method
to accomplish that task:

    SAVEIMAGE=example_output python example.py

Note that the image is saved to the same directory as the python script you are
running; it is not always the current directory.


### Running Headless

It's kind of annoying for the window to pop up for the brief period that it
takes to process the entire program. On a Linux machine, the window can be
avoided by using a virtual framebuffer. The xvfb program provides a convenient
way to create and use a virtual framebuffer to handle such output. Assuming
xvfb is installed the previous example can be run in a headless manor via:

    SAVEIMAGE=example_output xvfb-run python example.py


### Caveats

In order to automatically capture the end-of-program state, the mainloop and
exitOnClick functions have been disabled. Additionally, to minimize the amount
of time required to run the entire program, many functions that attempt to
delay the rendering time have been disabled. Finally the `onTimer` function has
been disabled. Any disabled function will produce a `NOTICE` message to the
terminal. Note that it is common to see notices about `_delay`.
