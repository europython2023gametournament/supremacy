# SPDX-License-Identifier: BSD-3-Clause

import uuid
from typing import Any

import numpy as np
import pyglet


from . import config
from .tools import distance_on_plane, distance_on_torus, wrap_position
from .vehicles import Jet, Ship, Tank, VehicleProxy


class Base:
    def __init__(
        self,
        x: float,
        y: float,
        team: str,
        number: int,
        batch: Any,
        owner: Any,
        uid: str,
        high_contrast: bool = False,
    ):
        self.x = x
        self.y = y
        self.screen_x = x * config.scaling
        self.screen_y = y * config.scaling
        self._as_info = None
        self.kind = "base"
        self.health = config.health["base"]
        self.attack = config.attack["base"]
        self.team = team
        self.number = number
        self.owner = owner
        self.batch = batch
        self.uid = uid
        self.competing = False
        self.high_contrast = high_contrast
        muid = uuid.uuid4().hex
        self.mines = {
            muid: Mine(
                x=self.x,
                y=self.y,
                team=self.team,
                number=self.number,
                owner=self,
                uid=muid,
            )
        }
        self.crystal = 0
        self.owner.update_player_map(x=self.x, y=self.y)
        self.avatar = None
        if self.high_contrast:
            rgb = config.colors[self.number]
            self.shape = pyglet.shapes.Rectangle(
                x=self.screen_x - (config.competing_mine_radius * config.scaling),
                y=self.screen_y - (config.competing_mine_radius * config.scaling),
                width=config.competing_mine_radius * 2 * config.scaling,
                height=config.competing_mine_radius * 2 * config.scaling,
                color=tuple(int(round(c * 255)) for c in rgb[:-1]) + (50,),
                batch=batch,
            )
        else:
            self.shape = None
        self.health_label = None
        self.mines_label = None
        self.clabel = None
        self.make_avatar()

        ix = int(x)
        iy = int(y)
        dx = config.vehicle_offset
        offset = None
        while offset is None:
            xx, yy = wrap_position(ix + dx, iy + dx)
            if self.owner.game_map[yy, xx] == 1:
                offset = (dx, dx)
                break
            xx, yy = wrap_position(ix + dx, iy - dx)
            if self.owner.game_map[yy, xx] == 1:
                offset = (dx, -dx)
                break
            xx, yy = wrap_position(ix - dx, iy + dx)
            if self.owner.game_map[yy, xx] == 1:
                offset = (-dx, dx)
                break
            xx, yy = wrap_position(ix - dx, iy - dx)
            if self.owner.game_map[yy, xx] == 1:
                offset = (-dx, -dx)
                break
            dx += 1
        self.tank_offset = offset

        dx = config.vehicle_offset
        offset = None
        while offset is None:
            xx, yy = wrap_position(ix + dx, iy + dx)
            if self.owner.game_map[yy, xx] == 0:
                offset = (dx, dx)
                break
            xx, yy = wrap_position(ix + dx, iy - dx)
            if self.owner.game_map[yy, xx] == 0:
                offset = (dx, -dx)
                break
            xx, yy = wrap_position(ix - dx, iy + dx)
            if self.owner.game_map[yy, xx] == 0:
                offset = (-dx, dx)
                break
            xx, yy = wrap_position(ix - dx, iy - dx)
            if self.owner.game_map[yy, xx] == 0:
                offset = (-dx, -dx)
                break
            dx += 1
        self.ship_offset = offset

    def make_avatar(self):
        if self.health <= 0:
            return
        if self.health_label is not None:
            self.avatar.delete()
            self.health_label.delete()
            self.mines_label.delete()
        self.avatar = pyglet.sprite.Sprite(
            img=config.images[f"base_{self.number}{'_C' if self.competing else ''}"],
            x=self.screen_x,
            y=self.screen_y,
            batch=self.batch,
        )
        self.health_label = pyglet.sprite.Sprite(
            img=config.images[f"health_{self.health}"],
            x=self.screen_x - (6 * config.scaling),
            y=self.screen_y + (18 * config.scaling),
            batch=self.batch,
        )
        self.mines_label = pyglet.sprite.Sprite(
            img=config.images[f"mines_{len(self.mines)}"],
            x=self.screen_x + (18 * config.scaling),
            y=self.screen_y + (18 * config.scaling),
            batch=self.batch,
        )

    def delete(self):
        self.avatar.delete()
        self.health_label.delete()
        self.mines_label.delete()
        if self.shape is not None:
            self.shape.delete()

    def reset_info(self):
        self._as_info = None

    def as_info(self) -> dict:
        if self._as_info is None:
            self._as_info = {
                "x": self.x,
                "y": self.y,
                "team": self.team,
                "number": self.number,
                "mines": len(self.mines),
                "crystal": self.crystal,
                "uid": self.uid,
                "position": self.get_position(),
            }
        return self._as_info

    def mine_cost(self) -> int:
        return config.cost["mine"] * (2 ** (len(self.mines) - 1))

    def not_enough_crystal(self, kind: str) -> bool:
        if kind == "mine":
            cost = self.mine_cost()
        else:
            cost = config.cost[kind]

        not_ok = self.crystal < cost
        if not_ok:
            print(f"Not enough crystal to build {kind}")
        return not_ok

    def build_mine(self):
        if self.not_enough_crystal("mine"):
            return
        print(f"Player {self.team} is building a MINE at {self.x}, {self.y}")
        self.crystal -= self.mine_cost()
        uid = uuid.uuid4().hex
        self.mines[uid] = Mine(
            x=self.x, y=self.y, team=self.team, number=self.number, owner=self, uid=uid
        )
        self.make_avatar()

    def build_tank(self, heading: float) -> str:
        """
        Build a tank at this base.
        Returns the uid of the tank.

        Parameters
        ----------
        heading : float
            The initial heading of the tank in degrees.
        """
        if self.not_enough_crystal("tank"):
            return
        print(f"Player {self.team} is building a TANK at {self.x}, {self.y}")
        uid = uuid.uuid4().hex
        tank = Tank(
            x=self.x + self.tank_offset[0],
            y=self.y + self.tank_offset[1],
            team=self.team,
            number=self.number,
            heading=heading,
            batch=self.batch,
            owner=self,
            uid=uid,
        )
        self.owner.tanks[uid] = tank
        self.crystal -= config.cost["tank"]
        return VehicleProxy(tank)

    def build_ship(self, heading: float) -> str:
        """
        Build a ship at this base.
        Returns the uid of the ship.

        Parameters
        ----------
        heading : float
            The initial heading of the ship in degrees.
        """
        if self.not_enough_crystal("ship"):
            return
        print(f"Player {self.team} is building a SHIP at {self.x}, {self.y}")
        uid = uuid.uuid4().hex
        ship = Ship(
            x=self.x + self.ship_offset[0],
            y=self.y + self.ship_offset[1],
            team=self.team,
            number=self.number,
            heading=heading,
            batch=self.batch,
            owner=self,
            uid=uid,
        )
        self.owner.ships[uid] = ship
        self.crystal -= config.cost["ship"]
        return VehicleProxy(ship)

    def build_jet(self, heading: float) -> str:
        """
        Build a jet at this base.
        Returns the uid of the jet.

        Parameters
        ----------
        heading : float
            The initial heading of the jet in degrees.
        """
        if self.not_enough_crystal("jet"):
            return
        print(f"Player {self.team} is building a JET at {self.x}, {self.y}")
        uid = uuid.uuid4().hex
        jet = Jet(
            x=self.x,
            y=self.y,
            team=self.team,
            number=self.number,
            heading=heading,
            batch=self.batch,
            owner=self,
            uid=uid,
        )
        self.owner.jets[uid] = jet
        self.crystal -= config.cost["jet"]
        return VehicleProxy(jet)

    def get_distance(self, x: float, y: float, shortest=True) -> float:
        """
        Get the distance between this base and the given position (x, y).
        If shortest is ``True``, the shortest distance is returned, potentially going
        via the periodic boundaries.

        Parameters
        ----------
        x : float
            The x position.
        y : float
            The y position.
        shortest : bool
            If shortest is ``True``, the shortest distance is returned, potentially
            going via the periodic boundaries. If it is ``False``, a naive distance
            ignoring the periodic boundaries is returned.
        """
        if not shortest:
            return distance_on_plane(self.x, self.y, x, y)
        else:
            return distance_on_torus(self.x, self.y, x, y)

    def get_position(self) -> np.ndarray:
        """
        Return the curent position of the vehicle (x, y).
        """
        return np.array([self.x, self.y])


class BaseProxy:
    def __init__(self, base):
        self._data = base.as_info()
        for key, item in self._data.items():
            setattr(self, key, item)
        self.build_mine = base.build_mine
        self.build_tank = base.build_tank
        self.build_ship = base.build_ship
        self.build_jet = base.build_jet
        self.mine_cost = base.mine_cost
        self.get_distance = base.get_distance

    def __getitem__(self, key):
        return self._data[key]

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def cost(self, kind):
        if kind == "mine":
            return self.mine_cost()
        else:
            return config.cost[kind]


class Mine:
    def __init__(
        self, x: float, y: float, team: str, number: int, owner: Base, uid: str
    ):
        self.x = x
        self.y = y
        self.team = team
        self.number = number
        self.owner = owner
        self.health = config.health["mine"]
        self.attack = config.attack["mine"]
        self.kind = "mine"
        self.uid = uid

    def make_avatar(self):
        return
