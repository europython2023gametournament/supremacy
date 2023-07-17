# SPDX-License-Identifier: BSD-3-Clause

from typing import Any, List, Tuple
import os

import importlib_resources as ir
import numpy as np
import pyglet
from matplotlib import font_manager
import matplotlib.pyplot as plt
from PIL import Image, ImageFont, ImageDraw

MAX_HEALTH = 100


def _recenter_image(img: pyglet.image.ImageData) -> pyglet.image.ImageData:
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    return img


def scale_image(img: Image, scale: float) -> Image:
    return img.resize((int(img.width * scale), int(img.height * scale)))


def _to_image(img: Image) -> pyglet.image.ImageData:
    return _recenter_image(
        pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGBA",
            data=img.tobytes(),
            pitch=-img.width * 4,
        )
    )


def _make_base_image(resources: Any, name: str, rgb: Tuple[float, ...]) -> Image:
    img = Image.open(resources / f"{name}.png")
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = np.array(data).reshape(img.height, img.width, 4)
    for i in range(3):
        new_data[..., i] = int(round(rgb[i] * 255))
    return Image.fromarray(new_data.astype(np.uint8))


def _make_colors(num_colors: int) -> List[Tuple[float, ...]]:
    cols = []
    cmap = plt.get_cmap("gist_ncar")
    for i in range(num_colors):
        cols.append(cmap(i / (num_colors - 1)))
    return cols


