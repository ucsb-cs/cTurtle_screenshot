# cTurtle.py is based on the following work:
# xturtle.py: a Tkinter based turtle graphics module for 
#
# Copyright (C) 2006  Gregor Lingl,  <glingl@aon.at>
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#
# ------------------------------
# Modifications to support World Coordinates added by
# Brad Miller <bmiller@luther.edu>
# Turtle Modifications are released under the same conditions as the base
#

"""
Turtle graphics is a popular way for introducing programming to
kids. It was part of the original Logo programming language developed
by Wally Feurzig and Seymour Papert in 1966.

Imagine a robotic turtle starting at (0, 0) in the x-y plane. Give it
the command turtle.forward(15), and it moves (on-screen!) 15 pixels in
the direction it is facing, drawing a line as it moves. Give it the
command turtle.left(25), and it rotates in-place 25 degrees clockwise.

By combining together these and similar commands, intricate shapes and
pictures can easily be drawn.

----- cTurtle.py

This module is an extended reimplementation of turtle.py from the
Python standard distribution. (See: http:\\www.python.org)

It tries to keep the merits of turtle.py and to be (nearly) 100%
compatible with it. This means in the first place to enable the
learning programmer to use all the commands, classes and methods
interactively when using the module from within IDLE run with
the -n switch.

Roughly it has the following features added:

- Better animation of the turtle movements, especially of turning the
  turtle. So the turtles can more easily be used as a visual feedback
  instrument by the (beginning) programmer.

- different turtle shapes, gif-images as turtle shapes, user defined
  and user controllable turtle shapes, among them compound
  (multicolored) shapes.

- fine control over turtle movement and screen updates via delay(),
  and enhanced tracer() and speed() methods.

- aliases for the most commonly used commands, like fd for forward etc.,
  following the early Logo traditions. This reduces the boring work of
  typing long sequences of commands, which often occur in a natural way
  when kids try to program fancy pictures on their first encounter with
  turtle graphcis.

- some simple commands/methods for creating event driven programs
  (mouse-, key-, timer-events). Especially useful for programming games.
  
- A scrollable Canvas class. The default scrollable Canvas can be
  extended interactively as needed while playing around with the turtle(s).

- commands for controlling background color or backgorund image.

- The implementation uses a 2-vector class named _Vec, derived from
  tuple. This class can also be imported and used by the programmer,
  which makes certain types of computations very natural and compact.

Behind the scenes there are some features included with possible
extensionsin in mind. These will be commented and documented elsewhere. -

The module comes with a set of examples of different characters and
complexity and a very simple q&d assembled demo viewer.
"""

# cTurtle.py
# Version: 0.91
# Date: 2006-06-26

# Author: Gregor Lingl,
#         Vienna, Austria
# email: glingl@aon.at


import tkinter as TK
import types
import math           ## for compatibility: from math import *   ???

from os.path import isfile
from copy import deepcopy

def __methodDict(cls, _dict):
    baseList = list(cls.__bases__)
    baseList.reverse()   
    for _super in baseList:
        __methodDict(_super, _dict)
    for key, value in cls.__dict__.items():
        if type(value) == types.FunctionType:
            _dict[key] = value

def __methods(cls):
    _dict = {}
    __methodDict(cls, _dict)
    return list(_dict.keys())

__stringBody = (
    'def %(method)s(self, *args, **kw): return ' +
    'self.%(attribute)s.%(method)s(*args, **kw)')
    
def __forwardmethods(fromClass, toClass, toPart, exclude = ()):
    _dict = {}
    __methodDict(toClass, _dict)

    for ex in list(_dict.keys()):
        if ex[:1] == '_' or ex[-1:] == '_':
            del _dict[ex]
    for ex in exclude:
        if ex in _dict:
            del _dict[ex]
    for ex in __methods(fromClass):
        if ex in _dict:
            del _dict[ex]

    for method, func in _dict.items():
        d = {'method': method, 'func': func}
        if type(toPart) == str:
            execString = __stringBody % {'method' : method, 'attribute' : toPart}
        exec(execString, d)
        # TODO how to update the fromClass.__dict__ in Python 3.0??
        #fromClass.__dict__[method] = d[method]
        setattr(fromClass,method,d[method])
    

