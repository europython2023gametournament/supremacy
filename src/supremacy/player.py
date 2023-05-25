# SPDX-License-Identifier: BSD-3-Clause

import uuid
from itertools import chain
from typing import Any, Iterator, Tuple

import numpy as np
from PIL import Image, ImageDraw
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
        nplayers: int,
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
        self.animate_skull = 0
        # if nplayers <= 5:
        #     dx = 250
        # elif nplayers <= 10:
        #     dx = 160
        # else:
        #     dx = 120
        dy = 50
        self.score_position = self.number

        # image1_size = image1.size
        # image2_size = image2.size
        # new_image = Image.new('RGB',(2*image1_size[0], image1_size[1]), (250,250,250))
        # new_image.paste(image1,(0,0))
        # new_image.paste(image2,(image1_size[0],0))
        # self.avatar_base_image = Image.new("RGBA", (100, 24), (0, 0, 0, 0))
        # self.avatar_base_image.paste(config.images[f"player_{self.number}"], (0, 0))
        # self.avatar_base_image.paste(
        #     text_to_raw_image(self.team, width=70, height=24), (30, 0)
        # )
        self.avatar = None
        self.make_avatar_base_image()
        self.make_avatar()
        # self.avatar = pyglet.sprite.Sprite(
        #     img=config.images[f"base_{self.number}"],
        #     x=config.nx + 10,
        #     y=config.ny - (dy * (self.number + 1)),
        #     batch=self.batch,
        # )
        # img = text_to_image(self.team, width=80, height=20)
        # img.anchor_y = img.height // 2
        # self.name_label = pyglet.sprite.Sprite(
        #     img=img,
        #     x=self.avatar.x + 20,
        #     y=self.avatar.y,
        #     batch=self.batch,
        # )

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
        key = "cross" if self.dead else "player"
        self.avatar_base_image.paste(config.images[f"{key}_{self.number}"], (0, 0))
        self.avatar_base_image.paste(
            text_to_raw_image(self.team, width=70, height=24), (30, 0)
        )

    def update_score(self, score: int):
        self.score_this_round += score
        self.global_score += score

    def make_avatar(self, ind=None):
        if ind is not None:
            self.score_position = ind
        img = Image.new("RGBA", (200, 24), (0, 0, 0, 0))
        img.paste(self.avatar_base_image, (0, 0))
        img.paste(
            text_to_raw_image(
                f"{self.score_position + 1}. {self.global_score}[{self.score_this_round}]",
                width=100,
                height=24,
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
            x=config.nx + 10,
            y=config.ny - 50 - 50 * self.score_position,
            batch=self.batch,
        )

    def make_label(self) -> str:
        # return
        return f"{self.economy()}[{self.score}]"
        # if self.label is not None:
        #     self.label.delete()
        img = Image.new("RGBA", (200, 20), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text(
            (0, 0),
            f"{self.economy()}[{self.score}]",
            fill=(255, 255, 255),
            font=config.large_font,
        )
        imdata = pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGBA",
            data=img.tobytes(),
            pitch=-img.width * 4,
        )
        self.label = pyglet.sprite.Sprite(
            img=imdata,
            x=self.avatar.x + 10,
            y=self.avatar.y,
            batch=self.batch,
        )
        # self.label = pyglet.text.Label(
        #     f"{self.economy()}[{self.score}]",
        #     color=(255, 255, 255, 255),
        #     font_name="monospace",
        #     font_size=14,
        #     x=config.nx + 10,
        #     y=self.avatar.y - 10,
        #     anchor_x="left",
        #     batch=self.batch,
        # )

    def rip(self):
        for v in self.vehicles:
            v.delete()
        self.tanks.clear()
        self.ships.clear()
        self.jets.clear()
        # avx = self.avatar.x
        # avy = self.avatar.y
        # self.avatar.delete()
        # self.avatar = pyglet.sprite.Sprite(
        #     img=config.images[f"cross_{self.number}"], x=avx, y=avy, batch=self.batch
        # )

        self.dead = True
        self.make_avatar_base_image()
        # self.make_avatar()
        # self.init_skull_animation()

    def dump_map(self):
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(15, 9))
        ax.imshow(self.game_map.array, origin="lower", aspect="equal")
        fig.savefig(f"{self.team}_map.png", bbox_inches="tight")

    def init_skull_animation(self):
        self.animate_skull = 10
        self.skull_x = np.linspace(self.avatar.x, config.nx / 2, self.animate_skull)
        self.skull_y = np.linspace(self.avatar.y, config.ny / 2, self.animate_skull)
        self.skull_s = np.linspace(1, 30, self.animate_skull)
        self.skull_o = [255] + ([128] * (self.animate_skull - 1))
        ind = self.animate_skull - 1
        self.avatar.x = self.skull_x[ind]
        self.avatar.y = self.skull_y[ind]
        self.avatar.opacity = self.skull_o[ind]
        self.avatar.scale = self.skull_s[ind]

    def skull_animate(self):
        self.animate_skull -= 1
        self.avatar.x = self.skull_x[self.animate_skull]
        self.avatar.y = self.skull_y[self.animate_skull]
        self.avatar.scale = self.skull_s[self.animate_skull]
        self.avatar.opacity = self.skull_o[self.animate_skull]
