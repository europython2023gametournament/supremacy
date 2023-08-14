# SPDX-License-Identifier: BSD-3-Clause

import importlib
import os
import time
from typing import Dict

import numpy as np
import pyglet

from . import config
from .base import BaseProxy
from .fight import fight
from .game_map import GameMap, MapView
from .graphics import Graphics
from .player import Player
from .tools import ReadOnly
from .vehicles import Vehicle, VehicleProxy


class Engine:
    def __init__(
        self,
        players: dict,
        safe=False,
        high_contrast=False,
        test=True,
        time_limit=300,
        crystal_boost=1,
        seed=None,
        fullscreen=False,
    ):
        if seed is not None:
            np.random.seed(seed)

        config.initialize(nplayers=len(players), fullscreen=fullscreen)

        self.nx = config.nx
        self.ny = config.ny
        self.time_limit = time_limit
        self.start_time = None
        self.scores = self.read_scores(players=players, test=test)
        self.dead_players = []
        self.high_contrast = high_contrast
        self.safe = safe
        self.player_ais = players
        self.players = {}
        self.explosions = {}
        self.crystal_boost = crystal_boost
        self.paused = False
        self.previously_paused = False
        self.pause_time = 0
        self.exiting = False
        self.time_of_last_scoreboard_update = 0

        self.game_map = GameMap(
            nx=self.nx, ny=self.ny, high_contrast=self.high_contrast
        )
        self.graphics = Graphics(engine=self, fullscreen=fullscreen)
        self.setup()

        pyglet.clock.schedule_interval(self.update, 1 / config.fps)
        pyglet.app.run()

    def setup(self):
        self.base_locations = np.zeros((self.ny, self.nx), dtype=int)
        player_locations = self.game_map.add_players(players=self.player_ais)
        self.players = {}
        for i, (name, ai) in enumerate(self.player_ais.items()):
            p = ai.PlayerAi()
            p.team = name
            self.players[p.team] = Player(
                ai=p,
                location=player_locations[p.team],
                number=i,
                team=p.team,
                batch=self.graphics.main_batch,
                game_map=self.game_map.array,
                score=self.scores[p.team],
                high_contrast=self.high_contrast,
                base_locations=self.base_locations,
            )
        self.make_player_avatars()

    def make_player_avatars(self):
        players = sorted(
            self.players.values(),
            key=lambda p: p.global_score,
            reverse=True,
        )
        for i, p in enumerate(players):
            p.make_avatar(ind=i)

    def read_scores(self, players: dict, test: bool) -> Dict[str, int]:
        scores = {}
        fname = "scores.txt"
        if os.path.exists(fname) and (not test):
            with open(fname, "r") as f:
                contents = f.readlines()
            for line in contents:
                name, score = line.split(":")
                scores[name] = int(score.strip())
        else:
            scores = {p: 0 for p in players}
        print("Scores:", scores)
        return scores

    def move(self, vehicle: Vehicle, dt: float):
        x, y = vehicle.next_position(dt=dt)
        map_value = self.game_map.array[int(y), int(x)]
        vehicle.move(x, y, map_value=map_value)

    def generate_info(self, player: Player):
        info = {}
        for n, p in [(n, p) for n, p in self.players.items() if not p.dead]:
            info[n] = {"bases": [], "tanks": [], "ships": [], "jets": []}
            army = list(p.army)
            xy = np.array([(v.y, v.x) for v in army]).astype(int)
            inds = np.where(player.game_map.array[(xy[:, 0], xy[:, 1])] != -1)[0]
            for ind in inds:
                v = army[ind]
                info[n][f"{v.kind}s"].append(
                    (BaseProxy(v) if v.kind == "base" else VehicleProxy(v))
                    if player.team == n
                    else ReadOnly(v.as_info())
                )
            for key in list(info[n].keys()):
                if len(info[n][key]) == 0:
                    del info[n][key]
        return info

    def init_dt(self, t: float):
        min_distance = config.competing_mine_radius
        base_locs = MapView(self.base_locations)
        for player in self.players.values():
            player.init_dt()
            for base in player.bases.values():
                base.reset_info()
                nbases = sum(
                    [
                        view.sum()
                        for view in base_locs.view(
                            x=base.x, y=base.y, dx=min_distance, dy=min_distance
                        )
                    ]
                )
                base.crystal += (
                    self.crystal_boost
                    * 2
                    * (30.0 / config.fps)
                    * len(base.mines)
                    / nbases
                )
                before = base.competing
                base.competing = nbases > 1
                if before != base.competing:
                    base.make_avatar()
        if abs(t - self.time_of_last_scoreboard_update) > 1:
            self.time_of_last_scoreboard_update = t
            self.graphics.update_scoreboard(t=t)

    def exit(self, message: str):
        self.exiting = True
        self.exit_time = time.time() + 1
        print(message)
        score_left = len(self.dead_players)
        for name, p in self.players.items():
            if not p.dead:
                p.update_score(score_left)
        self.make_player_avatars()
        sorted_scores = [
            (p.team, p.global_score)
            for p in sorted(
                self.players.values(), key=lambda x: x.global_score, reverse=True
            )
        ]
        fname = "scores.txt"
        with open(fname, "w") as f:
            for name, p in self.players.items():
                f.write(f"{name}: {p.global_score}\n")
        for i, (name, score) in enumerate(sorted_scores):
            print(f"{i + 1}. {name}: {score}")

    def finalize(self):
        # Dump player maps
        for p in self.players.values():
            p.dump_map()

    def update(self, dt: float):
        if self.exiting:
            if self.graphics.exit_message is None:
                self.graphics.show_exit_message()
            return

        if self.paused:
            if not self.previously_paused:
                self.previously_paused = True
                self.pause_time = time.time()
            return
        else:
            if self.previously_paused:
                self.previously_paused = False
                self.time_limit += time.time() - self.pause_time
                for name, ai in self.player_ais.items():
                    importlib.reload(ai)
                    new_ai = ai.PlayerAi()
                    new_ai.team = name
                    self.players[new_ai.team].ai = new_ai

        if self.start_time is None:
            self.start_time = time.time()
        t = time.time() - self.start_time
        if t > self.time_limit:
            self.exit(message="Time limit reached!")
        self.init_dt(self.time_limit - t)

        for key in list(self.explosions.keys()):
            self.explosions[key].update()
            if self.explosions[key].animate <= 0:
                del self.explosions[key]

        for name, player in self.players.items():
            if player.dead:
                if player.animate_cross > 0:
                    player.cross_animate()
            else:
                info = self.generate_info(player)
                player.execute_ai(t=t, dt=dt, info=info, safe=self.safe)
                player.collect_transformed_ships()
        for name, player in self.players.items():
            for v in player.vehicles:
                v.reset_info()
                if not v.stopped:
                    self.move(v, dt)
                    player.update_player_map(x=v.x, y=v.y)

        dead_vehicles, dead_bases, explosions = fight(
            players={key: p for key, p in self.players.items() if not p.dead},
            batch=self.graphics.main_batch,
        )
        self.explosions.update(explosions)
        for name in dead_vehicles:
            for uid in dead_vehicles[name]:
                self.players[name].remove(uid)
        rip_players = []
        for name in dead_bases:
            for uid in dead_bases[name]:
                if uid in self.players[name].bases:
                    b = self.players[name].bases[uid]
                    self.base_locations[int(b.y), int(b.x)] = 0
                    self.players[name].remove_base(uid)
            if len(self.players[name].bases) == 0:
                print(f"Player {name} died!")
                self.players[name].update_score(len(self.dead_players))
                self.dead_players.append(name)
                self.players[name].rip()
                rip_players.append(name)
        if dead_bases:
            self.make_player_avatars()
        for name in rip_players:
            self.players[name].init_cross_animation()
        players_alive = [p.team for p in self.players.values() if not p.dead]
        if len(players_alive) == 1:
            self.exit(message=f"Player {players_alive[0]} won!")
        if len(players_alive) == 0:
            self.exit(message="Everyone died!")
