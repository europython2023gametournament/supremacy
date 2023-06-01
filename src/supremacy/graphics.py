# SPDX-License-Identifier: BSD-3-Clause

import datetime
from typing import Any


import pyglet

from PIL import Image, ImageDraw

# from OpenGL.GL import *
# from OpenGL.GLU import *
# from OpenGL.GLUT import *


from . import config
from .tools import text_to_image


# # The game window
# class Window(pyglet.window.Window):
#     def __init__(self, *args, **kwargs):
#         super(Window, self).__init__(*args, vsync=False, **kwargs)
#         # Run "self.update" 128 frames a second and set FPS limit to 128.
#         pyglet.clock.schedule_interval(self.update, 1.0 / config.fps)
#         pyglet.clock.set_fps_limit(config.fps)

#     # You need the dt argument there to prevent errors,
#     # it does nothing as far as I know.
#     def update(self, dt):
#         pass

#     def on_draw(self):
#         pyglet.clock.tick()  # Make sure you tick the clock!
#         self.clear()
#         # fps.draw()


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
        self.redraw = True
        # pyglet.clock.set_fps_limit(config.fps)
        # self.window = Window(
        #     config.nx + config.scoreboard_width,
        #     config.ny,
        #     caption="Supremacy",
        #     fullscreen=False,
        #     resizable=True,
        # )
        # self.background = pyglet.resource.image("background.png")
        # print(self.background)
        # print(self.background)

        self.background = self.engine.game_map.background_image.get_texture()
        self.main_batch = pyglet.graphics.Batch()

        # self.background = pyglet.sprite.Sprite(
        #     img=self.engine.game_map.background_image,
        #     x=0,
        #     y=0,
        #     batch=self.main_batch,
        # )

        self.time_label = pyglet.sprite.Sprite(
            img=text_to_image("Time left:", width=100, height=24),
            x=config.nx + 20,
            y=config.ny - 50,
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
            # if self.redraw:
            self.window.clear()
            self.background.blit(0, 0)
            self.main_batch.draw()
            # self.redraw = False

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
        if self.time_left is not None:
            self.time_left.delete()
        t_str = str(datetime.timedelta(seconds=int(t)))[2:]
        self.time_left = pyglet.sprite.Sprite(
            img=text_to_image(t_str, width=100, height=24),
            x=config.nx + 100,
            y=config.ny - 50,
            batch=self.main_batch,
        )
