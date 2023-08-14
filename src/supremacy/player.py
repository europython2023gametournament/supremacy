# SPDX-License-Identifier: BSD-3-Clause

import uuid
from itertools import chain
from typing import Any, Iterator, Tuple

import numpy as np
from PIL import Image
import pyglet

from . import config
from .base import Base
from .game_map import MapView
from .tools import text_to_raw_image


class Player:
    def __init__(
        self,
        ai: Any,
        location: Tuple[int, int],
        number: int,
        team: str,
        batch: Any,
        game_map: np.ndarray,
        score: int,
        base_locations: np.ndarray,
        high_contrast: bool = False,
    ):
        self.ai = ai
        self.ai.team = team
        self.hq = location
        self.number = number
        self.team = team
        self.batch = batch
        self.base_locations = base_locations
        self.original_map_array = game_map
        self.game_map = MapView(np.full_like(game_map, -1))
        self.dead = False
        self.bases = {}
        self.tanks = {}
        self.ships = {}
        self.jets = {}
        self.global_score = score
        self.score_this_round = 0
        self.high_contrast = high_contrast
        self.build_base(x=location[0], y=location[1])
        self.transformed_ships = []
        self.label = None
        self.animate_cross = 0
        self.score_position = self.number
        self.avatar = None
        self.make_avatar_base_image()

    def update_player_map(self, x: float, y: float):
        r = config.view_radius
        slices = self.game_map.view_slices(x=x, y=y, dx=r, dy=r)
        for s in slices:
            self.game_map.array[s[0], s[1]] = self.original_map_array[s[0], s[1]]

    def build_base(self, x: float, y: float):
        uid = uuid.uuid4().hex
        self.bases[uid] = Base(
            x=x,
            y=y,
            team=self.team,
            number=self.number,
            batch=self.batch,
            owner=self,
            uid=uid,
            high_contrast=self.high_contrast,
        )
        self.base_locations[int(y), int(x)] = 1
        return uid

    def init_dt(self):
        self.transformed_ships.clear()

    def execute_ai(self, t: float, dt: float, info: dict, safe: bool = False):
        if safe:
            try:
                self.ai.run(t=t, dt=dt, info=info, game_map=self.game_map.array)
            except:
                pass
        else:
            self.ai.run(t=t, dt=dt, info=info, game_map=self.game_map.array)

    def collect_transformed_ships(self):
        for uid in self.transformed_ships:
            del self.ships[uid]

    @property
    def children(self) -> Iterator:
        """
        All the players's vehicles, bases and mines
        """
        mines = [base.mines.values() for base in self.bases.values()]
        return chain(self.army, *mines)

    @property
    def vehicles(self) -> Iterator:
        """
        All the players's vehicles
        """
        return chain(self.tanks.values(), self.ships.values(), self.jets.values())

    @property
    def army(self) -> Iterator:
        """
        All the players's vehicles and bases
        """
        return chain(self.bases.values(), self.vehicles)

    def remove(self, uid: str):
        if uid in self.tanks:
            self.tanks[uid].delete()
            del self.tanks[uid]
        elif uid in self.ships:
            self.ships[uid].delete()
            del self.ships[uid]
        elif uid in self.jets:
            self.jets[uid].delete()
            del self.jets[uid]
        else:
            for base in self.bases.values():
                if uid in base.mines:
                    del base.mines[uid]
                    base.make_avatar()

    def remove_base(self, uid: str):
        self.bases[uid].delete()
        del self.bases[uid]

    def economy(self) -> int:
        return int(sum([base.crystal for base in self.bases.values()]))

    def make_avatar_base_image(self):
        self.avatar_base_image = Image.new("RGBA", (100, 24), (0, 0, 0, 0))
        key = "skull" if self.dead else "player"
        self.avatar_base_image.paste(config.images[f"{key}_{self.number}"], (0, 0))
        self.avatar_base_image.paste(
            text_to_raw_image(
                self.team[:10], width=70, height=24, font=config.medium_font
            ),
            (30, 0),
        )

    def update_score(self, score: int):
        self.score_this_round += score
        self.global_score += score

    def make_avatar(self, ind):
        self.score_position = ind
        img = Image.new("RGBA", (200, 24), (0, 0, 0, 0))
        img.paste(self.avatar_base_image, (0, 0))
        img.paste(
            text_to_raw_image(
                f"  {'  ' if self.score_position < 9 else ''}"
                f"{self.score_position + 1}.   "
                f"{self.global_score}[{self.score_this_round}]",
                width=100,
                height=24,
                font=config.medium_font,
            ),
            (100, 0),
        )

        imd = pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGBA",
            data=img.tobytes(),
            pitch=-img.width * 4,
        )
        if self.avatar is not None:
            self.avatar.delete()
        self.avatar = pyglet.sprite.Sprite(
            img=imd,
            x=(config.nx * config.scaling) + 4,
            y=(config.ny * config.scaling) - 100 - 35 * self.score_position,
            batch=self.batch,
        )

    def rip(self):
        for v in self.vehicles:
            v.delete()
        self.tanks.clear()
        self.ships.clear()
        self.jets.clear()
        self.dead = True
        self.make_avatar_base_image()

    def dump_map(self):
        im = Image.fromarray(
            np.flipud((self.game_map.array.astype(np.uint8) + 1) * 127)
        )
        im.save(f"{self.team}_map.png")

    def init_cross_animation(self):
        self.animate_cross = 8
        self.cross_x = np.linspace(
            self.avatar.x, (config.nx / 2) * config.scaling, self.animate_cross
        )
        self.cross_y = np.linspace(
            self.avatar.y, (config.ny / 2) * config.scaling, self.animate_cross
        )
        self.cross_s = np.linspace(1, 30, self.animate_cross)
        self.cross_o = [255] + ([128] * (self.animate_cross - 1))
        ind = self.animate_cross - 1
        self.avatar.x = self.cross_x[ind]
        self.avatar.y = self.cross_y[ind]
        self.avatar.opacity = self.cross_o[ind]
        self.avatar.scale = self.cross_s[ind]

    def cross_animate(self):
        self.animate_cross -= 1
        self.avatar.x = self.cross_x[self.animate_cross]
        self.avatar.y = self.cross_y[self.animate_cross]
        self.avatar.scale = self.cross_s[self.animate_cross]
        self.avatar.opacity = self.cross_o[self.animate_cross]
