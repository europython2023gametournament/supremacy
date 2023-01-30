from matplotlib import colors
import turtle


class Graphics:

    def __init__(self, game_map):

        self.game_map = game_map
        self.nx = self.game_map.nx
        self.ny = self.game_map.ny
        self.ng = self.game_map.ng
        self.screen = turtle.Screen()
        self.screen.clearscreen()

        self.screen.setup(width=self.nx, height=self.ny)
        self.screen.setworldcoordinates(0, 0, self.nx, self.ny)

        cv = self.screen.getcanvas()
        cv.adjustScrolls()

        self.screen.bgpic('background.png')
        cv.itemconfig(self.screen._bgpic, anchor="sw")

        tank = ((-4, -5), (4, -5), (4, 5), (1, 5), (1, 10), (-1, 10), (-1, 5),
                (-4, 5))
        ship = ((-4, -5), (4, -5), (4, 5), (0, 10), (-4, 5))
        jet = ((-4, -5), (4, -5), (1, -4), (1, -2), (8, -2), (1, 3), (0, 10),
               (-1, 3), (-8, -2), (-1, -2), (-1, -4))

        self.screen.register_shape("tank", tank)
        self.screen.register_shape("ship", ship)
        self.screen.register_shape("jet", jet)

        self.pen = turtle.Turtle()
        self.pen.speed(0)
        # self.pen.hideturtle()
        self.pen.penup()
        self.pen.goto(self.nx, 0)
        self.pen.color('red')
        self.pen.setheading(90)
        self.pen.pendown()
        self.pen.forward(500)
        input()

        # for j in range(self.ny):
        #     for i in range(self.nx):
        #         s

        # self.screen.register_shape("jet.gif")

        # self.t = turtle.Turtle()

        # self.t.shape("jet.gif")
        # self.t.setheading(45)
        # self.t.forward(500)
        # self.t.setheading(90)
        # self.t.forward(200)


#

    def draw_base_star(self, x, y, n):
        star_size = 10
        self.pen.penup()
        self.pen.color(colors.to_hex(f'C{n}'))
        self.pen.goto(x - 0.5 * star_size, y - 0.25 * star_size)
        self.pen.setheading(0)
        self.pen.pendown()
        self.pen.begin_fill()
        for i in range(5):
            self.pen.forward(star_size)
            self.pen.left(360 / 2.5)
        self.pen.end_fill()
        self.pen.penup()
