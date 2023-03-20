# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import pyglet

from . import config
from . import tools as tls


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
        self.stopped = False

        x, y = tls.wrap_position(x, y)
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
        self._as_info = None

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

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.avatar.x = self.x
        self.avatar.y = self.y
        self.label.x = self.x
        self.label.y = self.y

    def reset_info(self):
        self._as_info = None

    def as_info(self):
        if self._as_info is None:
            self._as_info = {
                'team': self.team,
                'number': self.number,
                'uid': self.uid,
                'speed': self.speed,
                'health': self.health,
                'attack': self.attack,
                'x': self.x,
                'y': self.y,
                'heading': self.get_heading(),
                'vector': self.get_vector(),
                'position': self.get_position(),
                'stopped': self.stopped
            }
        return self._as_info

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
        d, xl, yl = tls.periodic_distances(self.x, self.y, x, y)
        ind = np.argmin(d)
        self.set_vector(
            [xl[ind] - (self.x + config.nx), yl[ind] - (self.y + config.ny)])

    def ray_trace(self, dt: float) -> np.ndarray:
        vt = self.speed * dt
        ray = self.get_vector().reshape((2, 1)) * np.linspace(0, vt, int(vt) + 2)
        return (self.get_position().reshape((2, 1)) + ray).astype(int)

    def next_position(self, dt: float) -> np.ndarray:
        pos = self.get_position() + self.get_vector() * self.speed * dt
        x, y = tls.wrap_position(*pos)
        return x, y

    def get_distance(self, x: float, y: float, shortest=True) -> float:
        if not shortest:
            return tls.distance_on_plane(self.x, self.y, x, y)
        else:
            return tls.distance_on_torus(self.x, self.y, x, y)

    def delete(self):
        self.avatar.delete()
        self.label.delete()

    def stop(self):
        self.stopped = True

    def start(self):
        self.stopped = False


class VehicleProxy:

    def __init__(self, vehicle):
        for key, item in vehicle.as_info().items():
            setattr(self, key, item)
        self.owner = tls.ReadOnly(vehicle.owner.as_info())
        self.set_heading = vehicle.set_heading
        self.set_vector = vehicle.set_vector
        self.goto = vehicle.goto
        self.get_distance = vehicle.get_distance
        if vehicle.kind == 'ship':
            self.convert_to_base = vehicle.convert_to_base
        self.stop = vehicle.stop
        self.start = vehicle.start


class Tank(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='tank', **kwargs)

    def move(self, x, y, map_value):
        if map_value == 1:
            self.set_position(x, y)


class Ship(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='ship', **kwargs)

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
        self.set_position(x, y)