class ScrolledCanvas(TK.Frame):
    """Modeled after the scrolled canvas class from Grayons's book
    Python and Tkinter Programming.
    Used as the default canvas, which pops up automatically when
    using turtle graphics functions or the Pen class.
    """
    def __init__(self, master, width=500, height=350,
                                          canvwidth=600, canvheight=500):
        TK.Frame.__init__(self, master, width=width, height=height)
        self._root = self.winfo_toplevel()
        self.width, self.height = width, height
        self.canvwidth, self.canvheight = canvwidth, canvheight
        self.bg = "white"
        self._canvas = TK.Canvas(master, width=width, height=height,
                                 bg=self.bg, relief=TK.SUNKEN, borderwidth=2)
        self.hscroll = TK.Scrollbar(master, command=self._canvas.xview,
                                    orient=TK.HORIZONTAL)
        self.vscroll = TK.Scrollbar(master, command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=self.hscroll.set,
                               yscrollcommand=self.vscroll.set)
        self.rowconfigure(0, weight=1, minsize=0)
        self.columnconfigure(0, weight=1, minsize=0)
        self._canvas.grid(padx=1, in_ = self, pady=1, row=0, 
                column=0, rowspan=1, columnspan=1, sticky='news')
        self.vscroll.grid(padx=1, in_ = self, pady=1, row=0,
                column=1, rowspan=1, columnspan=1, sticky='news')
        self.hscroll.grid(padx=1, in_ = self, pady=1, row=1,
                column=0, rowspan=1, columnspan=1, sticky='news')
        self.reset()
        self._root.bind('<Configure>', self.onResize)

    def reset(self, canvwidth=None, canvheight=None, bg = None):
        if canvwidth:
            self.canvwidth = canvwidth
        if canvheight:
            self.canvheight = canvheight
        if bg:
            self.bg = bg
        self._canvas.config(bg=bg,
                        scrollregion=(-self.canvwidth//2, -self.canvheight//2,
                                       self.canvwidth//2, self.canvheight//2))
        self._canvas.xview_moveto(0.5*(self.canvwidth - self.width + 30) /
                                                               self.canvwidth)
        self._canvas.yview_moveto(0.5*(self.canvheight- self.height + 30) /
                                                              self.canvheight)
        self.adjustScrolls()


    def adjustScrolls(self):
        """ Adjust Scrollbars according to window- and canvas-size.
        """
        cwidth = self._canvas.winfo_width()
        cheight = self._canvas.winfo_height()
        self._canvas.xview_moveto(0.5*(self.canvwidth-cwidth)/self.canvwidth)
        self._canvas.yview_moveto(0.5*(self.canvheight-cheight)/self.canvheight)
        if cwidth < self.canvwidth or cheight < self.canvheight:       
            self.hscroll.grid(padx=1, in_ = self, pady=1, row=1,
                              column=0, rowspan=1, columnspan=1, sticky='news')
            self.vscroll.grid(padx=1, in_ = self, pady=1, row=0,
                              column=1, rowspan=1, columnspan=1, sticky='news')
        else:
            self.hscroll.grid_forget()
            self.vscroll.grid_forget()
            
    def onResize(self, event):
        self.adjustScrolls()

    def bbox(self, *args):
        """ 'forward' method, which canvas itself has inherited...
        """
        return self._canvas.bbox(*args)

    def cget(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        return self._canvas.cget(*args, **kwargs)

    def config(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.config(*args, **kwargs)

    def bind(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.bind(*args, **kwargs)

    def unbind(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.unbind(*args, **kwargs)

    def focus_force(self):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.focus_force()

__forwardmethods(ScrolledCanvas, TK.Canvas, '_canvas')


class _Vec(tuple):
    """A 2 dimensional vector class, used as a helper class
    for implementing turtle graphics.
    May be useful for turtle graphics programs also.
    Derived from tuple, so a vector is a tuple!

    Provides (for a, b vectors, k number=:
       a+b vector addition
       a-b vector subtraction
       a*b inner product
       k*a and a*k multiplication with scalar
       |a| absolute value of a
       a.rotate(angle) rotation       
    """
    def __new__(cls, x, y):
        return tuple.__new__(cls, (x, y))
    def __add__(self, other):
        return _Vec(self[0]+other[0], self[1]+other[1])
    def __mul__(self, other):
        if isinstance(other, _Vec):
            return self[0]*other[0]+self[1]*other[1]
        return _Vec(self[0]*other, self[1]*other)
    def __rmul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return _Vec(self[0]*other, self[1]*other)
    def __sub__(self, other):
        return _Vec(self[0]-other[0], self[1]-other[1])
    def __neg__(self):
        return _Vec(-self[0], -self[1])
    def __abs__(self):
        return (self[0]**2 + self[1]**2)**0.5
    def rotate(self, angle):
        """rotate self counterclockwise by angle
        """
        perp = _Vec(-self[1], self[0])
        angle = angle * math.pi / 180.0
        c, s = math.cos(angle), math.sin(angle)
        return _Vec(self[0]*c+perp[0]*s, self[1]*c+perp[1]*s)
    def __getnewargs__(self):
        return (self[0], self[1])
    def __repr__(self):
        return "(%.2f,%.2f)" % self 


class TurtleScreenBase(object):
    """Provides the basic graphics functionality.
       Interface between Tkinter and cTurtle.py.
    
       To port cTurtle.py to some other graphics toolkit
       a corresponding TurtleScreenBase class has to be
       implemented.
    """
    # TODO Add patches to this class.
    
    @staticmethod
    def _blankimage():
        """returns a blank image object
        """
        img = TK.PhotoImage(width=1, height=1)
        img.blank()
        return img

    @staticmethod
    def _image(filename):
        """returns an image object containing the
        imagedata from a gif-file named filename.
        """
        return TK.PhotoImage(file=filename)

    def __init__(self, cv): 
        self.cv = cv
        if isinstance(cv, ScrolledCanvas):
            w = self.cv.canvwidth
            h = self.cv.canvheight
        else:  # expected: ordinary TK.Canvas
            w = int(self.cv.cget("width"))
            h = int(self.cv.cget("height"))
            self.cv.config(scrollregion = (-w//2, -h//2, w//2, h//2 ))
        self.canvwidth = w
        self.canvheight = h
        self.xscale = 1.0
        self.yscale = 1.0        

    def getXScale(self):
        return self.xscale

    def getYScale(self):
        return self.yscale
        
    def setXScale(self,sf):
        self.xscale = sf
    
    def setYScale(self,sf):
        self.yscale = sf
        
    def setWorldCoords(self,llx,lly,urx,ury):
        llx = float(llx)
        lly = float(lly)
        urx = float(urx)
        ury = float(ury)
        xspan = urx - llx
        yspan = ury - lly
        self.xscale = self.canvwidth / xspan
        self.yscale = self.canvheight / yspan
        srx1 = (llx - 0) * self.xscale
        sry1 = (0 - ury) * self.yscale
        srx2 = self.canvwidth + srx1
        sry2 = self.canvheight + sry1
        self.cv.config(scrollregion=(srx1,sry1,srx2,sry2))
    
    def _createpoly(self):
        """Creates an invisible polygon item on canvas self.cv) 
        """
        return self.cv.create_polygon((0, 0, 0, 0, 0, 0), fill="", outline="")

    def _drawpoly(self, polyitem, coordlist, fill=None,
                  outline=None, width=None, top=False, xform=True):
        """configures polygonitem polyitem according to provided
        arguments:
        coordlist is sequence of coordinates
        fill is filling color
        outline is outline color
        top is a boolean value, which specifies if polyitem
        will be put on top of the canvas' displaylist so it
        will not be covered by other items.
        """
        cl = []
        for x, y in coordlist:
            # could add world -- screen transforms here.
            # slight problem with drawing the turtle....
            # The translation of the origin to the center of the window is done using scrollregion
            # xview_moveto and yview_moveto functions on the canvas....
            if xform:
                x = x * self.xscale
                y = y * self.yscale
            cl.append(x)
            cl.append(-y)
        self.cv.coords(polyitem, *cl)
        if fill is not None:
            self.cv.itemconfigure(polyitem, fill=fill)
        if outline is not None:
            self.cv.itemconfigure(polyitem, outline=outline)
        if width is not None:
            self.cv.itemconfigure(polyitem, width=width)
        if top:
            self.cv.tag_raise(polyitem)
            
    def _createline(self):
        """Creates an invisible line item on canvas self.cv) 
        """
        return self.cv.create_line(0, 0, 0, 0, fill="", width=2,
                                   capstyle = TK.ROUND)

    def _drawline(self, lineitem, coordlist=None,
                  fill=None, width=None, top=False,xform=True):
        """configures lineitem according to provided arguments:
        coordlist is sequence of coordinates
        fill is drawing color
        width is width of drawn line.
        top is a boolean value, which specifies if polyitem
        will be put on top of the canvas' displaylist so it
        will not be covered by other items.
        """
        if coordlist is not None:
            cl = []
            for x, y in coordlist:
                # could add world --- screen transforms here
                if xform:
                    x = x * self.xscale
                    y = y * self.yscale
                cl.append(x)
                cl.append(-y)
            self.cv.coords(lineitem, *cl)
        if fill is not None:
            self.cv.itemconfigure(lineitem, fill=fill)
        if width is not None:
            self.cv.itemconfigure(lineitem, width=width)
        if top:
            self.cv.tag_raise(lineitem)

    def _delete(self, item):
        """deletes graphics item from canvas
        """
        self.cv.delete(item)

    def _update(self):
        """readraws graphics items on canvas
        """
        self.cv.update()

    def _delay(self, delay):
        """delay subsequent canvas actions for delay ms."""
        self.cv.after(delay)

    def _isColorString(self, color):
        """Checks if the string color is a legal
        Tkinter color string.
        """
        try:
            rgb = self.cv.winfo_rgb(color)
            ok = True
        except TK.TclError:
            ok = False
        return ok

    def _bgcolor(self, color=None):
        """Set canvas' backgroundcolor if color is not None,
        else return backgroundcolor."""
        if color is not None:
            self.cv._canvas.config(bg = color)
            self._update()
        else:
            return self.cv.cget("bg")
        
    def _write(self, pos, txt, align, font, pencolor):
        """Write txt at pos in canvas with specified font
        and color.
        Return text item and x-coord of right bottom corner
        of text's bounding box."""
        x, y = pos
        anchor = {"left":"sw", "center":"s", "right":"se" }
        xscale = self.getXScale()
        yscale = self.getYScale() 
        nx = x * xscale
        ny = y * yscale
        item = self.cv.create_text(nx-1, -ny, text = txt, anchor = anchor[align],
                                        fill = pencolor, font = font)
        x0, y0, x1, y1 = self.cv.bbox(item)
        self.cv.update()
        return item, x1-1

    def _onClick(self, fun, num=1): 
        """Bind fun to mouse-click event on canvas.
        fun must be a function with two arguments, the coordinates
        of the clicked point on the canvas.
        num, the number of the mouse-button defaults to 1
        """
        if fun is None:
            self.cv.unbind("<Button-%s>" % num)
        else:
            def eventfun(event):
                x, y = self.cv.canvasx(event.x)/self.xscale, -self.cv.canvasy(event.y)/self.yscale
                fun(x, y)
            self.cv.bind("<Button-%s>" % num, eventfun)
    
    def _onKey(self, fun, key):
        """Bind fun to key-release event of key.
        Canvas must have focus. See method listen
        """
        if fun is None:
            self.cv.unbind("<KeyRelease-%s>" % key, None)
        else:
            def eventfun(event):
                fun()
            self.cv.bind("<KeyRelease-%s>" % key, eventfun)
           
    def _listen(self):
        """Set focus on canvas (in order to collect key-events)
        """
        self.cv.focus_force()

    def _onTimer(self, fun, t):
        """Install a timer, which calls fun after t milliseconds.
        """
        if t == 0:
            self.cv.after_idle(fun)
        else:
            self.cv.after(t, fun)

    def _createimage(self, image):
        """Create and return image item on canvas.
        """
        return self.cv.create_image(0, 0, image=image)

    def _drawimage(self, item, xxx_todo_changeme, image):
        """Configure image item as to draw image object
        at position (x,y) on canvas)
        """
        (x, y) = xxx_todo_changeme
        self.cv.coords(item, (x, -y))
        self.cv.itemconfig(item, image=image)

    def _setbgpic(self, item, image):
        """Configure image item as to draw image object
        at center of canvas. Set item to the first item
        in the displaylist, so it will be drawn below
        any other item ."""
        self.cv.itemconfig(item, image=image)
        self.cv.tag_lower(item)
        
#### Rudiments of Error hanling with these classes
#### Urgently need to be amended.

_DEBUG = 0
_NONE = type(None)

def debug(level=1):
    global _DEBUG
    _DEBUG = level

class Terminator (Exception):
    """Will be raised in TurtleScreen.update,
    if _RUNNING becomes False. Thus stops execution of
    turtle graphics script. (Main purpose: use in
    in the Demo-Viewer cTurtle.Demo.py.
    """
    pass

class TG_Error(Exception):
    """Some TurtleGraphics Error
    """

###- THIS IS A PROMISE (under development) -###

def checkargs(*typelist):
    """check if arguments passed to caller correspond
    to typelist.
    """
    if _DEBUG == 0:
        return
###- yet to implement -###
    

class Shape(object):
    """Data structure modeling shapes.
    
    attribute _type is one of "polygon", "image", "compound"
    attribute _data is - depending on _type a poygon-tuple,
    an image or a list constructed using the addComponent method.
    """
    def __init__(self, type, data=None):
        self._type = type
        if type == "polygon":
            if isinstance(data, list):
                data = tuple(data)
        elif type == "image":
            if isinstance(data, str):
                if data.lower().endswith(".gif") and isfile(data):
                    data = TurtleScreen._image(data)
                # else data assumed to be Photoimage
        elif type == "compound":
            data = []
        else:
            raise TG_Error("There is no shape type %s" % type)
        self._data = data
        
    def addComponent(self, poly, fill, outline=None):
        """add component to a shape of type compound.
        ---
        Arguments: poly is a polygon, i. e. a tuple of number pairs.
        fill is the fillcolor of the component,
        outline is the outline color of the component.

        call (for a Shapeobject namend s):
        --   s.addcomponent(((0,0), (10,10), (-10,10)), "red", "blue")
        
        Example:
        >>> poly = ((0,0),(10,-5),(0,10),(-10,-5))
        >>> s = Shape("compound")
        >>> s.addComponent(poly, "red", "blue")
        ### .. add more components and then use addshape()
        """
        if self._type != "compound":
            raise TG_Error("Cannot add component to %s Shape" % self._type)
        if outline is None:
            outline = fill
        checkargs("polygon", "color", "color")
        self._data.append([poly, fill, outline])


class TurtleScreen(TurtleScreenBase):
    """Provides screen oriented methods like setbg etc.

    All those methods are also transferred to the RawPen
    class, so theys can be called as RawPen methods or
    - consequently - functions. 

    Only relies upon the methods of TurtleScreenBase and NOT
    upon components of the underlying graphics toolkit -
    which is Tkinter in this case.
    """
    _STANDARD_DELAY = 5
    _RUNNING = True

    def __init__(self, cv):   
        self._shapes = { # triangle
                   "arrow" : Shape("polygon", ((-10,0), (10,0), (0,10))),
                         # turtle
                  "turtle" : Shape("polygon", ((0,16), (-2,14), (-1,10), (-4,7),
                              (-7,9), (-9,8), (-6,5), (-7,1), (-5,-3), (-8,-6),
                              (-6,-8), (-4,-5), (0,-7), (4,-5), (6,-8), (8,-6),
                              (5,-3), (7,1), (6,5), (9,8), (7,9), (4,7), (1,10),
                              (2,14))),
                  "circle" : Shape("polygon", ((10,0), (9.51,3.09), (8.09,5.88),
                              (5.88,8.09), (3.09,9.51), (0,10), (-3.09,9.51),
                              (-5.88,8.09), (-8.09,5.88), (-9.51,3.09), (-10,0),
                              (-9.51,-3.09), (-8.09,-5.88), (-5.88,-8.09),
                              (-3.09,-9.51), (-0.00,-10.00), (3.09,-9.51),
                              (5.88,-8.09), (8.09,-5.88), (9.51,-3.09))) 
                   ,
                   "blank" : Shape("image", self._blankimage())
                  }
        
        self._bgpics = {"nopic" : ""}

        TurtleScreenBase.__init__(self, cv) 
        self._colormode = 1.0
        self._bgpic = self._createimage("")
        self._bgpicname = "nopic"
        self._tracing = 1
        self._delayvalue = 10
        self._updatecounter = 0
        self._turtles = []

    def addshape(self, name, shape=None):
        """Adds a turtle shape to TurtleScreen's shapelist.
        ---
        Arguments:
        (1) name is the name of a gif-file and shape is None.
            Installs the corresponding image shape.
            !! Image-shapes DO NOT rotate when turning the turtle,
            !! so they do not display the heading of the turtle!   
        (2) name is an arbitrary string and shape is a tuple
            of pairs of coordinates. Installs the corresponding
            polygon shape
        (3) name is an arbitrary string and shape is a
            (compound) Shape object. Installs the corresponding
            compound shape.
        To use a shape, you have to issue the command shape(shapename).

        call: addshape("turtle.gif")
        --or: addshape("tri", ((0,0), (10,10), (-10,10)))
        
        Example (for a TurtleScreen instance named screen):
        >>> screen.addshape("triangle", ((5,-3),(0,5),(-5,-3)))
        
        """
        checkargs("shape")
        if shape is None:
            # image
            if name.lower().endswith(".gif"):
                shape = Shape("image", self._image(name))
            else:
                raise
        elif isinstance(shape, tuple):
            shape = Shape("polygon", shape)
        ## else shape assumed to be Shape-instance
        self._shapes[name] = shape       

    def _color(self, args):
        """Return color string corresponding to args.

        Argument may be a string or a tuple of three
        numbers corresponding to actual colormode,
        i.e. in the range 0<=n<=colormode.

        If the argument doesn't represent a color,
        an error is raised.
        """
        if len(args) == 1:
            color = args[0]
            if color == "":
                return color
            if isinstance(color, str) and self._isColorString(color):
                return color
            else:
                args = color
        if isinstance(args, str):
            raise TG_Error("bad color sequence: %s" % repr(args)) 
        try:
            r, g, b = args
        except:
            raise TG_Error("bad color arguments: %s" % repr(args))
        if self._colormode == 1.0:
#            r, g, b = tuple(map(lambda x: round(255.0*x), (r, g, b)))
            r, g, b = [round(255.0*x) for x in (r, g, b)]
        if not ((0 <= r <= 255) and (0 <= g <= 255) and (0 <= b <= 255)):
            raise TG_Error("bad color sequence: %s" % repr(args))        
        return "#%02x%02x%02x" % (r, g, b)
    
    def colormode(self, cmode=None):
        """ Return the colormode or set it to 1.0 or 255.
        ---
        Argument: one of the values 1.0 or 255


        call:  colormode(255) # for example
        --or:  colormode()
        
        Example (for a Pen instance named turtle):
        >>> screen = turtle.getScreen()
        >>> screen.colormode()
        1.0
        >>> screen.colormode(255)
        >>> turtle.pencolor(240,160,80)
        
        """
        checkargs([1.0, 255, None])
        if cmode is None:
            return self._colormode
        if cmode in [1.0, 255]:
            self._colormode = cmode

    def resetscreen(self):
        """Reset all Turtles on the Screen to
        their initial state.

        Example (for a TurtleScreen instance named screen):
        >>> screen.reset()
        """
        for turtle in self._turtles:
            turtle.reset()

    def turtles(self):
        """Return the list of turtles on the screen.

        Example (for a TurtleScreen instance named screen):
        >>> screen.turtles()
        [<cTurtle.Pen object at 0x00E11FB0>]
        """
        return self._turtles
            
    def bgcolor(self, *args):
        """Set or return backgroundcolor of the TurtleScreen.

        Arguments (if given): a color string or three numbers
        in the range 0..colormode or a 3-tuple of such numbers.

        Example (for a TurtleScreen instance named screen):
        >>> screen.bgcolor("orange")
        >>> screen.bgcolor()
        'orange'
        >>> screen.bgcolor(0.5,0,0.5)
        >>> screen.bgcolor()
        '#800080'        
        """
        checkargs("color")
        if args:
            color = self._color(args)
        else:
            color = None
        return self._bgcolor(color)
        
    def tracer(self, n=None, delay=None):
        """tracer(True/False) turns turtle animation on/off.
        ---
        tracer accepts positive integers as first argument:
        tracer(n) has the effect, that only each n-th update
        is really performed. Can be used to accelerate
        the drawing of complex graphics.)
        Second arguments sets delay value (see RawPen.delay())
        Optional arguments: two nonnegative integers

        call: tracer(<nonnegative integer>)
        --or: tracer(<nonnegative integer>, <nonnegative integer>)

        Example (for a Pen instance named turtle):
        >>> turtle.tracer(8, 25)
        >>> l=2
        >>> for i in range(200):
                turtle.fd(l)
                turtle.rt(90)
                l+=2
        """
        checkargs("positive", "positive")
        if n is None:
            return self._tracing
        self._tracing = int(n)
        self._updatecounter = 0
        if delay is None:
            pass
            self._delayvalue = self._STANDARD_DELAY
        else:
            self._delayvalue = int(delay)
        self.update()
        
    def delay(self, delay=None):
        """ Return or set the drawing delay in milliseconds,
        which determines the speed of the turtle-animation.
        ---
        Argument: None or positive integer

        call: delay(<positive integer>)
        --or: delay()
        
        Example (for a TurtleScreen instance named screen):
        >>> screen.delay(15)
        >>> screen.delay()
        15
        """
        checkargs("positive")
        if delay is None:
            return self._delayvalue
        self._delayvalue = int(delay)

    def _incrementudc(self):
        if self._tracing > 0:
            self._updatecounter += 1
            self._updatecounter %= self._tracing

    def update(self, forced=False):
        if not TurtleScreen._RUNNING:
            raise Terminator
        if self._tracing == 0 and not forced:
            return
        if self._updatecounter == 0 or forced:
            self._update()
            self._delay(self._delayvalue)

    def resize(self, canvwidth=None, canvheight=None, bg=None):
        if not isinstance(self.cv, ScrolledCanvas):
            return self.canvwidth, self.canvheight
        if canvwidth is None or canvheight is None:
            return self.cv.canvwidth, self.cv.canvheight
        self.cv.reset(canvwidth, canvheight, bg)
        self.canvwidth, self.canvheight = canvwidth, canvheight
    
    def window_width(self):
        """ Returns the width of the turtle window.

        Example (for a TurtleScreen instance named screen):
        >>> screen.window_width()
        640
        """
        width = self.cv.winfo_width()
        if width <= 1:  # the window isn't managed by a geometry manager
            width = self.cv['width']
        return width

    def window_height(self):
        """ Return the height of the turtle window.

        Example (for a TurtleScreen instance named screen):
        >>> screen.window_height()
        480
        """
        height = self.cv.winfo_height()
        if height <= 1: # the window isn't managed by a geometry manager
            height = self.cv['height']
        return height

    def screen_width(self):
        """ Returns the width of the turtle screen, that is of
        the rectangular area, which can be viewed by using
        the scrollbars.

        Example (for a TurtleScreen instance named screen):
        >>> screen.screen_width()
        800
        """
        return self.canvwidth

    def screen_height(self):
        """ Return the height of the turtle screen, that is of
        the rectangular area, which can be viewed by using
        the scrollbars.

        Example (for a TurtleScreen instance named screen):
        >>> screen.screen_height()
        600
        """
        return self.canvheight

    def getshapes(self):
        """Return a list of names of all currently available
        shapes.
        
        Example (for a TurtleScreen instance named screen):
        >>> screen.getshapes()
        ['turtle', 'circle', 'arrow', 'blank']
        """
        return sorted(self._shapes.keys())

    def onClick(self, fun, btn=1):
        """Bind fun to mouse-click event on canvas.

        Arguments: fun must be a function with two arguments,
        the coordinates of the clicked point on the canvas.
        num, the number of the mouse-button defaults to 1

        Example (for a TurtleScreen instance named screen
        and a Pen instance named turtle):

        >>> screen.onClick(turtle.goto)

        ### Subsequently clicking into the TurtleScreen will
        ### make the turtle move to the clicked point.
        >>> screen.onClick(None)
        
        ### event-binding will be removed
        """
        self._onClick(fun, btn)

    def onKey(self, fun, key = None):
        """Bind fun to key-release event of key.
        Canvas must have focus. (See method listen.)

        Example (for a TurtleScreen instance named screen
        and a Pen instance named turtle):

        >>> def f():
                turtle.fd(50)
                turtle.lt(60)

                
        >>> screen.onKey(f, "Up")
        >>> screen.listen()
        
        ### Subsequently the turtle can be moved by
        ### repeatedly pressing the up-arrow key, 
        ### consequently drawing a hexagon
        """
        self._onKey(fun, key)
            
    def listen(self, xdummy=None, ydummy=None):
        """Set focus on TurtleScreen (in order to collect key-events)

        No arguments. Dummy argumetns are provided in order
        to be able to pass listen to the onClick method.

        Example (for a TurtleScreen instance named screen):
        >>> screen.listen()        
        """
        self._listen()

    def onTimer(self, fun, t=0):
        """Install a timer, which calls fun after t milliseconds.

        Arguments:
        fun is a function with no arguments.
        t is a number >= 0

        Example (for a TurtleScreen instance named screen
        and a Pen instance named turtle):

        >>> running = True
        >>> def f():
                if running:
                        turtle.fd(50)
                        turtle.lt(60)
                        screen.onTimer(f, 250)

        >>> f()   ### makes the turtle marching around
        >>> running = False        
        """
        self._onTimer(fun, t)

    def bgpic(self, picname=None):
        """Set background image to image contained in gif-file picname,
        or return name of current backgroundimage.
        If picname is "nopic", backgroundimage is deleted.

        Argument: string, which is the name of a gif imagefile
        or "nopic".

        Example (for a TurtleScreen instance named screen):
        >>> screen.bgpic()
        'nopic'
        >>> screen.bgpic("landscape.gif")
        >>> screen.bgpic()
        'landscape.gif'
        >>> screen.bgpic("nopic")
        """
        if picname is None:
            return self._bgpicname
        if picname not in self._bgpics:
            self._bgpics[picname] = self._image(picname)
        self._setbgpic(self._bgpic, self._bgpics[picname])
        self._bgpicname = picname
        
    def colorpatch(self,x,y):
        """docstring for colorpatch"""
        pass

    


class TNavigator(object):
    """Navigation part of the RawPen.
    Implements methods for turtle movement.
    """
    START_ORIENTATION = {
        "standard": _Vec(1.0, 0.0),
        "logo"    : _Vec(0.0, 1.0)  }
    DEFAULT_MODE = "standard"
    DEFAULT_ANGLEOFFSET = 0
    DEFAULT_ANGLEORIENT = 1

    def __init__(self):
        self._mode = self.DEFAULT_MODE
        self._angleOffset = self.DEFAULT_ANGLEOFFSET
        self._angleOrient = self.DEFAULT_ANGLEORIENT
        self.degrees()
        TNavigator.reset(self)
    
    def reset(self):
        """reset turtle to its initial values

        Will be overwritten by parent class
        """
        self._position = _Vec(0.0, 0.0)
        self._orient =  TNavigator.START_ORIENTATION[self._mode]

    def mode(self, mode=None):
        """Sets turtle-mode to 'standard' or 'logo' and resets
        turtle. Mode 'standard' is compatible with turtle.py.
        Mode 'logo' is compatible with most Logo-Turtle-Graphics'.
        If mode is not given, return the current mode.

        call: mode('standard')
        --or: mode('logo')
        --or: mode()
         
             Mode      Initial turtle heading     positive angles
         ------------|-------------------------|-------------------   
          'standard'    to the right (east)       counterclockwise
            'logo'        upward    (north)         clockwise

        Examples:
        >>> mode('logo')   # resets turtle heading to north
        >>> mode()
        'logo'
        """
        checkargs([None, "standard", "logo"])
        if mode == None:
            return self._mode
        if mode not in ["standard", "logo"]:
            return
        self._mode = mode
        if mode == "standard":
            self._angleOffset = 0
            self._angleOrient = 1
        else: # mode == "logo":
            self._angleOffset = self._fullcircle/4.
            self._angleOrient = -1
        self.reset()

    def _setDegreesPerAU(self, fullcircle):
        self._fullcircle = fullcircle
        self._degreesPerAU = 360/fullcircle
        if self._mode == "standard":
            self._angleOffset = 0
        else:
            self._angleOffset = fullcircle/4.
            
    def degrees(self, fullcircle=360.0):
        """ Set angle measurement units to degrees.
        Optional argument: fullcircle: number (set number
        of 'degrees' for a full circle).

        call: degrees()   # fullcircle defaults to 360
        -                 # learn more with help(degrees)
        
        Example (for a Pen instance named turtle):
        >>> turtle.left(90)
        >>> turtle.heading()
        90
        >>> turtle.degrees(400.0)  # angle measurement in gon
        >>> turtle.heading()
        100
        >>> turtle.degrees()
        >>> turtle.heading()
        90
        
        """
        checkargs((int, float))
        self._setDegreesPerAU(fullcircle)

    def radians(self):
        """ Set the angle measurement units to radians.
        No arguments.

        Example (for a Pen instance named turtle):
        >>> turtle.heading()   
        90
        >>> turtle.radians()
        >>> turtle.heading()
        1.5707963267948966
        """
        self._setDegreesPerAU(2*math.pi)

    def _go(self, distance):
        """Bewegt die Turtle um distance nach vorne"""
        ende = self._position + self._orient * distance    
        self._goto(ende)

    def _rotate(self, angle):
        """Dreht turtle um angle Grad nach links"""
        angle *= self._degreesPerAU
        self._orient = self._orient.rotate(angle)

    def _goto(self, end):
        """Bewegt die Turtle nach end""" 
        self._position = end
        
    def forward(self, distance):
        """forward | fd: Move the turtle forward by the specified distance,
        in the direction the turtle is headed.
        ---
        Argument: a number (integer or float)

        call: forward(<number>)
        --or: fd(<number>)

        Example (for a Pen instance named turtle):
        >>> turtle.position()
        (0.00, 0.00)
        >>> turtle.forward(25)
        >>> turtle.position()
        (25.00,0.00)
        >>> turtle.forward(-75)
        >>> turtle.position()
        (-50.00,0.00)
        """
        checkargs((int, float))
        self._go(distance)

    def back(self, distance):
        """back | backward | bk: Move the turtle backward by distance,
        opposite to the direction the turtle is headed
        The turtle's heading does not change.
        ---
        Argument: a number (integer or float)

        call: back(<number>)
        --or: bk(<number>)
        --or: backward(<number>)

        Example (for a Pen instance named turtle):
        >>> turtle.position()
        (0.00, 0.00)
        >>> turtle.backward(30)
        >>> turtle.position()
        (-30.00, 0.00)
        """
        checkargs((int, float))
        self._go(-distance)

    def right(self, angle):
        """right | rt: Turn turtle right angle units
        (units are by default degrees, but can be set
        via the degrees() and radians() functions.)
        ---
        Argument: a number (integer or float)

        call: right(<number>)
        --or: rt(<number>)

        Example (for a Pen instance named turtle):
        >>> turtle.heading()
        22.0
        >>> turtle.right(45)
        >>> turtle.heading()
        337.0
        """
        checkargs((int, float))
        self._rotate(-angle)
        
    def left(self, angle):
        """ left | lt: Turn turtle left angle units
        (units are by default degrees, but can be set
        via the degrees() and radians() functions.)
        ---
        Argument: a number (integer or float)

        call: left(<number>)
        --or: lt(<number>)

        Example (for a Pen instance named turtle):
        >>> turtle.heading()
        22.0
        >>> turtle.left(45)
        >>> turtle.heading()
        67.0
        """
        checkargs((int, float))
        self._rotate(angle)

    def pos(self):
        """ pos | position: Return the turtle's current location (x,y)
        (as a vector)

        No arguments.

        Example (for a Pen instance named turtle):
        >>> turtle.pos()
        (0.00, 240.00)
        """
        return self._position

    def xcor(self):
        """ Return the turtle's x coordinate

        No arguments.

        Example (for a Pen instance named turtle):
        >>> reset()
        >>> turtle.left(60)
        >>> turtle.forward(100)
        >>> print turtle.xcor()
        50.0
        """
        return self._position[0]
    
    def ycor(self):
        """ Return the turtle's y coordinate

        No arguments.

        Example (for a Pen instance named turtle):
        >>> reset()
        >>> turtle.left(60)
        >>> turtle.forward(100)
        >>> print turtle.ycor()
        86.6025403784
        """
        return self._position[1]
    

    def setpos(self, pos, y=None):
        """setpos | setposition | goto: Move turtle to an absolute position.
        If the pen is down, then a line will be drawn. The turtle's
        orientation does not change.
        ---
        Arguments: two numbers or a pair/vector of numbers

        call: goto(<number>,<number>)    # two coordinates
        --or: goto((<number>,<number>))  # a pair (tuple) of coordinates
        --or: goto(<2-vector>)           # e.g. as returned by pos()

        >>> tp = turtle.pos()
        >>> tp
        (0.00, 0.00)
        >>> turtle.setpos(60,30)
        >>> turtle.pos()
        (60.00,30.00)
        >>> turtle.setpos((20,80))
        >>> turtle.pos()
        (20.00,80.00)
        >>> turtle.setpos(tp)
        >>> turtle.pos()
        (0.00,0.00)
        """
        checkargs("position")
        if y is None:
            self._goto(_Vec(*pos))
        else:
            self._goto(_Vec(pos, y))

    def setx(self, x):
        """Set the turtle's first coordinate to x
        Second coordinate remains unchanged.
        ---
        Argument: a number (integer or float)

        call: setx(<number>)

        Example (for a Pen instance named turtle):
        >>> turtle.position()
        (0.00, 240.00)
        >>> turtle.setx(10)
        >>> turtle.position()
        (10.00, 240.00)
        """
        checkargs((int, float))
        self._goto(_Vec(x, self._position[1]))

    def sety(self, y):
        """ Sets the turtle's second coordinate to y
        First coordinate remains unchanged.
        ---
        Argument: a number (integer or float)

        call: sety(<number>)

        Example (for a Pen instance named turtle):
        >>> turtle.position()
        (0.00, 40.00)
        >>> turtle.sety(-10)
        >>> turtle.position()
        (0.00, -10.00)
        """
        checkargs((int, float))
        self._goto(_Vec(self._position[0], y))
        
    def distance(self, pos, y=None):
        """Return the distance from the turtle to pos,
        in turtle step units.
        ---
        Arguments: two numbers or a pair/vector of numbers
                   or a Pen instance

        call: distance(<number>,<number>)    # two coordinates
        --or: distance((<number>,<number>))  # a pair (tuple) of coordinates
        --or: distance(<2-vector>)           # e.g. as returned by pos()
        --or: distance(mypen)            # where mypen is another turtle

        Example (for a Pen instance named turtle):
        >>> turtle.pos()
        (0.00, 0.00)
        >>> turtle.distance(30,40)
        50.0
        >>> pen = Pen()
        >>> pen.forward(77)
        >>> turtle.distance(pen)
        77.0
        """
        checkargs(("position", RawPen))
        if y is not None:
            pos = _Vec(pos, y)
        if isinstance(pos, _Vec):
            pass
        elif isinstance(pos, tuple):
            pos = _Vec(*pos)
        elif isinstance(pos, TNavigator):
            pos = pos._position
        return abs(pos - self._position)
                 
    def towards(self, pos, y=None):
        """Return the angle, between the line from turtle-position to pos
        and the turtle's start orientation. (Depends on modes - "standard"
        or "logo")
        ---
        Arguments: two numbers or a pair/vector of numbers
                   or a Pen instance

        call: towards(<number>,<number>)    # two coordinates
        --or: towards((<number>,<number>))  # a pair (tuple) of coordinates
        --or: towards(<2-vector>)           # e.g. as returned by pos()
        --or: towards(mypen)            # where mypen is another turtle

        Example (for a Pen instance named turtle):
        >>> turtle.pos()
        (10.00, 10.00)
        >>> turtle.towards(0,0)
        225.0
        """
        checkargs(("position", RawPen))
        if y is not None:
            pos = _Vec(pos, y)
        if isinstance(pos, _Vec):
            pass
        elif isinstance(pos, tuple):
            pos = _Vec(*pos)
        elif isinstance(pos, TNavigator):
            pos = pos._position
        x, y = pos - self._position
        result = round(math.atan2(y, x)*180.0/math.pi, 10) % 360.0
        result /= self._degreesPerAU
        return (self._angleOffset + self._angleOrient*result) % self._fullcircle
    
    def heading(self):
        """ Return the turtle's current heading.

        No arguments.

        Example (for a Pen instance named turtle):
        >>> turtle.left(67)
        >>> turtle.heading()
        67.0
        """
        x, y = self._orient
        result = round(math.atan2(y, x)*180.0/math.pi, 10) % 360.0
        result /= self._degreesPerAU
        return (self._angleOffset + self._angleOrient*result) % self._fullcircle

    def setheading(self, to_angle):
        """ setheading | seth: Set the turtle facing the given angle.
        Here are some common directions in degrees:
        ---
        standard - mode:          logo-mode:                  
        -------------------|--------------------
           0 - east                0 - north
          90 - north              90 - east
         180 - west              180 - south
         270 - south             270 - west
        ---
        Argument: a number (integer or float)

        call: setheading(<number>)

        Example (for a Pen instance named turtle):
        >>> turtle.setheading(90)
        >>> turtle.heading()
        90
        """
        checkargs((int, float))
        angle = (to_angle - self.heading())*self._angleOrient
        full = self._fullcircle
        angle = (angle+full/2.)%full - full/2.
        self._rotate(angle)

    def circle(self, radius, extent = None, steps = None):
        """ Draw a circle with given radius.
        The center is radius units left of the turtle;
        extent - an angle - determines which part of the circle is drawn.
        If not given, the entire circle is drawn.
        -
        If extent is not a full circle, one endpoint of the arc is the
        current pen position. The arc is drawn in a counter clockwise
        direction if radius is positive, otherwise in a clockwise
        direction. In the process, the direction of the turtle is
        changed by the amount of the extent.
        -
        As the circle is approximated by an inscribed regular polygon,
        steps determines the number of steps to use. If not given,
        it will be calculated automatically.
        ---
        Arguments: number,
        Optional arguments: number, integer

        call: circle(<number>)  # full circle
        --or: circle(<number>, <number>) # arc
        --or: circle(<number>, <number>, <integer>)

        Example (for a Pen instance named turtle):
        >>> turtle.circle(50)
        >>> turtle.circle(120, 180)  # semicircle
        """
        checkargs((int, float), (int, float), int)
        speed = self.speed()
        if extent is None:
            extent = self._fullcircle 
        if steps is None:
            frac = abs(extent)/self._fullcircle 
            steps = 1+int(min(11+abs(radius)/6.0, 59.0)*frac)
        w = 1.0 * extent / steps
        w2 = 0.5 * w
        l = 2.0 * radius * math.sin(w2*math.pi/180.0*self._degreesPerAU) 
        if radius < 0:
            l, w, w2 = -l, -w, -w2
        tr = self.tracer()
        dl = self.delay()
        if speed == 0:
            self.tracer(0, 0)
        else:
            self.speed(0)
        self._rotate(w2)
        for i in range(steps):
            self.speed(speed)
            self._go(l)
            self.speed(0)
            self._rotate(w)
        self._rotate(-w2)
        if speed == 0:
            self.tracer(tr, dl)
        self.speed(speed)

## three dummy methods to be implemented by child class:
    
    def speed(self, s=0):
        """dummy method - to be overwritten by child class"""
    def tracer(self, a=None, b=None):
        """dummy method - to be overwritten by child class"""
    def delay(self, n=None):
        """dummy method - to be overwritten by child class"""
        
    
    fd = forward
    bk = back
    backward = back
    rt = right
    lt = left
    position = pos
    goto = setpos
    setposition = setpos
    seth = setheading


class TPen(object):
    """Drawing part of the RawPen.
    Implements drawing properties.
    """
    def __init__(self):
        self._resizemode = "auto" # or "user" or "noresize"
        TPen._reset(self)
        
    def _reset(self):
        self._pensize = 1
        self._shown = True
        self._pencolor = "black"
        self._fillcolor = ""
        self._drawing = True
        self._speed = 3
        self._stretchfactor = 1
        self._outlinewidth = 1
        
    def resizemode(self, rmode=None):
        """Set resizemode to one of the values: "auto", "user", "noresize".
        Different resizemodes have the following effects:
          - "auto" adapts the appearance of the turtle
                   corresponding to the value of pensize.
          - "user" adapts the appearance of the turtle according to the
                   values of stretchfactor and outlinewidth (outline),
                   which are set by turtlesize()
          - "noresize" no adaption of the turtle's appearance takes place.
        If no argument is given, return current resizemode.
        ---
        (Optional) Argument: one of the strings "auto", "user", "noresize"

        call: resizemode("user") # for example
        --or: resizemode()

        Examples:
        >>> resizemode("noresize")
        >>> resizemode()
        'noresize'
        """
        checkargs(["auto", "user", "noresize", None])
        if rmode is None:
            return self._resizemode
        rmode = rmode.lower()
        if rmode in ["auto", "user", "noresize"]:
            self._resizemode = rmode
        self._update()

    def pensize(self, width=None):
        """ pensize | width: Set (or return) the line thickness to width.
        If resizemode is set to "auto" and turtleshape is a
        polygon, that polygon is drawn with the same line thickness.
        IF argument 
        ---
        Argument: positive number

        call: pensize(<positive number>)

        Example (for a Pen instance named turtle):
        >>> turtle.pensize()
        1
        turtle.pensize(10)   # from here on lines of width 10 are drawn
        """
        checkargs((int, float, _NONE))
        if width is None:
            return self._pensize
        self._newLine()
        self._pensize = width
        self._update()
    
    def penup(self):
        """penup | pu | up: Pull the pen up -- no drawing when moving.

        Aliases: penup, pu, up
        No argument
        
        Example:
        >>> turtle.penup()
        """
        if not self._drawing:
            return
        self._drawing = False
        self._newLine(False)

    def pendown(self):
        """pendown | pd | down: Pull the pen down -- no drawing when moving.

        Aliases: pendown, pd, down
        No argument
        
        Example (for a Pen instance named turtle):
        >>> turtle.pendown()
        """
        if self._drawing:
            return
        self._newLine()
        self._drawing = True

    def speed(self, speed=None):
        """ Return the turtle's speed or set it to an integer value
        in the range 0 .. 10.
        If no argument is given: current speed is returned.
        If input is a number greater than 10 or smaller than 0.5,
        speed is set to 0.
        Speedstrings correspond to speedvalues in the following way:
            'fastest' :  0
            'fast'    :  10
            'normal'  :  6 
            'slow'    :  3
            'slowest' :  1
        speeds from 1 to 10 enforces increasingly faster animation of
        line drawing and turtle turning.
        !!!
        speed = 0 : *no* animation takes place. forward/back makes turtle jump
        and likewise left/right make the turtle turn instantly
        Optional Argument: number
        or one of the strings 'fastest', 'fast', 'normal', 'slow', 'slowest'
        (for compatibility with turtle.py)
        !!!
        Optional Argument: number in range 0..10, or 'speedstring' as described above.

        call: speed(1)  # slow
        --or: speed(10) # fastest
        --or: speed('fastest')
        --or: speed(0)

        Example (for a Pen instance named turtle):
        >>> turtle.speed(3)
        """
        checkargs((int, float, str, None))        
        speeds = {'fastest':0, 'fast':10, 'normal':6, 'slow':3, 'slowest':1 }
        if speed is None:
            return self._speed
        if speed in speeds:
            speed = speeds[speed]
        elif 0.5 < speed < 10.5:
            speed = int(round(speed))
        else:
            speed = 0
        self._speed = speed

    def color(self, *args):
        """Return or set the pencolor and fillcolor.
        If turtleshape is a polygon, outline and interior of that
        polygon is drawn with the newly set colors.
        - Arguments:
        Several input formats are allowed.
        They use 0, 1, 2, 3, or 6 arguments as follows:
          - color()
            return the current pencolor and the current fillcolor
            as a pair of color specification strings as are returned
            by pencolor and fillcolor.
          - color(s), color((r,g,b)), color(r,g,b)
            inputs as in pencolor, set both, fillcolor and pencolor,
            to the given value.
          - color(s1, s2),
            color((r1,g1,b1), (r2,g2,b2))
            color(r1, g1, b1, r2, g2, b2)
            equivalent to 
            pencolor(s1)
            fillcolor(s2) and analog, if the other input formats are used.


        call: color(<colorstring>)
        --or: color(<colorstring>, <colorstring>)
        --or with <number>s in range 0 .. colormode (i.e. 1.0 or 255)
        -     color((<number>, <number>, <number>))
        -     color((<number>, <number>, <number>),
                    (<number>, <number>, <number>))
        -     color((<number>, <number>, <number>,
                     <number>, <number>, <number>))
        -     color()        

        Example (for a Pen instance named turtle):        
        >>> turtle.color('red', 'green')
        >>> turtle.color()
        ('red', 'green')
        >>> colormode(255)
        >>> color(40, 80, 120, 160, 200, 240)
        >>> color()
        ('#285078', '#a0c8f0')
        """
        checkargs("colors")
        if args:
            l = len(args)
            if l == 2 or l == 6: 
                pcolor = args[:(l//2)] 
                fcolor = args[(l//2):] 
            else:
                pcolor = fcolor = args 
            self.pencolor(*pcolor)
            self.fillcolor(*fcolor)
        else:
            return self._pencolor, self._fillcolor

    def pencolor(self, *args):
        """ Return or set the pen color. If turtleshape is a
        polygon, the outline of that polygon is drawn with
        the newly set pencolor.
        -Arguments:
        Four input formats are allowed:
          - pencolor()
            return the current pencolor as color specification string,
            possibly in hex-number format (see example).
            May be used as input to another color/pencolor/fillcolor call.            
          - pencolor(s)
            s is a Tk specification string, such as "red" or "yellow"
          - pencolor((r, g, b))
            *a tuple* of r, g, and b, which represent, an RGB color,
            and each of r, g, and b are in the range 0..colormode,
            where colormode is either 1.0 or 255
          - pencolor(r, g, b)
            r, g, and b represent an RGB color, and each of r, g, and b
            are in the range 0..colormode

        call: pencolor(<colorstring>)
        --or with <number>s in range 0 .. colormode (i.e. 1.0 or 255)
        -     pencolor(<number>, <number>, <number>)
        -     pencolor((<number>, <number>, <number>))
        -     pencolor()        

        Example (for a Pen instance named turtle):
        
        >>> turtle.pencolor('brown')
        >>> tup = (0.2, 0.8, 0.55)
        >>> turtle.pencolor(tup)
        >>> turtle.pencolor()
        '#33cc8c'
        """
        checkargs("color")
        if args:
            color = self._color(args)
            self._newLine()
            self._pencolor = color
            self._update()
        else:
            return self._pencolor

    def fillcolor(self, *args):
        """ Return or set the fill color.
        If turtleshape is a polygon, that polygon is filled with
        the newly set fillcolor.
        Four input formats are allowed:
          - fillcolor()
            return the current pencolor as color specification string,
            possibly in hex-number format (see example).
            May be used as input to another color/pencolor/fillcolor call.            
          - fillcolor(s)
            s is a Tk specification string, such as "red" or "yellow"
          - fillcolor((r, g, b))
            *a tuple* of r, g, and b, which represent, an RGB color,
            and each of r, g, and b are in the range 0..colormode,
            where colormode is either 1.0 or 255
          - fillcolor(r, g, b)
            r, g, and b represent an RGB color, and each of r, g, and b
            are in the range 0..colormode

        call: fillcolor(<colorstring>)
        --or with <number>s in range 0 .. colormode (i.e. 1.0 or 255)
        -     fillcolor(<number>, <number>, <number>)
        -     fillcolor((<number>, <number>, <number>))
        -     fillcolor()        

        Example (for a Pen instance named turtle):        
        >>> turtle.fillcolor('violet')
        >>> tup = turtle.pencolor()
        >>> turtle.fillcolor(tup)
        >>> turtle.fillcolor(0, .5, 0)
        """
        checkargs("color")
        if args:
            color = self._color(args)
            self._fillcolor = color 
            self._update()
        else:
            return self._fillcolor

    def showturtle(self):
        """showturtle | st: Makes the turtle visible.

           No argument.

        Example (for a Pen instance named turtle):
        >>> turtle.hideturtle()
        >>> turtle.showturtle()
        """
        self._shown = True
        self._update()

    def hideturtle(self):
        """hideturtle | ht: Makes the turtle invisible.
        It's a good idea to do this while you're in the
        middle of a complicated drawing, because hiding
        the turtle speeds up the drawing observably.

        No argument.

        Example (for a Pen instance named turtle):
        >>> turtle.hideturtle()
        """
        self._shown = False
        self._update()

    def pen(self, pen=None, **pendict):
        """return (with no argument) or set the pen's attributes,
        in a 'pen-dictionary' with the following key/value pairs:
           "shown"      :   True/False
           "pendown"    :   True/False
           "pencolor"   :   color-string or color-tuple
           "fillcolor"  :   color-string or color-tuple
           "pensize"    :   positive number
           "speed"      :   number in range 0..10
           "resizemode" :   "auto" or "user" or "noresize"
           "stretchfactor": positive number
           "outline"    :   positive number

        This dicionary can be used as argument for a subsequent
        pen()-call to restore the former pen-state. Moreover one
        or more of these attributes can be provided as keyword-arguments.
        This can be used to set several pen attributes in one statement.

        Arguments:
            pen : a dictionary with some or all of the above
                  listed keys.
            **pendict : one or more keyword-arguments with the above
                  listed keys as keywords.
                  
        Examples (for a Pen instance named turtle):
        >>> turtle.pen(fillcolor="black", pencolor="red", pensize=10)
        >>> turtle.pen()
        {'pensize': 10, 'shown': True, 'resizemode': 'auto', 'outline': 1,
        'pencolor': 'red', 'pendown': True, 'fillcolor': 'black',
        'stretchfactor': 1, 'speed': 3}
        >>> penstate=turtle.pen()
        >>> turtle.color("yellow","")
        >>> turtle.penup()
        >>> turtle.pen()
        {'pensize': 10, 'shown': True, 'resizemode': 'auto', 'outline': 1,
        'pencolor': 'yellow', 'pendown': False, 'fillcolor': '',
        'stretchfactor': 1, 'speed': 3}
        >>> p.pen(penstate, fillcolor="green")
        >>> p.pen()
        {'pensize': 10, 'shown': True, 'resizemode': 'auto', 'outline': 1,
        'pencolor': 'red', 'pendown': True, 'fillcolor': 'green',
        'stretchfactor': 1, 'speed': 3}
        """
        if not (pen or pendict):
            return {"shown"         : self._shown,
                    "pendown"       : self._drawing,
                    "pencolor"      : self._pencolor,
                    "fillcolor"     : self._fillcolor,
                    "pensize"       : self._pensize,
                    "speed"         : self._speed,
                    "resizemode"    : self._resizemode,
                    "stretchfactor" : self._stretchfactor,
                    "outline"       : self._outlinewidth
                   }
        if isinstance(pen, dict):
            p = pen
        else:
            p = {}
        p.update(pendict)
        newLine = False
        if "pendown" in p:
            if self._drawing != p["pendown"]:
                newLine = True
        if "pencolor" in p:
            if self._pencolor != p["pencolor"]:
                newLine = True
        if "pensize" in p:
            if self._pensize != p["pensize"]:
                newLine = True
        if newLine:
            self._newLine()
        if "pendown" in p:
            self._drawing = p["pendown"]
        if "pencolor" in p:
            self._pencolor = p["pencolor"]
        if "pensize" in p:
            self._pensize = p["pensize"]
        if "fillcolor" in p:
            self._fillcolor = p["fillcolor"]
        if "speed" in p:
            self._speed = p["speed"]
        if "resizemode" in p:
            self._resizemode = p["resizemode"]
        if "stretchfactor" in p:
            self._stretchfactor = p["stretchfactor"]
        if "outline" in p:
            self._outlinewidth = p["outline"]
        if "shown" in p:
            self._shown = p["shown"]
        self._update()
        
    def turtlesize(self, stretchfactor=None, outline=None):
        """Return or set the pen's attributes stretchfactor and/or outline,
        if and only if resizemode is set to "user".
        The turtle will be displayed stretchfactor times as big as the
        original shape with an outline of width outline.

        Optinonal arguments:
           stretchfactor : positive number
           outline       : positive number

        Examples (for a Pen instance named turtle):
        >>> turtle.resizemode("user")
        >>> turtlesize(5, 12)
        >>> turtlesize(outline=8)
        """
        checkargs("positive", "positive")
        if stretchfactor == None and outline == None:
            return self._stretchfactor, self._outlinewidth
        if stretchfactor is not None:
            self._stretchfactor = stretchfactor
        if outline is not None:
            self._outlinewidth = outline
        self._update()

## three dummy methods to be implemented by child class:
        
    def _newLine(self, usePos = True):
        """dummy method - to be overwritten by child class"""
    def _update(self, count=True, forced=False):
        """dummy method - to be overwritten by child class"""
    def _color(self, args):
        """dummy method - to be overwritten by child class"""

    width = pensize
    up = penup
    pu = penup
    pd = pendown
    down = pendown
    st = showturtle
    ht = hideturtle


class _TurtleImage(object):
    """Helper class: Datatype to store Turtle attributes
    """
    def __init__(self, screenIndex, shapeIndex):
        self.screenIndex = screenIndex
        self._type = None
        self._setshape(shapeIndex)
        
    def _setshape(self, shapeIndex):
        screen = RawPen.screens[self.screenIndex]
        self.shapeIndex = shapeIndex
        if self._type in ["image", "polygon"]:
            screen._delete(self._item)
        elif self._type == "compound":
            for item in self._item:
                screen._delete(item)                
        self._type = screen._shapes[shapeIndex]._type
        if self._type == "polygon":
            self._item = screen._createpoly()
        elif self._type == "image":
            self._item = screen._createimage(screen._shapes["blank"]._data)
        elif self._type == "compound":
            self._item = [screen._createpoly() for item in
                                          screen._shapes[shapeIndex]._data]

                  
class RawPen(TPen, TNavigator):
    """Animation part of the RawPen.
    Puts RawPen upon a TurtleScreen and provides tools for
    it's animation.
    """
    canvases = []
    screens = []    
    DEFAULT_MODE = "standard"
        
    def __init__(self, canvas, shape = "arrow"): 
        if canvas not in RawPen.canvases:
            RawPen.canvases.append(canvas)
            RawPen.screens.append(TurtleScreen(canvas))
        self.screenIndex = RawPen.canvases.index(canvas)
        TNavigator.__init__(self)
        TPen.__init__(self)
        screen = self.screens[self.screenIndex]
        screen._turtles.append(self)
        self.drawingLineItem = screen._createline()
        self.turtle = _TurtleImage(self.screenIndex, shape)
        self._poly = None
        self._creatingPoly = False
        self._fillitem = self._fillpath = None
        self._hidden_from_screen = False
        self.currentLineItem = screen._createline()
        self.currentLine = [self._position]
        self.items = [self.currentLineItem]
        self._update()
   
    def reset(self):
        """Delete the pen's drawing from the screen,
        re-center the pen and set variables to the default values.

        Example (for a Pen instance named turtle):
        
        >>> turtle.position()
        (0.00,-22.00)
        >>> turtle.seth(100)
        >>> turtle.position()
        (0.00,-22.00)
        >>> turtle.heading()
        100.0
        >>> turtle.reset()
        >>> turtle.position()
        (0.00,0.00)
        >>> turtle.heading()
        0.0        
        """
        TNavigator.reset(self)
        TPen._reset(self)
        self._clear()             
        self._drawturtle()
        self._update()             

    def _clear(self, n=None):
        """Delete all of pen's drawings"""
        screen = self.screens[self.screenIndex]
        items = self.items
        self._fillitem = self._fillpath = None
        #self._filling = False
        if n == None:
            for item in items:
                screen._delete(item)
            self.currentLineItem = screen._createline()
            self.currentLine = []
            if self._drawing:
                self.currentLine.append(self._position)
            self.items = [self.currentLineItem]
        else:                                      
            if n > 0 and len(self.currentLine)<2:
                n = n+1
            delete, stay = items[:-n], items[-n:]
            if n > 0:
                delete, stay = stay, delete
            for item in delete:
                screen._delete(item)
            self.items = stay
            if self.currentLineItem not in self.items:
                self.currentLineItem = screen._createline()
                self.currentLine = []
                if self._drawing:
                    self.currentLine.append(self._position)
                self.items.append(self.currentLineItem)

    def clear(self, n=None):
        """Delete the pen's drawings from the screen.
        The pen does not move. Drawings of other pens
        are not affected.

        Examples (for a Pen instance named turtle):
        >>> turtle.clear()

        NB!   Optional argument n is experimental
        NB!   and will be documented or removed later.
        """
        self._clear(n)
        self._update()

    def _update(self, count=True, forced=False):
        """Perform a TurtleScreen update.
        """
        screen = self.screens[self.screenIndex]
        if count:
            screen._incrementudc()
        if forced or (screen._tracing != 0 and screen._updatecounter==0):
            # bnm rather than self._drawturtle() this seems to fix the problem of
            # turtles coming and going at odd times when tracer is set to values != 1
            for t in screen._turtles:
                t._drawturtle()
                if len(t.currentLine)>1:   
                    screen._drawline(t.currentLineItem, t.currentLine,
                                     t._pencolor, t._pensize)
        screen.update(forced)

    def update(self):
        """Perform a TurtleScreen update.
        Especially useful to control screen updates
        when tracer(False) is set.

        Example (for a Pen instance named turtle):
        >>> tracer(0)
        >>> for i in range(36):
                for j in range(5):
                        turtle.fd(100)
                        turtle.lt(72)
                turtle.update() # draws a pentagon at once
                turtle.lt(10)        
        """
        self._update(forced=True)

    def tracer(self, flag=None, delay=None):
        """tracer(True/False) turns turtle animation on/off.

        tracer accepts positive integers as first argument:
        tracer(n) has the effect, that only each n-th update
        is really performed. Can be used to accelerate
        the drawing of complex graphics.)
        Second arguments sets delay value (see RawPen.delay())

        Example (for a Pen instance named turtle):
        >>> turtle.tracer(8, 25)
        >>> l=2
        >>> for i in range(200):
                turtle.fd(l)
                turtle.rt(90)
                l+=2
        """
        # checkargs will be performed by screen.tracer()
        screen = self.screens[self.screenIndex]
        if flag is None:
            return screen._tracing
        if screen._tracing != 1:
            for t in screen._turtles:
                if len(t.currentLine)>1:   
                    screen._drawline(t.currentLineItem, t.currentLine,
                                     t._pencolor, t._pensize)
        screen.tracer(flag, delay)
        self._update(forced=True)

    def _color(self, args): 
        return self.getScreen()._color(args) 
    
    def clone(self):
        """Create and return an clone of the pen, with same
        position, heading and pen properties.

        Example (for a Pen instance named turtle):
        turtle = Pen()
        tortoise = turtle.clone()
        """
        screen = self.getScreen()
        self._newLine(self._drawing)
        q = deepcopy(self)
        screen._turtles.append(q)
        ttype = screen._shapes[self.turtle.shapeIndex]._type
        if ttype == "polygon":
            q.turtle._item = screen._createpoly()
        elif ttype == "image":
            q.turtle._item = screen._createimage(screen._shapes["blank"]._data)
        elif ttype == "compound":
            q.turtle._item = [screen._createpoly() for item in
                              screen._shapes[self.turtle.shapeIndex]._data]
        q.currentLineItem = screen._createline()
        q._update()
        return q

    def shape(self, name=None):
        """Set pen shape to shape with given name.
        Shape must exist in the TurtleScreen's shape dictionary.
        Initially there are three polygon shapes: 'arrow',
        'turtle', 'circle'.
        To learn about different types of shapes see method addshape!

        Without argument return name of current shape.

        Example (for a Pen instance named turtle):
        >>> turtle.shape()
        'arrow'
        >>> turtle.shape("turtle")
        >>> shape()
        'turtle'
        """       
        if name is None:
            return self.turtle.shapeIndex
        if not name in self.getshapes():
            raise TG_Error("There is no shape named %s" % name)
        self.turtle._setshape(name)
        self._update()

    def _polytrafo(self, poly):
        """Computes transformed polygon shapes from a shape
        according to current position and heading.
        """
        xscale = self.screens[self.screenIndex].getXScale()
        yscale = self.screens[self.screenIndex].getYScale()
        p0, p1 = self._position[0]*xscale, self._position[1]*yscale
        e0, e1 = self._orient
        return [(p0+e1*x+e0*y, p1-e0*x+e1*y) for (x, y) in poly]

    def _drawturtle(self):
        screen = self.screens[self.screenIndex]
        shape = screen._shapes[self.turtle.shapeIndex]
        ttype = shape._type
        titem = self.turtle._item
        if self._shown and screen._updatecounter == 0 and screen._tracing > 0:
            self._hidden_from_screen = False
            tshape = shape._data
            if ttype == "polygon":
                if self._resizemode == "noresize":
                    w = 1
                    shape = tshape
                else:
                    if self._resizemode == "auto":
                        l = max(1, self._pensize/5.0)
                        w = self._pensize
                    elif self._resizemode == "user":
                        l = self._stretchfactor
                        w = self._outlinewidth
                    shape = [(l*x, l*y) for (x, y) in tshape]
                shape = self._polytrafo(shape)
                fc, oc = self._fillcolor, self._pencolor
                screen._drawpoly(titem, shape, fill=fc, outline=oc,
                                                      width=w, top=True,xform=False)
            elif ttype == "image":
                xscale = self.screens[self.screenIndex].getXScale()
                yscale = self.screens[self.screenIndex].getYScale()                
                np = (self._position[0]*xscale, self._position[1]*yscale)
                screen._drawimage(titem, np, tshape)
            elif ttype == "compound":
                l = self._stretchfactor
                w = self._outlinewidth
                for item, (poly, fc, oc) in zip(titem, tshape):
                    poly = [(l*x, l*y) for (x, y) in poly]
                    poly = self._polytrafo(poly)
                    screen._drawpoly(item, poly, fill=fc, outline=oc,
                                                      width=w, top=True,xform=False)
        else:
            if self._hidden_from_screen:
                return
            if ttype == "polygon":
                screen._drawpoly(titem, ((0, 0), (0, 0), (0, 0)), "", "")
            elif ttype == "image":
                screen._drawimage(titem, self._position,
                                          screen._shapes["blank"]._data)
            elif ttype == "compound":
                for item in titem:
                    screen._drawpoly(item, ((0, 0), (0, 0), (0, 0)), "", "")
            self._hidden_from_screen = True
                
    def _goto(self, end):
        """Move the pen to the point end, thereby drawing a line
        if pen is down. All other methodes for turtle movement depend
        on this one.
        """
        screen = self.screens[self.screenIndex]
        start = self._position
        if self._speed and screen._tracing == 1:
            diff = end-start
            nhops = 1+int(abs(diff)/(3*(1.1**self._speed)*self._speed))
            delta = diff * (1.0/nhops)
            for n in range(1, nhops):
                if n == 1:
                    top = True
                else:
                    top = False
                self._position = start + delta * n
                if self._drawing:
                    screen._drawline(self.drawingLineItem,
                                     (start, self._position),
                                     self._pencolor, self._pensize, top)
                self._update()
            if self._drawing:
                screen._drawline(self.drawingLineItem, ((0, 0), (0, 0)),
                                               fill="", width=self._pensize)
        # Turtle now at end, 
        if self._drawing: # now update currentLine
            self.currentLine.append(end)
        if isinstance(self._fillpath, list):
            self._fillpath.append(end)
        self._position = end
        if self._creatingPoly:
            xscale = self.screens[self.screenIndex].getXScale()
            yscale = self.screens[self.screenIndex].getYScale()
            end = (end[0]*xscale,end[1]*yscale)
            self._poly.append(end)
        if len(self.currentLine) > 42: # answer to the ultimate question
                                       # of life, the universe and everything
            self._newLine()
        self._update(count=True)

    def _rotate(self, angle):
        """Turns pen clockwise by angle.
        """
        screen = self.screens[self.screenIndex]
        angle *= self._degreesPerAU
        neworient = self._orient.rotate(angle)
        tracing = screen._tracing
        if tracing == 1 and self._speed > 0:
            anglevel = 3.0 * self._speed
            steps = 1 + int(abs(angle)/anglevel) 
            delta = 1.0*angle/steps
            for i in range(steps):
                self._orient = self._orient.rotate(delta)
                self._update()
        self._orient = neworient
        self._update()

    def _newLine(self, usePos=True):
        """Closes current line item and starts a new one.
           Remark: if current line becomes to long, animation
           performance (via _drawline) slows down considerably.
        """
        screen = self.screens[self.screenIndex]
        if len(self.currentLine) > 1:
            screen._drawline(self.currentLineItem, self.currentLine,
                                      self._pencolor, self._pensize)
            self.currentLineItem = screen._createline()
            self.items.append(self.currentLineItem)
        else:
            screen._drawline(self.currentLineItem, top=True)
        self.currentLine = []
        if usePos:
            self.currentLine = [self._position]
        
    def fill(self, flag):
        """ Call fill(True) before drawing the shape you want to fill,
        and  fill(False) when done.

        Argument: True/False (or 1/0 respectively)

        Example (for a Pen instance named turtle):
        >>> turtle.fill(True)
        >>> turtle.forward(100)
        >>> turtle.left(90)
        >>> turtle.forward(100)
        >>> turtle.left(90)
        >>> turtle.forward(100)
        >>> turtle.left(90)
        >>> turtle.forward(100)
        >>> turtle.fill(False)
        """
        checkargs("boolean")
        screen = self.screens[self.screenIndex]
        if isinstance(self._fillpath, list):
            if len(self._fillpath) > 2:
                screen._drawpoly(self._fillitem, self._fillpath,
                                                   fill=self._fillcolor) 
        if flag:
            self._fillitem = screen._createpoly()
            self.items.append(self._fillitem)
            self._fillpath = [self._position]
            self._newLine()
        else:
            self._fillitem = self._fillpath = None
        self._update(count=True)

    def begin_fill(self):
        """Called just before drawing a shape to be filled.

        No argument.
        
        Example (for a Pen instance named turtle):
        >>> turtle.begin_fill()
        >>> turtle.forward(100)
        >>> turtle.left(90)
        >>> turtle.forward(100)
        >>> turtle.left(90)
        >>> turtle.forward(100)
        >>> turtle.left(90)
        >>> turtle.forward(100)
        >>> turtle.end_fill()
        """
        self.fill(True)

    def end_fill(self):
        """Fill the shape drawn after the call begin_fill().

        No argument.
        
        Example (for a Pen instance named turtle):
        >>> turtle.begin_fill()
        >>> turtle.forward(100)
        >>> turtle.left(90)
        >>> turtle.forward(100)
        >>> turtle.left(90)
        >>> turtle.forward(100)
        >>> turtle.left(90)
        >>> turtle.forward(100)
        >>> turtle.end_fill()
        """
        self.fill(False)
    
    def dot(self, size=None, *color):
        """Draw a dot with diameter size, using pencolor.
        If size is not given, pensize()+4 is used.

        Argument: size is number >= 1 (if given)
                  color is colorstring or numeric color tuple

        Example (for a Pen instance named turtle):
        >>> turtle.dot()
        >>> turtle.fd(50); turtle.dot(20, "blue"); turtle.fd(50)
        """
        checkargs("positive", "color")
        pen = self.pen()
        self.ht()
        self.pendown()
        if size:
            self.pensize(size)
        else:
            self.pensize(self._pensize+4)
        if color:
            self.pencolor(*color)
        self.forward(0)
        self.pen(pen)

    def _write(self, txt, align, font):
        screen = self.screens[self.screenIndex]
        item, end = screen._write(self._position, txt, align, font,
                                                         self._pencolor)
        self.items.append(item)
        return end

    def write(self, arg, move=False, align="left",
              font=("Arial", 8, "normal")):
        """ Write text at the current pen position according to align
        ("left", "center" or right") and with the given font.
        
        If move is true, the pen is moved to the bottom-right corner
        of the text. By default, move is False.

        Example (for a Pen instance named turtle):
        >>> turtle.write('The race is on!')
        >>> turtle.write('Home = (0, 0)', True, align="center")
        """
        checkargs( True, "boolean", ["right", "left", "center"], "font")
        end = self._write(str(arg), align.lower(), font)
        if move:
            x, y = self.pos()
            self.setpos(end, y)

    def polystart(self):
        """Start recording the vertices of a polygon.
        Current turtle position is first point of polygon.

        Example (for a Pen instance named turtle):
        >>> turtle.polystart()
        """
        self._poly = [self._position]
        self._creatingPoly = True

    def polyend(self):
        """Stop recording the vertices of a polygon.
        Current turtle position is first last point
        of polygon. This will be connected with the
        first point.

        Example (for a Pen instance named turtle):
        >>> turtle.polyend()
        """
        self._creatingPoly = False

    def getpoly(self):
        """Return the lastly recorded polygon.

        Example (for a Pen instance named turtle):
        >>> p = turtle.getpoly()
        >>> turtle.addshape("myFavouriteShape", p)
        """
        ## check if there is any poly?
        return tuple(self._poly)

    def getCanvas(self):
        """Return the Canvas, the turtle is drawing
        on. Just for those who like it tu tinker around
        with (Scrolled or not) Canvas objects'

        Example (for a Pen instance named turtle):
        >>> cv = turtle.getCanvas()
        >>> cv
        <cTurtle.ScrolledCanvas instance at 0x010742D8>
        """
        return self.canvases[self.screenIndex]
    
    def getScreen(self):
        """Return the TurtleScreen object, the turtle is
        drawing  on. Some of the RawPen methods can also
        be called as TurtleScreen methods.

        Example (for a Pen instance named turtle):
        >>> ts = turtle.getScreen()
        >>> ts
        <cTurtle.TurtleScreen object at 0x0106B770>
        """
        return self.screens[self.screenIndex]

    def getPen(self):
        """Return the Penobject itself.
        Only reasonable use: as a function to return
        the 'anonymous turtle':
        
        Example:
        >>> turtle = getPen()
        >>> turtle.fd(50)
        >>> turtle
        <cTurtle.Pen object at 0x0187D810>
        >>> turtles()
        [<cTurtle.Pen object at 0x0187D810>]
        """
        return self

    ################################################################
    ### screen oriented methods recurring to methods of TurtleScreen
    ################################################################

    def addshape(self, name, shape=None):
        """Adds a turtle shape to TurtleScreen's shape dictionary.

        Arguments:
        (1) name is the name of a gif-file and shape is None.
            Installs the corresponding image shape.
        (2) name is an arbitrary string and shape is a tuple
            of pairs of coordinates. Installs the corresponding
            polygon shape
        (3) name is an arbitrary string and shape is a
            (compound) Shape object. Installs the corresponding
            compound shape.

        To use a shape, you have to issue the command shape(shapename).

        

        Examples (for a Pen instance named turtle):
        >>> turtle.addshape("triangle", ((5,-3),(0,5),(-5,-3)))
        """
        self.getScreen().addshape(name, shape)
        
    def bgcolor(self, *args):
        """Set or return backgroundcolor of the TurtleScreen.

        Arguments (if given): a color string or three numbers
        in the range 0..colormode or a 3-tuple of such numbers.

        Examples (for a Pen instance named turtle):
        >>> turtle.bgcolor("orange")
        >>> turtle.bgcolor()
        'orange'
        >>> turtle.bgcolor(0.5,0,0.5)
        >>> turtle.bgcolor()
        '#800080'        
        """
        return self.getScreen().bgcolor(*args)
        
    def bgpic(self, picname=None):
        """Set background image to image contained in gif-file picname,
        or return name of current backgroundimage.
        If picname is "nopic", backgroundimage is deleted.

        Argument: string, which is the name of a gif imagefile
        or "nopic".

        Examples (for a Pen instance named turtle):
        >>> turtle.bgpic()
        'nopic'
        >>> turtle.bgpic("landscape.gif")
        >>> turtle.bgpic()
        'landscape.gif'
        >>> turtle.bgpic("nopic")
        """
        return self.getScreen().bgpic(picname)
        
    def colormode(self, cmode=None):
        """ Return the colormode or set it to 1.0 or 255.
        ---
        Argument: None or one of the values 1.0 or 255


        call:  colormode(255) # for example
        --or:  colormode()
        

        Example (for a Pen instance named turtle):
        >>> turtle.colormode(255)
        >>> turtle.pencolor(240,160,80)
        """
        return self.getScreen().colormode(cmode)
    
    def delay(self, delay=None):
        """ Return or set the drawing delay in milliseconds.
        Screen oriented method, i.e. affects all Pens on the Screen.

        Argument: None or number >= 0.
        
        Example (for a Pen instance named turtle):
        >>> turtle.delay(15)
        >>> turtle.delay()
        15
        """
        return self.getScreen().delay(delay)
        
    def getshapes(self):
        """Return a list of names of all currently available
        shapes.
        
        Example (for a Pen instance named turtle):
        >>> turtle.getshapes()
        ['arrow', 'blank', 'circle', 'turtle']
        """
        return self.getScreen().getshapes()

    def clearscreen(self):
        """resetscreen | clearscreen: Reset all Pens on the
        Screen to their initial state.

        Example (for a Pen instance named turtle):
        >>> turtle.resetscreen()
        """
        self.getScreen().resetscreen()

    def turtles(self):
        """Return the list of turtles on the screen.

        Example (for a Pen instance named turtle):
        >>> turtle.turtles()
        [<cTurtle.Pen object at 0x00E11FB0>]
        """
        return self.getScreen().turtles()

    def screensize(self, canvwidth=None, canvheight=None, bg=None):
        """Resize the canvas, the turtles are drawing on. Does
        not alter the drawing window. To observe hidden parts of
        the canvas use the scrollbars. (Can make visible parts
        of a drawing, which were outside the canvas before!)

        Arguments: two positive integers

        Example (for a Pen instance named turtle):
        >>> turtle.screensize(2000,1500)
            ### e. g. to search for an erroneously escaped turtle ;-)
        """
        return self.getScreen().resize(canvwidth, canvheight, bg)

    resetscreen = clearscreen
    resize = screensize # for historical reasons, say: 'deprecated'
                        # so not documented
            
    #####   event binding methods   #####

    def onClick(self, fun, btn=1):
        """Bind fun to mouse-click event on canvas.

        Arguments: fun must be a function with two arguments,
        the coordinates of the clicked point on the canvas.
        num, the number of the mouse-button defaults to 1

        Example (for a Pen instance named turtle):

        >>> turtle.onClick(turtle.goto)

        ### Subsequently clicking into the TurtleScreen will
        ### make the turtle move to the clicked point.
        >>> turtle.onClick(None)
        
        ### event-binding will be removed
        """
        self.getScreen().onClick(fun, btn)

    def onKey(self, fun, key = None):
        """Bind fun to key-release event of key.
        Canvas must have focus. (See method listen.)

        Example (for a Pen instance named turtle):

        >>> def f():
                turtle.fd(50)
                turtle.lt(60)

                
        >>> turtle.onKey(f, "Up")
        >>> turtle.listen()
        
        ### Subsequently the turtle can be moved by
        ### repeatedly pressing the up-arrow key, 
        ### consequently drawing a hexagon
        """
        self.getScreen().onKey(fun, key)
            
    def listen(self, xdummy=None, ydummy=None):
        """Set focus on TurtleScreen (in order to collect key-events)

        No arguments.
        (Dummy arguments are provided, so listen can be passed
        as function argument to the onClick method.)

        Example (for a Pen instance named turtle):
        >>> turtle.listen()        
        """
        self.getScreen().listen()

    def onTimer(self, fun, t=0):
        """Install a timer, which calls fun after t milliseconds.

        Arguments:
        fun is a function with no arguments.
        t is a number >= 0

        Example (for a Pen instance named turtle):
        
        >>> running = True
        >>> def f():
                if running:
                        turtle.fd(50)
                        turtle.lt(60)
                        turtle.onTimer(f, 250)

        >>> f()   ### makes the turtle marching around
        >>> running = False        
        """
        self.getScreen().onTimer(fun, t)

    def window_width(self):
        """ Returns the width of the turtle window.

        Example (for a Pen instance named turtle):
        >>> turtle.window_width()
        640
        """
        return self.getScreen().window_width()

    def window_height(self):
        """ Return the height of the turtle window.

        Example (for a Pen instance named turtle):
        >>> turtle.window_height()
        480
        """
        return self.getScreen().window_height()

        
    def screen_width(self):
        """ Returns the width of the turtle screen.

        Example (for a Pen instance named turtle):
        >>> turtle.screen_width()
        800
        """
        return self.getScreen().screen_width()

    def screen_height(self):
        """ Return the height of the turtle screen.

        Example (for a Pen instance named turtle):
        >>> turtle.screen_height()
        600
        """
        return self.getScreen().screen_height()

###  Pen - Klasse  ########################

_root = None
_canvas = None
_pen = None
_title = "Extended Turtle Graphics"

# DEFAULT WINDOW CONFIGURATION

_WIDTH = 800
_HEIGHT = 600
_CANVWIDTH = 800
_CANVHEIGHT = 600
_LEFTRIGHT = -20
_TOPBOTTOM = -50

class Pen(RawPen):

    def __init__(self, turtleshape="arrow"):  
        global _root, _canvas
        if _root is None:
            _root = TK.Tk()
            _root.title(_title)
            ## Window geometry still has to be adapted to turtle.py
            ## _root.geometry("640x480-20-40")
            ## _root.maxsize(1240, 920)
            _root.wm_protocol("WM_DELETE_WINDOW", self._destroy)
        if _canvas is None:
            _canvas = ScrolledCanvas(_root, width=_WIDTH, height=_HEIGHT,
                                            canvwidth = _CANVWIDTH,
                                            canvheight = _CANVHEIGHT)
            self.winsize(_WIDTH, _HEIGHT, _LEFTRIGHT, _TOPBOTTOM)
            _canvas.pack(expand=1, fill="both")
        RawPen.__init__(self, _canvas, shape=turtleshape)


    def winsize(self, w, h, lr=_LEFTRIGHT, tb=_TOPBOTTOM):
        """Reset the geometry of the turtle graphics window.
        ---
        Arguments: w and h are new width and height of the window,
        lr ('left/right') and tb ('top/bottom') are coordinates
        of the edges of the graphics window on the monitor-screen.
        + is used for left/upper edge,
        - is used for right/bottom edge.

        Example (for a Pen instance named turtle):
        >>> turtle.winsize(800, 600, -10, 10)
            ### Resize the window to 800x600 with position
            ### 10 pixels from the left screen-edge and
            ### 10 pixels from the upper screen-edge.
        """
        _root.geometry("%dx%d%+d%+d"%(w, h, lr, tb))

    def setup(self, width=0.5, height=0.75, startx=None, starty=None):
        """ Set the size and position of the main window.
        Arguments:
        width: as integer a size in pixels, as float a fraction of the screen.
          Default is 50% of screen.
        height: as integer the height in pixels, as float a fraction of the
          screen. Default is 75% of screen.
        startx: if positive, starting position in pixels from the left
          edge of the screen, if negative from the right edge
          Default, startx=None is to center window horizontally.
        starty: if positive, starting position in pixels from the top
          edge of the screen, if negative from the bottom edge
          Default, starty=None is to center window vertically.

        Examples (when used as function):
        >>> setup (width=200, height=200, startx=0, starty=0)

        sets window to 200x200 pixels, in upper left of screen

        >>> setup(width=.75, height=0.5, startx=None, starty=None)

        sets window to 75% of screen by 50% of screen and centers
        """
        sw = _root.winfo_screenwidth()
        sh = _root.winfo_screenheight()
        if isinstance(width, float) and 0 <= width <= 1:
            width = sw*width
        if startx is None:
            startx = (sw - width) / 2
        if isinstance(height, float) and 0 <= height <= 1:
            height = sh*height
        if starty is None:
            starty = (sh - height) / 2
        self.winsize(width, height, startx, starty)
        

    def _destroy(self):
        global _root, _canvas, _pen
        screen = self.screens[self.screenIndex]        
        root = screen.cv._root
        if root is _root:
            _pen = None
            _root = None
            _canvas = None
        root.destroy()

    def bye(self):
        """Shut the turtlegraphics window.

        Example (for a Pen instance named turtle):
        >>> turtle.bye()
        """
        self._destroy()

    def setWorldCoordinates(self,llx,lly,urx,ury):
        self.screens[self.screenIndex].setWorldCoords(llx,lly,urx,ury)

from sys import exit
class Turtle(Pen):
    def exitOnClick(self):
        """Go into mainloop until the mouse is clicked."""
        def exitGracefully(x,y):
            """docstring for exitGracefully"""
            self.bye()
        self.onClick(exitGracefully)
        try:
            mainloop()
        except AttributeError as e:
            exit(0)

def _getpen():
    global _pen
    if not _pen:
        _pen = Pen()
    return _pen

def getmethparlist(ob):
    "Get strings describing the arguments for the given object"
    argText1 = argText2 = ""
    # bit of a hack for methods - turn it into a function
    # but we drop the "self" param.  bnm hacked for 3.0...
    if type(ob)==types.MethodType:
        fob = ob.__func__
        argOffset = 1
    else:
        fob = ob
        argOffset = 1
    # Try and build one for Python defined functions
    if type(fob) in [types.FunctionType, types.LambdaType]:
        try:
            counter = fob.__code__.co_argcount
            items2 = list(fob.__code__.co_varnames[argOffset:counter])
            realArgs = fob.__code__.co_varnames[argOffset:counter]
            defaults = fob.__defaults__ or []
            defaults = list(["=%s" % repr(name) for name in defaults])
            defaults = [""] * (len(realArgs)-len(defaults)) + defaults
            items1 = list(map(lambda arg, dflt: arg+dflt, realArgs, defaults))
            if fob.__code__.co_flags & 0x4:
                items1.append("*"+fob.__code__.co_varnames[counter])
                items2.append("*"+fob.__code__.co_varnames[counter])
                counter += 1
            if fob.__code__.co_flags & 0x8:
                items1.append("**"+fob.__code__.co_varnames[counter])
                items2.append("**"+fob.__code__.co_varnames[counter])
            argText1 = ", ".join(items1)
            argText1 = "(%s)" % argText1
            argText2 = ", ".join(items2)
            argText2 = "(%s)" % argText2
        except:
            pass
    return argText1, argText2

def _docrevision(docstr):
    """To reduce docstrings from RawPen class for functions
    """
    if docstr is None:
        return None
    newdocstr = docstr.replace("turtle.","")
    newdocstr = newdocstr.replace(" (for a Pen instance named turtle)","")
    return newdocstr

## The following mechanism makes all methods of RawPen and Pen available
## as functions. So we can enhance, change, add, delete methods to these
## classes and do not need to change anything here.

# bnm hacked to work under 3.0
for _cls in TNavigator, TPen, RawPen, Pen:
    for _key in  list(_cls.__dict__.keys()):
        if _key.startswith("_"):
            continue
        pl1, pl2 = getmethparlist(eval(_cls.__name__+'.'+_key))
        if pl1 == "":
            continue
        defstr = ("def %(key)s%(pl1)s: return _getpen().%(key)s%(pl2)s" %
                                        {'key':_key, 'pl1':pl1, 'pl2':pl2})
        exec(defstr)
        eval(_key).__doc__ = _docrevision(_cls.__dict__[_key].__doc__)

mainloop = TK.mainloop
del pl1, pl2, defstr
    
if __name__ == "__main__":
    def demo1():
        setWorldCoordinates(-500,-400,500,400)
        # demo des alten turtle-Moduls
        reset()
        tracer(1)
        up()
        backward(100)
        down()
        # draw 3 squares; the last filled
        width(3)
        for i in range(3):
            if i == 2:
                fill(1)
            for j in range(4):
                forward(20)
                left(90)
            if i == 2:
                color("maroon")
                fill(0)
            up()
            forward(30)
            down()
        width(1)
        color("black")
        # move out of the way
        tracer(0)
        up()
        right(90)
        forward(100)
        right(90)
        forward(100)
        right(180)
        down()
        # some text
        write("startstart", 1)
        write("start", 1)
        color("red")
        # staircase
        for i in range(5):
            forward(20)
            left(90)
            forward(20)
            right(90)
        # filled staircase
        fill(1)
        for i in range(5):
            forward(20)
            left(90)
            forward(20)
            right(90)
        fill(0)
        # more text
        write("wait a moment...")
        tracer(1)

    def demo2():
        # einige weitere und einige neue features
        speed(1)
        st()
        pensize(3)
        setheading(towards(0,0))
        r = distance(0,0)/2.0
        rt(90)
        for i in range(18):
            if pen()["pendown"]:
                pu()
            else:
                pd()
            circle(r,10)
        reset() 
        lt(90)
        colormode(255)
        l = 10
        pencolor("green")
        pensize(3)
        lt(180)
        for i in range(-2,16):
            if i > 0:
                fill(1)
                fillcolor(255-15*i,0,15*i)
            for j in range(3):
                fd(l)
                lt(120)
            l += 10
            lt(15)
            speed((speed()+1)%12)
        fill(0)

        lt(120)
        pu()
        fd(70)
        rt(30)
        pd()
        color("red","yellow")
        speed(0)
        fill(1)
        for i in range(4):
            circle(50,90)
            rt(90)
            fd(30)
            rt(90)
        fill(0)
        lt(90)
        pu(); fd(30); pd(); shape("turtle")

        tri = turtles()[0]
        turtle=Pen()
        turtle.shape("turtle")
        turtle.mode("logo")
        turtle.reset()
        turtle.speed(0)
        turtle.up()
        turtle.goto(280,40)
        turtle.lt(30)
        turtle.down()
        turtle.speed(6)
        turtle.color("blue","orange")
        turtle.pensize(2)
        tri.speed(6)
        setheading(towards(turtle))
        while tri.distance(turtle)>4:
            turtle.fd(3.5)
            turtle.lt(0.6)
            tri.setheading(tri.towards(turtle))
            tri.fd(4)
        tri.write("CAUGHT! ",font=("Arial",16,"bold"), align="right")
        tri.pencolor("black")
        tri.write("  Click me!", font = ("Courier", 12, "bold") )
        tri.pencolor("red")

        def baba(x,y):
            if tri.distance(x,y) < 10:
                resetscreen()
                turtle.ht()
                tri.ht()
                tri.up()
                tri.bk(130)
                tri.pencolor("red")
                tri.bye()

        onClick(baba, 1)
        
    demo1()
    demo2()
    mainloop()
    

