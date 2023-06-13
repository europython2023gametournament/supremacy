# SPDX-License-Identifier: BSD-3-Clause

import datetime
from typing import Any

import pyglet

from . import config
from .tools import text_to_image


class Graphics:
    def __init__(self, engine: Any, fullscreen: bool):
        self.engine = engine

        self.window = pyglet.window.Window(
            int((config.nx + config.scoreboard_width) * config.scaling),
            int((config.ny) * config.scaling),
            caption="Supremacy",
            fullscreen=fullscreen,
            resizable=not fullscreen,
        )

        self.background = self.engine.game_map.background_image.get_texture()
        self.main_batch = pyglet.graphics.Batch()
        self.time_label = pyglet.sprite.Sprite(
            img=text_to_image("Time left:", width=100, height=24, scale=False),
            x=(config.nx + 20) * config.scaling,
            y=(config.ny - 50) * config.scaling,
            batch=self.main_batch,
        )
        self.time_left = None

        self.map_review_label = None
        if not self.engine.test:
            self.map_review_label = pyglet.text.Label(
                "Map review stage [Y/N]?",
                color=(255, 255, 255, 255),
                font_size=14,
                x=config.nx * 0.4,
                y=config.ny + 5,
                batch=self.main_batch,
            )

        self.scoreboard_labels = []

        @self.window.event
        def on_draw():
            self.window.clear()
            self.background.blit(0, 0)
            self.main_batch.draw()

        @self.window.event
        def on_key_release(symbol, modifiers):
            if symbol == pyglet.window.key.Y:
                self.engine.map_review_stage = False
                if self.map_review_label is not None:
                    self.map_review_label.delete()
            elif symbol == pyglet.window.key.N:
                self.engine.need_new_map = True
            elif symbol == pyglet.window.key.P:
                self.engine.paused = not self.engine.paused

    def update_scoreboard(self, t: float):
        if self.time_left is not None:
            self.time_left.delete()
        t_str = str(datetime.timedelta(seconds=int(t)))[2:]
        self.time_left = pyglet.sprite.Sprite(
            img=text_to_image(t_str, width=100, height=24, scale=False),
            x=(config.nx + 100) * config.scaling,
            y=(config.ny - 50) * config.scaling,
            batch=self.main_batch,
        )
