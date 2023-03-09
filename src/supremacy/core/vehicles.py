# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import pyglet

from .. import config
from .tools import ReadOnly, wrap_position, eucledian_distance, periodic_distances


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

    # def forward(self, dist):
    #     pos = self.get_position() + self.get_vector() * dist
    #     x, y = wrap_position(*pos)
    #     self.x = x
    #     self.y = y
    #     self.avatar.x = self.x
    #     self.avatar.y = self.y
    #     self.label.x = self.x
    #     self.label.y = self.y

    def set_position(self, x, y):
        # pos = self.get_position() + self.get_vector() * dist
        # x, y = wrap_position(*pos)
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

    def goto(self, x, y, shortest_path=True):
        if not shortest_path:
            self.set_vector([x - self.x, y - self.y])
            return
        d, xl, yl = periodic_distances(self.x, self.y, x, y)
        ind = np.argmin(d)
        self.set_vector(
            [xl[ind] - (self.x + config.nx), yl[ind] - (self.y + config.ny)])

    def ray_trace(self, dt: float) -> np.ndarray:
        vt = self.speed * dt
        ray = self.get_vector().reshape((2, 1)) * np.linspace(0, vt, int(vt) + 2)
        return (self.get_position().reshape((2, 1)) + ray).astype(int)

    def next_position(self, dt: float) -> np.ndarray:
        # return self.get_position() + self.get_vector() * self.speed * dt
        pos = self.get_position() + self.get_vector() * self.speed * dt
        x, y = wrap_position(*pos)
        return x, y

    def get_distance(self, x: float, y: float, shortest=True) -> float:
        if not shortest:
            return eucledian_distance(self.x, self.y, x, y)
        else:
            return periodic_distances(self.x, self.y, x, y)[0].min()

    def delete(self):
        self.avatar.delete()
        self.label.delete()


class VehicleProxy:

    def __init__(self, vehicle):
        for key, item in vehicle.as_info().items():
            setattr(self, key, item)
        self.owner = ReadOnly(vehicle.owner.as_info())
        # self.get_position = vehicle.get_position
        # self.get_heading = vehicle.get_heading
        self.set_heading = vehicle.set_heading
        # self.get_vector = vehicle.get_vector
        self.set_vector = vehicle.set_vector
        self.goto = vehicle.goto
        self.get_distance = vehicle.get_distance
        if vehicle.kind == 'ship':
            self.convert_to_base = vehicle.convert_to_base

    # def __getitem__(self, key):
    #     return self._data[key]

    # def keys(self):
    #     return self._data.keys()

    # def values(self):
    #     return self._data.values()

    # def items(self):
    #     return self._data.items()


class Tank(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='tank', **kwargs)

    # def move(self, dt, path):
    #     obstacle = np.searchsorted(-path, 0)
    #     # fact = 1
    #     if obstacle == len(path):
    #         fact = 1
    #     else:
    #         fact = (obstacle - 1) / len(path)
    #     if fact < 0:
    #         print(f'warning, negative TANK factor {fact}')
    #     self.forward(self.speed * dt * fact)
    #     # no_obstacles = (np.sum(path == 0)) == 0
    #     # if no_obstacles:
    #     #     self.forward(self.speed * dt)
    def move(self, x, y, map_value):
        if map_value == 1:
            self.set_position(x, y)


class Ship(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='ship', **kwargs)

    # def move(self, dt, path):
    #     obstacle = np.searchsorted(path, 1)
    #     # fact = 1
    #     if obstacle == len(path):
    #         fact = 1
    #     else:
    #         fact = (obstacle - 1) / len(path)
    #     if fact < 0:
    #         print(f'warning, negative SHIP factor {fact}')
    #     self.forward(self.speed * dt * fact)
    #     # no_obstacles = (np.sum(path == 1)) == 0
    #     # if no_obstacles:
    #     #     self.forward(self.speed * dt)
    def move(self, x, y, map_value):
        if map_value == 0:
            self.set_position(x, y)

    def convert_to_base(self):
        player = self.owner.owner
        x = int(self.x)
        y = int(self.y)
        local_views = player.game_map.view(x=x, y=y, dx=1, dy=1)
        if sum([view.sum() for view in local_views]) < 1:
            print("No land found around ship, cannot build base on water!")
            return
        yy, xx = np.where(local_views[0] == 1)
        player.build_base(x=x + xx[0] - 1, y=y + yy[0] - 1)
        player.transformed_ships.append(self.uid)
        self.avatar.delete()


class Jet(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='jet', **kwargs)

    def move(self, x, y, map_value):
        # self.forward(self.speed * dt)
        self.set_position(x, y)
