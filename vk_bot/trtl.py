import turtle
import keyboard


def heart(color):
    turtle.color(color)
    turtle.setheading(90)
    for i in range(23):
        turtle.left(10)
        turtle.forward(5)
    turtle.forward(61)
    print(turtle.pos())



heart('#ea7e5d')
keyboard.add_hotkey('w', lambda: turtle.forward(10))
keyboard.add_hotkey('s', lambda: turtle.back(10))
keyboard.add_hotkey('a', lambda: turtle.right(10))
keyboard.add_hotkey('d', lambda: turtle.left(10))

turtle.exitonclick()