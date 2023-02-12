import numpy as np
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
        self.batch = batch
        # self.cooldown = 0

        x, y = wrap_position(x, y)
        self.x = x
        self.y = y
        self._heading = heading

        self.avatar = pyglet.sprite.Sprite(img=config.images[f'{kind}_{self.number}'],
                                           x=self.x,
                                           y=self.y,
                                           batch=batch)
        self.avatar.rotation = -heading
        self.label = None
        self.make_label()

    def make_label(self):
        if self.label is not None:
            self.label.delete()
        self.label = pyglet.text.Label(str(self.health),
                                       color=(0, 0, 0, 255),
                                       font_size=8,
                                       x=self.x,
                                       y=self.y,
                                       anchor_x='center',
                                       anchor_y='center',
                                       batch=self.batch)

    def forward(self, dist, nx, ny):
        pos = self.get_position() + self.get_vector() * dist
        x, y = wrap_position(*pos)
        self.x = x
        self.y = y
        self.avatar.x = self.x
        self.avatar.y = self.y
        self.label.x = self.x
        self.label.y = self.y

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

    def get_position(self):
        return np.array([self.x, self.y])

    def get_heading(self) -> float:
        return self._heading

    def set_heading(self, angle: float):
        self._heading = angle
        self.avatar.rotation = -angle

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
        player = self.owner.owner
        x = int(self.x)
        y = int(self.y)
        if np.sum(player.game_map[y - 1:y + 2, x - 1:x + 2]) < 1:
            print("No land found around ship, cannot build base on water!")
            return
        player.build_base(x=self.x, y=self.y)
        self.owner.transformed_ships.append(self.uid)
        self.avatar.delete()


class Jet(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='jet', **kwargs)

    def move(self, dt, path, nx, ny):
        self.forward(self.speed * dt, nx, ny)
