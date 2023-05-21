# SPDX-License-Identifier: BSD-3-Clause

import datetime
from typing import Any


import pyglet

from PIL import Image, ImageDraw

# from OpenGL.GL import *
# from OpenGL.GLU import *
# from OpenGL.GLUT import *


from . import config


class Graphics:
    def __init__(self, engine: Any):
        self.engine = engine

        self.window = pyglet.window.Window(
            config.nx + config.scoreboard_width,
            config.ny,
            caption="Supremacy",
            fullscreen=False,
            resizable=True,
        )
        # self.window.flip()
        # glScalef(0.5, 0.5, 1.0)
        self.background = pyglet.resource.image("background.png")
        self.main_batch = pyglet.graphics.Batch()

        # self.economy_label = pyglet.text.Label(
        #     "Economy [score]:",
        #     color=(255, 255, 255, 255),
        #     font_size=14,
        #     x=10,
        #     y=config.ny + 5,
        #     batch=self.main_batch,
        # )

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

        self.scoreboard_label = None

        @self.window.event
        def on_draw():
            self.window.clear()
            self.background.blit(0, 0)
            self.main_batch.draw()

        # @self.window.event
        # def on_key_release(symbol, modifiers):
        #     if symbol == pyglet.window.key.Y:
        #         self.engine.map_review_stage = False
        #         if self.map_review_label is not None:
        #             self.map_review_label.delete()
        #     elif symbol == pyglet.window.key.N:
        #         self.engine.need_new_map = True
        #     elif symbol == pyglet.window.key.P:
        #         self.engine.paused = not self.engine.paused

    def update_scoreboard(self, t: float):
        return
        if self.scoreboard_label is not None:
            self.scoreboard_label.delete()
        # t_str = str(datetime.timedelta(seconds=int(t)))[2:]
        # # p_str = [f"{name}: {value}" for name, value in players.items()]
        # # if len(players) <= 5:
        # #     nspaces = 3
        # #     font_size = 14
        # # elif len(players) <= 10:
        # #     nspaces = 0
        # #     font_size = 10
        # # else:
        # #     nspaces = 0
        # #     font_size = 8
        # # text = (" " * nspaces).join(p_str + ["Time: " + t_str])
        # # font_size
        # # text = "\n".join(p_str)
        # self.scoreboard_label = pyglet.text.Label(
        #     t_str,
        #     color=(255, 255, 255, 255),
        #     font_name="monospace",
        #     font_size=14,
        #     x=config.nx + 10,
        #     y=10,
        #     anchor_x="left",
        #     batch=self.main_batch,
        # )

        img = Image.new("RGBA", (200, 1000), (0, 0, 0, 0))
        # d = ImageDraw.Draw(img)
        # d.text(
        #     (0, 0),
        #     f"{self.economy()}[{self.score}]",
        #     fill=(255, 255, 255),
        #     font=config.large_font,
        # )
        imdata = pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGBA",
            data=img.tobytes(),
            pitch=-img.width * 4,
        )
        self.scoreboard_label = pyglet.sprite.Sprite(
            img=imdata,
            x=config.nx,
            y=0,
            batch=self.main_batch,
        )

        # document = pyglet.text.decode_text("Hello, \n world.")
        # self.scoreboard_label = pyglet.text.layout.TextLayout(
        #     document,
        #     200,
        #     500,
        #     multiline=True,
        #     x=100,  # config.nx,
        #     y=100,  # config.ny,
        #     anchor_y="top",
        #     batch=self.main_batch,
        # )

        # self.scoreboard_label = pyglet.text.HTMLLabel(
        #     '<span style="color: white;">Hello, <i><br>world</i></span>',
        #     x=100,  # config.nx,
        #     y=100,  # config.ny,
        #     anchor_y="top",
        #     batch=self.main_batch,
        # )
