# SPDX-License-Identifier: BSD-3-Clause

from typing import Any, Optional

import importlib_resources as ir
import numpy as np
import pyglet
from matplotlib import colors, font_manager
from PIL import Image, ImageFont, ImageDraw

MAX_HEALTH = 100


def _recenter_image(img: Any) -> Any:
    img.anchor_x = img.width // 2
    img.anchor_y = img.height // 2
    return img


def _to_image(img: Any) -> Any:
    # img.anchor_x = img.width // 2
    # img.anchor_y = img.height // 2
    # img = _recenter_image(img)
    # print(img.width, img.anchor_x)
    # print(img.height, img.anchor_y)
    return _recenter_image(
        pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGBA",
            data=img.tobytes(),
            pitch=-img.width * 4,
        )
    )


def _make_base_image(resources: Any, name: str, rgb: tuple) -> Image:
    img = Image.open(resources / f"{name}.png")
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = np.array(data).reshape(img.height, img.width, 4)
    for i in range(3):
        new_data[..., i] = int(round(rgb[i] * 255))
    return Image.fromarray(new_data.astype(np.uint8))


def _make_color(number):
    hue = number * 137.508
    return colors.hsv_to_rgb([(hue % 360) / 360, 0.5, 0.75])


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
        f = 1.2
        self.nx = int(1920 * f)
        self.ny = int(1080 * f)  # int(992 * f)
        self.scoreboard_width = 200
        self.fps = 15
        self.resources = ir.files("supremacy") / "resources"
        img = _recenter_image(pyglet.image.load(self.resources / "explosion.png"))
        self.images = {"explosion": img}
        file = font_manager.findfont("sans")
        self.small_font = ImageFont.truetype(file, size=10)
        self.large_font = ImageFont.truetype(file, size=14)

    def generate_images(self, nplayers: int):
        for n in range(nplayers):
            self.generate_vehicle_images(n)
            self.generate_base_images(n)
            self.generate_dead_images(n)

    def generate_vehicle_images(self, n: int):
        # rgb = colors.to_rgb(f"C{n}")
        rgb = _make_color(n)
        for name in ("jet", "ship", "tank"):
            # print(name)
            # img = Image.open(self.resources / f"{name}.png")
            # img = img.convert("RGBA")
            # data = img.getdata()
            # new_data = np.array(data).reshape(img.height, img.width, 4)
            # for i in range(3):
            #     new_data[..., i] = int(round(rgb[i] * 255))
            for health in range(0, MAX_HEALTH + 1, 10):
                # temp_image = Image.fromarray(new_data.astype(np.uint8))
                img = _make_base_image(self.resources, name, rgb)
                d = ImageDraw.Draw(img)
                d.text(
                    (img.width / 2, img.height / 2),
                    str(health),
                    fill=(0, 0, 0),
                    font=self.small_font,
                    anchor="mm",
                )
                self.images[f"{name}_{n}_{health}"] = _to_image(img)

    def generate_base_images(self, n: int):
        # rgb = colors.to_rgb(f"C{n}")
        rgb = _make_color(n)
        name = "base"
        # img = Image.open(self.resources / f"{name}.png")
        # img = img.convert("RGBA")
        # data = img.getdata()
        # new_data = np.array(data).reshape(img.height, img.width, 4)
        # for i in range(3):
        #     new_data[..., i] = int(round(rgb[i] * 255))
        img = _make_base_image(self.resources, name, rgb)
        self.images[f"player_{n}"] = img
        self.images[f"{name}_{n}"] = _to_image(img)

        for health in range(0, MAX_HEALTH + 1, 10):
            # img = _make_base_image(self.resources, name, rgb)
            img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
            # self.images[f"{name}_{n}"] = _to_image(temp_image)
            # temp_image = Image.fromarray(new_data.astype(np.uint8))
            d = ImageDraw.Draw(img)
            d.text(
                (img.width / 2, img.height / 2),
                f"{health}",
                fill=(0, 0, 0),
                font=self.small_font,
                anchor="mm",
            )
            self.images[f"health_{health}"] = _to_image(img)
        for mines in range(0, 20):
            # img = _make_base_image(self.resources, name, rgb)
            img = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            d.text(
                (img.width / 2, img.height / 2),
                f"[{mines}]",
                fill=(0, 0, 0),
                font=self.small_font,
                anchor="mm",
            )
            self.images[f"mines_{mines}"] = _to_image(img)

    def generate_dead_images(self, n: int):
        # rgb = colors.to_rgb(f"C{n}")
        rgb = _make_color(n)
        name = "cross"
        # img = _make_base_image(self.resources, name, rgb)
        self.images[f"{name}_{n}"] = _make_base_image(self.resources, name, rgb)
