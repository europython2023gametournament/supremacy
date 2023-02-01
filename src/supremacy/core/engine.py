import numpy as np
import pyglet
import time

from .. import config
from .game_map import GameMap
from .graphics import Graphics
from .player import Player


class Engine:

    def __init__(self, players: list, speedup: int = 1):

        config.generate_images(nplayers=len(players))

        self.ng = 4
        self.nx = self.ng * 475
        self.ny = self.ng * 250
        self.speedup = speedup
        self.game_map = GameMap(nx=self.nx, ny=self.ny, ng=self.ng)
        self.graphics = Graphics(game_map=self.game_map)

        player_locations = self.game_map.add_players(players=players)
        self.players = {
            p.creator: Player(ai=p,
                              location=player_locations[p.creator],
                              number=i,
                              team=p.creator,
                              batch=self.graphics.main_batch,
                              game_map=np.ma.masked_where(True, self.game_map.array))
            for i, p in enumerate(players)
        }
        # self.graphics = Graphics(game_map=self.game_map, players=self.players)

    def move(self, vehicle, dt):
        pos = vehicle.ray_trace(dt=dt)
        # above_xmin = np.amin(pos[0]) >= 0
        # below_xmax = np.amax(pos[0]) < self.map.nx
        # above_ymin = np.amin(pos[1]) >= 0
        # below_ymax = np.amax(pos[1]) < self.map.ny
        xpos = np.mod(pos[0], self.nx - 1)
        ypos = np.mod(pos[1], self.ny - 1)
        # no_obstacles = (np.sum(self.map.array[(xpos, ypos)] == 1)) == 0
        path = self.game_map.array[(ypos, xpos)]
        vehicle.move(dt=dt, path=path, nx=self.nx, ny=self.ny)

    def run(self, safe: bool = False, fps=30):

        t = 0
        self.time_limit = 2 * 60  # 5 * 60
        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 1 / fps)

        pyglet.app.run()

        # dt = 1. / fps
        # start_time = time.time()
        # frame_times = np.linspace(dt, self.time_limit, int(self.time_limit / dt))
        # dt *= self.speedup
        # frame = 0
        # while t < self.time_limit:
        #     t = (time.time() - start_time) * self.speedup
        #     if (frame < len(frame_times)) and (t >= frame_times[frame]):

    def update(self, dt):
        t = time.time() - self.start_time
        if t > self.time_limit:
            raise RuntimeError('Time limit reached!')
        for name, player in self.players.items():
            for base in player.bases:
                base.crystal += dt * base.mines * 50
                # print(name, t, int(base.crystal), base.mines)
            player.execute_ai(t=t,
                              dt=dt,
                              info={'bases': player.bases},
                              safe=False,
                              batch=self.graphics.main_batch)
            player.collect_transformed_ships()
        for name, player in self.players.items():
            for base in player.bases:
                for v in base.vehicles:
                    self.move(v, dt)
