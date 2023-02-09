import numpy as np
import pyglet


class Graphics:

    def __init__(self, game_map):

        self.game_map = game_map
        self.nx = self.game_map.nx
        self.ny = self.game_map.ny
        self.ng = self.game_map.ng

        self.window = pyglet.window.Window(self.nx, self.ny)
        self.background = pyglet.resource.image('background.png')
        self.main_batch = pyglet.graphics.Batch()

        @self.window.event
        def on_draw():
            self.window.clear()
            self.background.blit(0, 0)
            self.main_batch.draw()
