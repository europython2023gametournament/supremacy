import numpy as np
import pythreejs as p3
import turtle
import pyglet

from .. import config


class Vehicle:

    def __init__(self, x, y, team, number, kind, batch, heading=0):

        self.team = team
        self.number = number
        self.speed = config.speed[kind]
        self.health = config.health[kind]
        self.attack = config.attack[kind]
        self.cost = config.cost[kind]

        print(config.images.keys())

        self.x = x
        self.y = y
        self._heading = heading

        self.avatar = pyglet.sprite.Sprite(img=config.images[f'{kind}_{self.number}'],
                                           x=self.x,
                                           y=self.y,
                                           rotation=-heading,
                                           batch=batch)
        # image.anchor_x = image.width // 2

        # geometry = p3.BoxGeometry(width=10, height=10, depth=10)
        # self.avatar = p3.Mesh(geometry=geometry,
        #                       material=p3.MeshBasicMaterial(color=color),
        #                       position=[self.x, self.y, 0])

        # self.avatar = turtle.Turtle()
        # self.avatar.speed(0)
        # self.avatar.penup()
        # self.avatar.setx(x)
        # self.avatar.sety(y)
        # self.avatar.color(color)
        # self.avatar.shape(kind)
        # self.avatar.setheading(heading)

    def forward(self, dist, nx, ny):
        pos = self.position + self.vector * dist
        x = pos[0] % nx
        y = pos[1] % ny
        if x < 0:
            x = nx + x
        if y < 0:
            y = ny + y
        self.x = x
        self.y = y
        self.avatar.x = self.x
        self.avatar.y = self.y

    # @property
    # def x(self) -> int:
    #     return self._x

    # @x.setter
    # def x(self, value):
    #     self._x = value

    # @property
    # def y(self) -> int:
    #     return self._y

    @property
    def position(self):
        return np.array([self.x, self.y])

    @property
    def heading(self) -> float:
        return self._heading

    @heading.setter
    def heading(self, angle: float):
        self._heading = angle
        self.avatar.rotation = -angle

    @property
    def vector(self) -> np.ndarray:
        h = self.heading * np.pi / 180.0
        return np.array([np.cos(h), np.sin(h)])

    def ray_trace(self, dt: float) -> np.ndarray:
        vt = self.speed * dt
        ray = self.vector.reshape((2, 1)) * np.linspace(1, vt, int(vt) + 1)
        return (self.position.reshape((2, 1)) + ray).astype(int)

    def get_distance(self, pos: tuple) -> float:
        return np.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2)


class Tank(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='tank', **kwargs)

    def move(self, dt, path, nx, ny):
        no_obstacles = (np.sum(path == 0)) == 0
        if no_obstacles:
            self.forward(self.speed * dt, nx, ny)


class Ship(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='ship', **kwargs)

    def move(self, dt, path, nx, ny):
        no_obstacles = (np.sum(path == 1)) == 0
        if no_obstacles:
            self.forward(self.speed * dt, nx, ny)


class Jet(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='jet', **kwargs)

    def move(self, dt):
        self.forward(self.speed * dt)