class Config:
    def __init__(self):
        self.speed = {"tank": 10, "ship": 5, "jet": 20, "base": 0}
        self.health = {"tank": 50, "ship": 80, "jet": 50, "base": 100, "mine": 50}
        self.attack = {"tank": 20, "ship": 10, "jet": 30, "base": 0, "mine": 0}
        self.cost = {"tank": 500, "ship": 2000, "jet": 4000, "mine": 1000}
        self.view_radius = 20
        self.vehicle_offset = 5
        self.competing_mine_radius = 40
        self.fight_radius = 5
        self.scoreboard_width = 200
        self.taskbar_height = 60
        self.fps = 15
        self.resources = ir.files("supremacy") / "resources"
        self.cache_dir = ".cache"
        file = font_manager.findfont("sans")
        self.small_font = ImageFont.truetype(file, size=10)
        self.large_font = ImageFont.truetype(file, size=16)
        self.medium_font = ImageFont.truetype(file, size=12)

    def initialize(self, nplayers: int, fullscreen=False):
        dy = self.taskbar_height * (not fullscreen)
        ref_nx = 1920 - self.scoreboard_width
        ref_ny = 1080 - dy
        max_nx = 3840
        max_ny = 2160
        area = nplayers * (ref_nx * ref_ny) / 10
        ratio = ref_nx / ref_ny
        self.nx = min(max(int(np.sqrt(area * ratio)), ref_nx), max_nx)
        self.ny = min(max(int(np.sqrt(area / ratio)), ref_ny), max_ny)

        display = pyglet.canvas.Display()
        screen = display.get_default_screen()
        screen_width = screen.width - self.scoreboard_width
        screen_height = screen.height - dy
        self.scaling = min(min(screen_width / self.nx, screen_height / self.ny), 1.0)
        self.scaling_str = f"{self.scaling:.3f}"

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.generate_images(nplayers)

    def generate_images(self, nplayers: int):
        expl_fname = os.path.join(self.cache_dir, f"explosion_{self.scaling_str}.png")
        if os.path.exists(expl_fname):
            expl_img = Image.open(expl_fname)
        else:
            img = Image.open(self.resources / "explosion.png")
            expl_img = scale_image(img, self.scaling)
            expl_img.save(expl_fname)
        self.images = {"explosion": _to_image(expl_img)}
        self.colors = _make_colors(nplayers)
        for n in range(nplayers):
            rgb = self.colors[n]
            self.generate_vehicle_images(n, rgb)
            self.generate_base_images(n, rgb)
            self.generate_dead_images(n, rgb)

    def generate_vehicle_images(self, n: int, rgb: tuple):
        for name in ("jet", "ship", "tank"):
            for health in range(0, MAX_HEALTH + 1, 10):
                img_name = f"{name}_{n}_{health}"
                img_fname = os.path.join(
                    self.cache_dir, f"{img_name}_{self.scaling_str}.png"
                )
                if os.path.exists(img_fname):
                    img = Image.open(img_fname)
                else:
                    img = _make_base_image(self.resources, name, rgb)
                    d = ImageDraw.Draw(img)
                    d.text(
                        (img.width / 2, img.height / 2),
                        str(health),
                        fill=(0, 0, 0),
                        font=self.small_font,
                        anchor="mm",
                    )
                    img = scale_image(img, self.scaling)
                    img.save(img_fname)
                self.images[img_name] = _to_image(img)

    def generate_base_images(self, n: int, rgb: tuple):
        name = "base"
        player_img_name = f"player_{n}"
        player_img_fname = os.path.join(
            self.cache_dir, f"{player_img_name}_{self.scaling_str}.png"
        )
        if os.path.exists(player_img_fname):
            player_img = Image.open(player_img_fname)
        else:
            img = _make_base_image(self.resources, name, rgb)
            player_img = scale_image(img, self.scaling)
            player_img.save(player_img_fname)
        self.images[player_img_name] = player_img

        name_img_name = f"{name}_{n}"
        name_img_fname = os.path.join(
            self.cache_dir, f"{name_img_name}_{self.scaling_str}.png"
        )
        if os.path.exists(name_img_fname):
            name_img = Image.open(name_img_fname)
        else:
            img = _make_base_image(self.resources, name, rgb)
            name_img = scale_image(img, self.scaling)
            name_img.save(name_img_fname)
        self.images[name_img_name] = _to_image(name_img)

        name_c_img_name = f"{name}_{n}_C"
        name_c_img_fname = os.path.join(
            self.cache_dir, f"{name_c_img_name}_{self.scaling_str}.png"
        )
        if os.path.exists(name_c_img_fname):
            name_c_img = Image.open(name_c_img_fname)
        else:
            img = _make_base_image(self.resources, name, rgb)
            d = ImageDraw.Draw(img)
            d.text(
                (img.width / 2, img.height / 2),
                "C",
                fill=(0, 0, 0),
                font=self.large_font,
                anchor="mm",
            )
            name_c_img = scale_image(img, self.scaling)
            name_c_img.save(name_c_img_fname)
        self.images[name_c_img_name] = _to_image(name_c_img)

        for health in range(0, MAX_HEALTH + 1, 10):
            health_img_name = f"health_{health}"
            health_img_fname = os.path.join(
                self.cache_dir, f"{health_img_name}_{self.scaling_str}.png"
            )
            if os.path.exists(health_img_fname):
                health_img = Image.open(health_img_fname)
            else:
                img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
                d = ImageDraw.Draw(img)
                d.text(
                    (img.width / 2, img.height / 2),
                    f"{health}",
                    fill=(0, 0, 0),
                    font=self.medium_font,
                    anchor="mm",
                )
                health_img = scale_image(img, self.scaling)
                health_img.save(health_img_fname)
            self.images[health_img_name] = _to_image(health_img)
        for mines in range(0, 20):
            mine_img_name = f"mines_{mines}"
            mine_img_fname = os.path.join(
                self.cache_dir, f"{mine_img_name}_{self.scaling_str}.png"
            )
            if os.path.exists(mine_img_fname):
                mine_img = Image.open(mine_img_fname)
            else:
                img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
                d = ImageDraw.Draw(img)
                d.text(
                    (img.width / 2, img.height / 2),
                    f"[{mines}]",
                    fill=(0, 0, 0),
                    font=self.medium_font,
                    anchor="mm",
                )
                mine_img = scale_image(img, self.scaling)
                mine_img.save(mine_img_fname)
            self.images[mine_img_name] = _to_image(mine_img)

    def generate_dead_images(self, n: int, rgb: tuple):
        name = "cross"
        cross_img_name = f"{name}_{n}"
        cross_img_fname = os.path.join(
            self.cache_dir, f"{cross_img_name}_{self.scaling_str}.png"
        )
        if os.path.exists(cross_img_fname):
            cross_img = Image.open(cross_img_fname)
        else:
            cross_img = scale_image(
                _make_base_image(self.resources, name, rgb), self.scaling
            )
        self.images[cross_img_name] = cross_img
