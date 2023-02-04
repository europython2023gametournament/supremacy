import numpy as np
import pythreejs as p3
import turtle
import pyglet

from .. import config
from .tools import wrap_position


class Vehicle:

    def __init__(self, x, y, team, number, kind, batch, owner, uid, heading=0):

        self.team = team
        self.number = number
        self.owner = owner
        self.uid = uid
        self.speed = config.speed[kind]
        self.health = config.health[kind]
        self.attack = config.attack[kind]
        self.kind = kind

        # print(config.images.keys())
        # x = x % config.nx
        # y = y % config.ny
        # if x < 0:
        #     x = config.nx + x
        # if y < 0:
        #     y = config.ny + y
        x, y = wrap_position(x, y)
        self.x = x
        self.y = y
        self._heading = heading

        self.avatar = pyglet.sprite.Sprite(img=config.images[f'{kind}_{self.number}'],
                                           x=self.x,
                                           y=self.y,
                                           batch=batch)
        self.avatar.rotation = -heading
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

    # def wrap_position(self, x, y):
    #     x = x % config.nx
    #     y = y % config.ny
    #     if x < 0:
    #         x = config.nx + x
    #     if y < 0:
    #         y = config.ny + y
    #     return x, y

    def forward(self, dist, nx, ny):
        pos = self.get_position() + self.get_vector() * dist
        x, y = wrap_position(*pos)
        self.x = x
        self.y = y
        self.avatar.x = self.x
        self.avatar.y = self.y

    def as_info(self):
        return {
            'team': self.team,
            'number': self.number,
            # 'owner': self.owner.as_info(),
            'uid': self.uid,
            'speed': self.speed,
            'health': self.health,
            'attack': self.attack,
            'x': self.x,
            'y': self.y,
            'heading': self.get_heading(),
            'vector': self.get_vector(),
            'position': self.get_position()
        }

    # @property
    # def x(self) -> int:
    #     return self._x

    # @x.setter
    # def x(self, value):
    #     self._x = value

    # @property
    # def y(self) -> int:
    #     return self._y

    # @property
    def get_position(self):
        return np.array([self.x, self.y])

    # @property
    def get_heading(self) -> float:
        return self._heading

    # @heading.setter
    def set_heading(self, angle: float):
        self._heading = angle
        self.avatar.rotation = -angle

    # @property
    def get_vector(self) -> np.ndarray:
        h = self.get_heading() * np.pi / 180.0
        return np.array([np.cos(h), np.sin(h)])

    def set_vector(self, vec) -> np.ndarray:
        vec = vec / np.linalg.norm(vec)
        h = np.arccos(np.dot(vec, [1, 0])) * 180 / np.pi
        if vec[1] < 0:
            h = 360 - h
        self.set_heading(h)

    def goto(self, x, y):
        self.set_vector([x - self.x, y - self.y])

    def ray_trace(self, dt: float) -> np.ndarray:
        vt = self.speed * dt
        ray = self.get_vector().reshape((2, 1)) * np.linspace(1, vt, int(vt) + 1)
        return (self.get_position().reshape((2, 1)) + ray).astype(int)

    def get_distance(self, pos: tuple) -> float:
        return np.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2)


class VehicleProxy:

    def __init__(self, vehicle):
        self._data = vehicle.as_info()
        self._data['owner'] = vehicle.owner.as_info()
        self.get_position = vehicle.get_position
        self.get_heading = vehicle.get_heading
        self.set_heading = vehicle.set_heading
        self.get_vector = vehicle.get_vector
        self.set_vector = vehicle.set_vector
        self.goto = vehicle.goto
        self.get_distance = vehicle.get_distance
        if vehicle.kind == 'ship':
            self.convert_to_base = vehicle.convert_to_base

    def __getitem__(self, key):
        return self._data[key]

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()


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

    def convert_to_base(self):
        self.owner.owner.build_base(x=self.x, y=self.y)
        self.owner.transformed_ships.append(self.uid)
        self.avatar.delete()


class Jet(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='jet', **kwargs)

    def move(self, dt):
        self.forward(self.speed * dt)
