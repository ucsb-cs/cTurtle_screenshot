The `cTurtle.py` module in combination with the `original` package contained
within this folder provide a drop-in replacement for cTurtle that can
automatically save images of the canvas state at exit.

To perform the "snapshot" functionality, the environment variable SAVEIMAGE
must be set. The following is one easy method to set the environment:

    SAVEIMAGE=1 python example.py

The `example.py` file contains the code from the demo to demonstrate
completeness.
