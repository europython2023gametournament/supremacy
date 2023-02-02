import numpy as np
import pyglet
import time

from .. import config
from .base import BaseProxy
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

    def generate_info(self):
        # st = time.time()
        info = {name: {} for name in self.players}
        for player in self.players.values():
            for base in player.bases:
                for n, p in self.players.items():
                    if not p.game_map[int(base.y):int(base.y) + 1,
                                      int(base.x):int(base.x) + 1].mask[0]:
                        if 'bases' not in info[n]:
                            info[n]['bases'] = []
                        info[n]['bases'].append(BaseProxy(base))
                    for group in ('tanks', 'ships', 'jets'):
                        for v in getattr(base, group).values():
                            if not p.game_map[int(v.y):int(v.y) + 1,
                                              int(v.x):int(v.x) + 1].mask[0]:
                                if group not in info[n]:
                                    info[n][group] = []
                                info[n][group].append(v.as_info())
        # print("time to generate info", time.time() - st)
        return info

    def init_dt(self, dt):
        for player in self.players.values():
            for base in player.bases:
                base.init_dt()
                base.crystal += dt * base.mines * 50

    def update(self, dt):
        t = time.time() - self.start_time
        if t > self.time_limit:
            pyglet.clock.unschedule(self.update)
            # raise RuntimeError('Time limit reached!')
        self.init_dt(dt)

        info = self.generate_info()

        for name, player in self.players.items():
            # for base in player.bases:
            #     base.crystal += dt * base.mines * 50
            # print(name, t, int(base.crystal), base.mines)
            player.execute_ai(t=t,
                              dt=dt,
                              info=info[name],
                              safe=False,
                              batch=self.graphics.main_batch)
            player.collect_transformed_ships()
        for name, player in self.players.items():
            for base in player.bases:
                for v in base.vehicles:
                    self.move(v, dt)
                    player.update_player_map(x=v.x, y=v.y)
