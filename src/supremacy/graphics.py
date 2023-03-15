# SPDX-License-Identifier: BSD-3-Clause

import datetime
import pyglet

from . import config


class Graphics:

    def __init__(self, engine):

        self.window = pyglet.window.Window(config.nx,
                                           config.ny + 32,
                                           caption='Supremacy')
        self.background = pyglet.resource.image('background.png')
        self.main_batch = pyglet.graphics.Batch()

        self.economy_label = pyglet.text.Label('Economy [score]:',
                                               color=(255, 255, 255, 255),
                                               font_size=14,
                                               x=10,
                                               y=config.ny + 5,
                                               batch=self.main_batch)

        self.engine = engine

        self.scoreboard_label = None

        @self.window.event
        def on_draw():
            self.window.clear()
            self.background.blit(0, 0)
            self.main_batch.draw()

        @self.window.event
        def on_key_release(symbol, modifiers):
            if symbol == pyglet.window.key.Y:
                self.engine.map_review_stage = False
            elif symbol == pyglet.window.key.N:
                self.engine.need_new_map = True

    def update_scoreboard(self, t, players):
        if self.scoreboard_label is not None:
            self.scoreboard_label.delete()
        t_str = str(datetime.timedelta(seconds=int(t)))[2:]
        p_str = [f'{name}: {value}'.ljust(20) for name, value in players.items()]
        if len(players) <= 5:
            nspaces = 9
            font_size = 14
        elif len(players) <= 10:
            nspaces = 0
            font_size = 10
        else:
            nspaces = 0
            font_size = 8
        text = (' ' * nspaces).join(p_str + ['Time: ' + t_str])
        self.scoreboard_label = pyglet.text.Label(text,
                                                  color=(255, 255, 255, 255),
                                                  font_name='monospace',
                                                  font_size=font_size,
                                                  x=200,
                                                  y=config.ny + 5,
                                                  batch=self.main_batch)
