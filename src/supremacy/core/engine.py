# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import pyglet
import time
import os

from .. import config
from .base import BaseProxy
from .fight import fight
from .game_map import GameMap, MapView
from .graphics import Graphics
from .player import Player
from .tools import ReadOnly
from .vehicles import VehicleProxy


class Engine:

    def __init__(self,
                 players: list,
                 safe=False,
                 high_contrast=False,
                 test=True,
                 time_limit=300):

        config.generate_images(nplayers=len(players))

        self.ng = config.ng
        self.nx = config.nx
        self.ny = config.ny
        self.time_limit = time_limit
        self.game_map = GameMap(nx=self.nx,
                                ny=self.ny,
                                ng=self.ng,
                                high_contrast=high_contrast)
        self.graphics = Graphics(game_map=self.game_map,
                                 players=[p.team for p in players])
        self.safe = safe
        self.base_locations = np.zeros_like(self.game_map.array)

        _scores = self.read_scores(players=players, test=test)

        player_locations = self.game_map.add_players(players=players)
        self.players = {
            p.team: Player(ai=p,
                           location=player_locations[p.team],
                           number=i,
                           team=p.team,
                           batch=self.graphics.main_batch,
                           game_map=np.ma.masked_where(True, self.game_map.array),
                           score=_scores[p.team],
                           nplayers=len(players),
                           high_contrast=high_contrast,
                           base_locations=self.base_locations)
            for i, p in enumerate(players)
        }
        self.scores = {}

    def read_scores(self, players, test):
        scores = {}
        fname = 'scores.txt'
        if os.path.exists(fname) and (not test):
            with open(fname, 'r') as f:
                contents = f.readlines()
            for line in contents:
                name, score = line.split(':')
                scores[name] = int(score.strip())
        else:
            scores = {p.team: 0 for p in players}
        return scores

    def move(self, vehicle, dt):
        # pos = vehicle.ray_trace(dt=dt)
        x, y = vehicle.next_position(dt=dt)
        # xpos = np.mod(pos[0], self.nx - 1)
        # ypos = np.mod(pos[1], self.ny - 1)
        map_value = self.game_map.array[int(y), int(x)]
        vehicle.move(x, y, map_value=map_value)

    def run(self, fps=30):
        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 1 / fps)
        pyglet.app.run()

    # def generate_info(self):
    #     info = {name: {} for name in self.players}
    #     for name, player in self.players.items():
    #         for n, p in self.players.items():
    #             for group in ('bases', 'tanks', 'ships', 'jets'):
    #                 for v in getattr(player, group).values():
    #                     if not p.game_map[int(v.y):int(v.y) + 1,
    #                                       int(v.x):int(v.x) + 1].mask[0]:
    #                         if name not in info[n]:
    #                             info[n][name] = {}
    #                         if group not in info[n][name]:
    #                             info[n][name][group] = []
    #                         info[n][name][group].append((
    #                             BaseProxy(v) if group == 'bases' else VehicleProxy(v)
    #                         ) if name == n else ReadOnly(v.as_info()))
    #     return info

    def generate_info(self, player):
        info = {}
        for n, p in self.players.items() if not p.dead :
            info[n] = {'bases': [], 'tanks': [], 'ships': [], 'jets': []}
            army = p.army
            xy = np.array([(v.y, v.x) for v in army]).astype(int)
            inds = np.where(~player.game_map.array.mask[(xy[:, 0], xy[:, 1])])[0]
            for ind in inds:
                v = army[ind]
                info[n][f'{v.kind}s'].append((
                    BaseProxy(v) if v.kind == 'base' else VehicleProxy(v)
                ) if player.team == n else ReadOnly(v.as_info()))
            for key in list(info[n].keys()):
                if len(info[n][key]) == 0:
                    del info[n][key]
        return info

    def generate_info_old(self, player):
        # TODO: optimize this
        info = {}
        for n, p in self.players.items():
            info[n] = {}
            for group in ('bases', 'tanks', 'ships', 'jets'):
                for v in getattr(p, group).values():
                    if not player.game_map[int(v.y):int(v.y) + 1,
                                           int(v.x):int(v.x) + 1].mask[0]:
                        # if n not in info:
                        #     info[n] = {}
                        if group not in info[n]:
                            info[n][group] = []
                        info[n][group].append((
                            BaseProxy(v) if group == 'bases' else VehicleProxy(v)
                        ) if player.team == n else ReadOnly(v.as_info()))
        return info

    # def map_all_bases(self):
    #     self.base_locations_buffer[...] = 0.0
    #     for player in self.players.values():
    #         for base in player.bases.values():
    #             self.base_locations_buffer[int(base.y), int(base.x)] = 1
    #     # return base_locations

    def init_dt(self, t, dt):
        min_distance = config.competing_mine_radius
        # self.map_all_bases()
        base_locs = MapView(self.base_locations)
        scoreboard_labels = {}
        for name, player in self.players.items():
            player.init_dt(dt)
            for base in player.bases.values():
                base.reset_info()
                nbases = sum([
                    view.sum() for view in base_locs.view(
                        x=base.x, y=base.y, dx=min_distance, dy=min_distance)
                ])
                base.crystal += 2 * len(base.mines) / nbases
                before = base.competing
                base.competing = nbases > 1
                if before != base.competing:
                    base.make_label()
            scoreboard_labels[name] = player.make_label()
        self.graphics.update_scoreboard(t=t, players=scoreboard_labels)

    # def fight(self):
    #     cooldown = 1
    #     combats = {}
    #     dead_vehicles = {}
    #     dead_bases = {}
    #     for name, player in self.players.items():
    #         for child in player.children:
    #             igrid = int(child.x) // self.game_map.ng
    #             jgrid = int(child.y) // self.game_map.ng
    #             key = f'{igrid},{jgrid}'
    #             li = [child]
    #             if child.kind == 'base':
    #                 li += list(child.mines.values())
    #             if key not in combats:
    #                 combats[key] = {name: li}
    #             elif name not in combats[key]:
    #                 combats[key][name] = li
    #             else:
    #                 combats[key][name] += li
    #     for c in combats.values():
    #         if len(c) > 1:
    #             keys = list(c.keys())
    #             for name in keys:
    #                 for team in set(keys) - {name}:
    #                     for attacker in c[name]:
    #                         for defender in c[team]:
    #                             defender.health -= attacker.attack
    #                             defender.make_label()
    #                             if defender.health <= 0:
    #                                 if defender.kind == 'base':
    #                                     if team not in dead_bases:
    #                                         dead_bases[team] = []
    #                                     dead_bases[team].append(defender.uid)
    #                                     attacker.owner.owner.score += 1
    #                                 else:
    #                                     if team not in dead_vehicles:
    #                                         dead_vehicles[team] = []
    #                                     dead_vehicles[team].append(defender.uid)
    #     return dead_vehicles, dead_bases

    def exit(self, message):
        print(message)
        pyglet.clock.unschedule(self.update)
        pyglet.app.exit()
        score_left = len(self.scores)
        for name, p in self.players.items():
            self.scores[name] = p.score + score_left
            p.dump_map()
        fname = 'scores.txt'
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
            self.exit(message="Time limit reached!")
        # self.graphics.update_time(self.time_limit - t)
        # self.init_dt(dt)
        self.init_dt(self.time_limit - t, dt)

        # info = self.generate_info()

        for name, player in self.players.items():
            if player.dead:
                if player.animate_skull > 0:
                    player.skull_animate()
            else:
                info = self.generate_info(player)
                player.execute_ai(t=t, dt=dt, info=info, safe=self.safe)
                player.collect_transformed_ships()
        for name, player in self.players.items():
            for v in player.vehicles:
                v.reset_info()
                self.move(v, dt)
                player.update_player_map(x=v.x, y=v.y)

        dead_vehicles, dead_bases = fight(
            players={key: p
                     for key, p in self.players.items() if not p.dead},
            ng=self.game_map.ng)
        for name in dead_vehicles:
            for uid in dead_vehicles[name]:
                self.players[name].remove(uid)
        for name in dead_bases:
            for uid in dead_bases[name]:
                if uid in self.players[name].bases:
                    b = self.players[name].bases[uid]
                    self.base_locations[int(b.y), int(b.x)] = 0
                    self.players[name].remove_base(uid)
            if len(self.players[name].bases) == 0:
                print(f'Player {name} died!')
                self.scores[name] = self.players[name].score + len(self.scores)
                self.players[name].rip()
                # del self.players[name]
        players_alive = [p.team for p in self.players.values() if not p.dead]
        if len(players_alive) == 1:
            self.exit(message=f'Player {players_alive[0]} won!')
        if len(players_alive) == 0:
            self.exit(message='Everyone died!')
