import numpy as np
import pyglet


class Graphics:

    def __init__(self, game_map):

        self.game_map = game_map
        self.nx = self.game_map.nx
        self.ny = self.game_map.ny
        self.ng = self.game_map.ng

        # geometry = p3.PlaneGeometry(width=self.nx,
        #                             height=self.ny,
        #                             widthSegments=1,
        #                             heightSegments=1)
        # # self._cmap = mpl.colormaps[cmap]
        # # colors = np.ones([self.ny, self.nx, 3])
        # colors = np.repeat(self.game_map.array, 3, axis=1).reshape(self.ny, self.nx, 3)
        # texture = p3.DataTexture(
        #     data=colors.astype('float32'),
        #     format="RGBFormat",
        #     type="FloatType",
        # )
        # self.canvas = p3.Mesh(geometry=geometry,
        #                       material=p3.MeshBasicMaterial(map=texture),
        #                       position=[0.5 * self.nx, 0.5 * self.ny, 0])

        # # Create the scene and the renderer
        # scaling = 0.5
        # view_width = self.nx * scaling
        # view_height = self.ny * scaling
        # self.camera = p3.PerspectiveCamera(
        #     position=[0.5 * self.nx, 0.5 * self.ny, self.nx],
        #     aspect=view_width / view_height,
        #     far=5 * self.nx)
        # self.scene = p3.Scene(children=[self.canvas, self.camera], background="#DDDDDD")
        # self.controller = p3.OrbitControls(controlling=self.camera)
        # self.renderer = p3.Renderer(camera=self.camera,
        #                             scene=self.scene,
        #                             controls=[self.controller],
        #                             width=view_width,
        #                             height=view_height)

        self.window = pyglet.window.Window(self.nx, self.ny)
        self.background = pyglet.resource.image('background.png')
        self.main_batch = pyglet.graphics.Batch()
        self.jet_image = pyglet.image.load('jet.png')

        @self.window.event
        def on_draw():
            self.window.clear()
            self.background.blit(0, 0)
            self.main_batch.draw()

    def add(self, obj):
        self.scene.add(obj)

    def remove(self, obj):
        self.scene.remove(obj)

        # renderer

        # self.screen = turtle.Screen()
        # self.screen.clearscreen()

        # self.screen.setup(width=self.nx, height=self.ny)
        # self.screen.setworldcoordinates(0, 0, self.nx, self.ny)

        # cv = self.screen.getcanvas()
        # cv.adjustScrolls()

        # self.screen.bgpic('background.png')
        # cv.itemconfig(self.screen._bgpic, anchor="sw")

        # tank = ((-4, -5), (4, -5), (4, 5), (1, 5), (1, 10), (-1, 10), (-1, 5), (-4, 5))
        # ship = ((-4, -5), (4, -5), (4, 5), (0, 10), (-4, 5))
        # jet = ((-4, -5), (4, -5), (1, -4), (1, -2), (8, -2), (1, 3), (0, 10), (-1, 3),
        #        (-8, -2), (-1, -2), (-1, -4))

        # self.screen.register_shape("tank", tank)
        # self.screen.register_shape("ship", ship)
        # self.screen.register_shape("jet", jet)

        # self.pen = turtle.Turtle()
        # self.pen.speed(0)
        # self.pen.hideturtle()
        # # self.pen.penup()
        # # self.pen.goto(0, 0)
        # # self.pen.color('red')
        # # # self.pen.setheading(90)
        # # self.pen.pendown()
        # # # self.pen.forward(500)
        # # self.pen.goto(self.nx, 0)
        # # self.pen.goto(self.nx, self.ny)
        # # self.pen.goto(0, self.ny)
        # # self.pen.goto(0, 10)
        # self.pen.penup()
        # # input()

        # # for j in range(self.ny):
        # #     for i in range(self.nx):
        # #         s

        # # self.screen.register_shape("jet.gif")

        # # self.t = turtle.Turtle()

        # # self.t.shape("jet.gif")
        # # self.t.setheading(45)
        # # self.t.forward(500)
        # # self.t.setheading(90)
        # # self.t.forward(200)

    # def add_bases(self, players):
    #     for n, p in enumerate(players.values()):
    #         self.draw_base(x=p.bases[0].x, y=p.bases[0].y, color=p.color)

    # def draw_base(self, x, y, color):
    #     size = 15
    #     geom = p3.SphereGeometry(
    #         radius=size,
    #         widthSegments=8,
    #         heightSegments=6,
    #         # phiStart=0,
    #         # phiLength=1.5*pi,
    #         # thetaStart=0,
    #         # thetaLength=2.0*pi/3.0
    #     )
    #     mat = p3.MeshBasicMaterial(color=color)
    #     self.scene.add(p3.Mesh(geometry=geom, material=mat, position=[x, y, 0]))
    #     # self.pen.penup()
    #     # self.pen.color(color)
    #     # self.pen.goto(x - 0.5 * star_size, y - 0.25 * star_size)
    #     # self.pen.setheading(0)
    #     # self.pen.pendown()
    #     # self.pen.begin_fill()
    #     # for i in range(5):
    #     #     self.pen.forward(star_size)
    #     #     self.pen.left(360 / 2.5)
    #     # self.pen.end_fill()
    #     # self.pen.penup()
