import numpy as np
import pyglet
import time
import os

from .. import config
from .base import BaseProxy
from .game_map import GameMap
from .graphics import Graphics
from .player import Player
from .vehicles import VehicleProxy

from .. import config


class Engine:

    def __init__(self, players: list, speedup: int = 1):

        config.generate_images(nplayers=len(players))

        self.ng = config.ng
        self.nx = config.nx
        self.ny = config.ny
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
        self.scores = {}
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
        self.time_limit = 4 * 60  # 5 * 60
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
        for name, player in self.players.items():
            for base in player.bases.values():
                for n, p in self.players.items():
                    if not p.game_map[int(base.y):int(base.y) + 1,
                                      int(base.x):int(base.x) + 1].mask[0]:
                        if name not in info[n]:
                            info[n][name] = {}
                        if 'bases' not in info[n][name]:
                            info[n][name]['bases'] = []
                        info[n][name]['bases'].append(
                            BaseProxy(base) if name == n else base.as_info())
                    for group in ('tanks', 'ships', 'jets'):
                        for v in getattr(base, group).values():
                            if not p.game_map[int(v.y):int(v.y) + 1,
                                              int(v.x):int(v.x) + 1].mask[0]:
                                if name not in info[n]:
                                    info[n][name] = {}
                                if group not in info[n][name]:
                                    info[n][name][group] = []
                                info[n][name][group].append(
                                    VehicleProxy(v) if name == n else v.as_info())
        # print("time to generate info", time.time() - st)
        # print(info)
        # assert False
        return info

    def init_dt(self, dt):
        for player in self.players.values():
            for base in player.bases.values():
                base.init_dt(dt)
                base.crystal += dt * len(base.mines) * 50

    def fight(self, t):
        cooldown = 1
        combats = {}
        dead = {}
        for name, player in self.players.items():
            for base in player.bases.values():
                igrid = int(base.x) // self.game_map.ng
                jgrid = int(base.y) // self.game_map.ng
                key = f'{igrid},{jgrid}'
                li = [base] + list(base.mines.values())
                if key not in combats:
                    combats[key] = {name: li}
                elif name not in combats[key]:
                    combats[key][name] = li
                else:
                    combats[key][name] += li

                for v in base.vehicles:
                    igrid = int(v.x) // self.game_map.ng
                    jgrid = int(v.y) // self.game_map.ng
                    key = f'{igrid},{jgrid}'
                    if key not in combats:
                        combats[key] = {name: [v]}
                    elif name not in combats[key]:
                        combats[key][name] = [v]
                    else:
                        combats[key][name].append(v)
        for c in combats.values():
            if len(c) > 1:
                keys = list(c.keys())
                for name in keys:
                    for team in set(keys) - {name}:
                        for attacker in c[name]:
                            # if attacker.cooldown == 0:
                            #     attacker.cooldown = cooldown
                            for defender in c[team]:
                                defender.health -= attacker.attack
                                # if defender.kind in ('mine', 'base'):
                                # print(c[team], defender.health)
                                defender.make_label()
                                if defender.health <= 0:
                                    if team not in dead:
                                        dead[team] = {}
                                    owner = (defender if defender.kind == 'base' else
                                             defender.owner)
                                    if owner.uid not in dead[team]:
                                        dead[team][owner.uid] = []
                                    dead[team][owner.uid].append(defender.uid)
                                    if defender.kind == 'base':
                                        attacker.owner.owner.score += 2
                                    # if defender.kind not in dead[team][owner.uid]:
                                    #     dead[team][owner.uid][defender.kind] = [
                                    #         defender.uid
                                    #     ]
                                    # else:
                                    #     dead[team][owner.uid][defender.kind].append(
                                    #         defender.uid)

            # if set(combats[key]) == {'blue', 'red'}:
            #     blue_attack = sum(
            #         [k.attack if k.cooldown == 0 else 0 for k in combats[key]['blue']])
            #     red_attack = sum(
            #         [k.attack if k.cooldown == 0 else 0 for k in combats[key]['red']])
            #     for k in combats[key]['blue']:
            #         k.health = max(
            #             0, k.health - int(red_attack / len(combats[key]['blue'])))
            #         if k.health <= 0:
            #             dead.append(k)
            #         if k.cooldown == 0:
            #             k.cooldown = cooldown
            #     for k in combats[key]['red']:
            #         k.health = max(
            #             0, k.health - int(blue_attack / len(combats[key]['red'])))
            #         if k.health <= 0:
            #             dead.append(k)
            #         if k.cooldown == 0:
            #             k.cooldown = cooldown
        return dead

    def exit(self):
        print("Time limit reached!")
        pyglet.clock.unschedule(self.update)
        # event_loop = pyglet.app.EventLoop()
        # event_loop.exit()
        pyglet.app.exit()
        score_left = len(self.scores)
        for name, p in self.players.items():
            self.scores[name] = p.score + score_left
        fname = 'scores.txt'
        if os.path.exists(fname):
            with open(fname, 'r') as f:
                contents = f.readlines()
            for line in contents:
                name, score = line.split(':')
                self.scores[name] += int(score.strip())
        with open(fname, 'w') as f:
            for name, score in self.scores.items():
                f.write(f'{name}: {score}\n')
        sorted_scores = [
            (k, v)
            for k, v in sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        ]
        for i, (name, score) in enumerate(sorted_scores):
            print(f'{i + 1}. {name}: {score}')

        input()

    def update(self, dt):
        t = time.time() - self.start_time
        if t > self.time_limit:
            self.exit()
            # pyglet.clock.unschedule(self.update)
            # raise RuntimeError('Time limit reached!')
        self.init_dt(dt)

        info = self.generate_info()

        for name, player in self.players.items():
            # for base in player.bases:
            #     base.crystal += dt * base.mines * 50
            # print(name, t, int(base.crystal), base.mines)
            player.execute_ai(t=t, dt=dt, info=info[name], safe=False)
            player.collect_transformed_ships()
        for name, player in self.players.items():
            for base in player.bases.values():
                for v in base.vehicles:
                    self.move(v, dt)
                    player.update_player_map(x=v.x, y=v.y)

        dead = self.fight(t)
        for name in dead:
            for baseid, idlist in dead[name].items():
                for uid in idlist:
                    self.players[name].bases[baseid].remove(uid)
            if len(self.players[name].bases) == 0:
                print(f'Player {name} died!')
                self.scores[name] = self.players[name].score + len(self.scores)
                del self.players[name]
