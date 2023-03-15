# SPDX-License-Identifier: BSD-3-Clause

import datetime
import pyglet

from . import config


class Graphics:

    def __init__(self, engine):

        # self.game_map = game_map
        # self.nx = self.game_map.nx
        # self.ny = self.game_map.ny
        # self.ng = self.game_map.ng

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

        # self.time_label = pyglet.text.Label(f'Time left:',
        #                                     color=(255, 255, 255, 255),
        #                                     font_size=14,
        #                                     x=config.nx - 150,
        #                                     y=config.ny + 5,
        #                                     batch=self.main_batch)
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
                # pyglet.app.exit()
                self.engine.map_review_stage = False
            elif symbol == pyglet.window.key.N:
                self.engine.need_new_map = True
            # self.window.clear()
            # self.background.blit(0, 0)
            # self.main_batch.draw()


#     def update_time(self, time):
#         if self.time_label is not None:
#             self.time_label.delete()
#         t = str(datetime.timedelta(seconds=int(time)))[2:]
#         self.time_label = pyglet.text.Label(f'Time left: {t}',
#                                             color=(255, 255, 255, 255),
#                                             font_size=14,
#                                             x=config.nx - 150,
#                                             y=config.ny + 5,
#                                             batch=self.main_batch)

    def update_scoreboard(self, t, players):
        if self.scoreboard_label is not None:
            self.scoreboard_label.delete()
        t_str = str(datetime.timedelta(seconds=int(t)))[2:]
        # font_size = min(14, 100 / len(players))
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
