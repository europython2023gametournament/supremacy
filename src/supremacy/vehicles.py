# SPDX-License-Identifier: BSD-3-Clause

from typing import Any, Iterator, Sequence, Tuple, Union

import numpy as np
import pyglet

from . import config
from . import tools as tls


class Vehicle:
    def __init__(
        self,
        x: float,
        y: float,
        team: str,
        number: int,
        kind: str,
        batch: Any,
        owner: Any,
        uid: str,
        heading: float = 0,
    ):
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
        self.previous_position = None

        x, y = tls.wrap_position(x, y)
        self.x = x
        self.y = y
        self.screen_x = x * config.scaling
        self.screen_y = y * config.scaling
        self._heading = heading
        self.avatar = None
        self.make_avatar()
        self._as_info = None

    def make_avatar(self):
        if self.health <= 0:
            return
        if self.avatar is not None:
            self.avatar.delete()
        self.avatar = pyglet.sprite.Sprite(
            img=config.images[f"{self.kind}_{self.number}_{self.health}"],
            x=self.screen_x,
            y=self.screen_y,
            batch=self.batch,
        )
        self.avatar.rotation = -self._heading

    def set_position(self, x: float, y: float):
        self.x = x
        self.y = y
        self.screen_x = x * config.scaling
        self.screen_y = y * config.scaling
        self.avatar.x = self.screen_x
        self.avatar.y = self.screen_y

    def reset_info(self):
        self._as_info = None

    def as_info(self) -> dict:
        if self._as_info is None:
            self._as_info = {
                "team": self.team,
                "number": self.number,
                "uid": self.uid,
                "speed": self.speed,
                "health": self.health,
                "attack": self.attack,
                "x": self.x,
                "y": self.y,
                "heading": self.get_heading(),
                "vector": self.get_vector(),
                "position": self.get_position(),
                "stopped": self.stopped,
                "stuck": self.stuck(),
                "kind": self.kind,
            }
        return self._as_info

    def get_position(self) -> np.ndarray:
        """
        Return the curent position of the vehicle (x, y).
        """
        return np.array([self.x, self.y])

    def get_heading(self) -> float:
        """
        Return the current heading angle (in degrees) of the vehicle.
        East is 0, North is 90, West is 180, South is 270.
        """
        return self._heading

    def set_heading(self, angle: float):
        """
        Set the heading angle (in degrees) of the vehicle.
        East is 0, North is 90, West is 180, South is 270.
        """
        self._heading = angle
        self.avatar.rotation = -angle

    def get_vector(self) -> np.ndarray:
        """
        Return the vector [vx, vy] corresponding to the vehicle's current heading.
        """
        h = self.get_heading() * np.pi / 180.0
        return np.array([np.cos(h), np.sin(h)])

    def set_vector(self, vec: Union[np.ndarray, Sequence[float]]):
        """
        Set the vehicle's heading according to the given vector [vx, vy].
        """
        vec = np.asarray(vec) / np.linalg.norm(vec)
        h = np.arccos(np.dot(vec, [1, 0])) * 180 / np.pi
        if vec[1] < 0:
            h = 360 - h
        self.set_heading(h)

    def goto(self, x: float, y: float, shortest_path: bool = True):
        """
        Set the vehicle's heading to point towards the given position.
        If ``shortest_path`` is True, the vehicle will take the shortest path,
        potentially through the periodic boundaries.
        If ``shortest_path`` is False, the vehicle will take the direct path, and not
        travel through the periodic boundaries.

        Parameters
        ----------
        x : float
            The x-coordinate of the position to go to.
        y : float
            The y-coordinate of the position to go to.
        shortest_path : bool, optional
            Whether to take the shortest path, potentially through the periodic
            boundaries. Default is True.
        """
        if not shortest_path:
            self.set_vector([x - self.x, y - self.y])
            return
        d, xl, yl = tls.periodic_distances(self.x, self.y, x, y)
        ind = np.argmin(d)
        self.set_vector(
            [xl[ind] - (self.x + config.nx), yl[ind] - (self.y + config.ny)]
        )

    def next_position(self, dt: float) -> Tuple[float, float]:
        pos = self.get_position() + self.get_vector() * self.speed * dt
        x, y = tls.wrap_position(*pos)
        return x, y

    def get_distance(self, x: float, y: float, shortest=True) -> float:
        """
        Return the distance between the vehicle's current position and the given
        position (x, y).
        If ``shortest`` is True, the distance is the shortest distance, potentially
        through the periodic boundaries.

        Parameters
        ----------
        x : float
            The x-coordinate of the position.
        y : float
            The y-coordinate of the position.
        shortest : bool, optional
            Whether to take the shortest path, potentially through the periodic
            boundaries. Default is True.
        """
        if not shortest:
            return tls.distance_on_plane(self.x, self.y, x, y)
        else:
            return tls.distance_on_torus(self.x, self.y, x, y)

    def delete(self):
        self.avatar.delete()
        # self.label.delete()

    def stop(self):
        self.stopped = True

    def start(self):
        self.stopped = False

    def move(self):
        self.previous_position = self.get_position()

    def stuck(self):
        return all(self.get_position() == self.previous_position)


class VehicleProxy:
    def __init__(self, vehicle: Vehicle):
        self._data = vehicle.as_info()
        for key, item in self._data.items():
            setattr(self, key, item)
        self.owner = tls.ReadOnly(vehicle.owner.as_info())
        self.set_heading = vehicle.set_heading
        self.set_vector = vehicle.set_vector
        self.goto = vehicle.goto
        self.get_distance = vehicle.get_distance
        if vehicle.kind == "ship":
            self.convert_to_base = vehicle.convert_to_base
        self.stop = vehicle.stop
        self.start = vehicle.start

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def keys(self) -> Iterator:
        return self._data.keys()

    def values(self) -> Iterator:
        return self._data.values()

    def items(self) -> Iterator:
        return self._data.items()


class Tank(Vehicle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind="tank", **kwargs)

    def move(self, x: float, y: float, map_value: int):
        super().move()
        if map_value == 1:
            self.set_position(x, y)


class Ship(Vehicle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind="ship", **kwargs)

    def move(self, x: float, y: float, map_value: int):
        super().move()
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
        if len(xx) == 0:
            print("Error finding land around ship....")
            return
        uid = player.build_base(x=x + xx[0] - 1, y=y + yy[0] - 1)
        player.transformed_ships.append(self.uid)
        self.avatar.delete()
        return uid


class Jet(Vehicle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind="jet", **kwargs)

    def move(self, x: float, y: float, map_value: int):
        super().move()
        self.set_position(x, y)
