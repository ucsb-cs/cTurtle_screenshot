import sys
from cTurtle import *

# This is just the demo code from copied form cTurtle.py
# See the Copyright notice in original/cTurtle.py

def main():
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


if __name__ == '__main__':
    sys.exit(main())
