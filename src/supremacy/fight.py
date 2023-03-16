# SPDX-License-Identifier: BSD-3-Clause

import numpy as np

from . import config
from .tools import distance_on_torus


def fight(players, batch):
    troops = [child for player in players.values() for child in player.children]
    n = len(troops)
    x = np.array([child.x for child in troops])
    y = np.array([child.y for child in troops])
    x1 = np.broadcast_to(x, (n, n))
    x2 = x1.T
    y1 = np.broadcast_to(y, (n, n))
    y2 = y1.T
    dist = distance_on_torus(x1, y1, x2, y2)
    attackers, defenders = np.where(dist < config.fight_radius)
    dead_vehicles = {}
    dead_bases = {}
    explosions = {}
    for a_ind, d_ind in zip(attackers, defenders):
        attacker = troops[a_ind]
        defender = troops[d_ind]
        if attacker.team != defender.team:
            defender.health -= attacker.attack
            defender.make_label()
            if defender.health <= 0:
                if defender.kind == 'base':
                    if defender.team not in dead_bases:
                        dead_bases[defender.team] = []
                    dead_bases[defender.team].append(defender.uid)
                    attacker.owner.owner.score += 1
                else:
                    if defender.team not in dead_vehicles:
                        dead_vehicles[defender.team] = []
                    dead_vehicles[defender.team].append(defender.uid)
                print(f"{defender.team}'s {defender.kind} was destroyed "
                      f"by {attacker.team}'s {attacker.kind} at "
                      f"{defender.x}, {defender.y}")
                explosions[defender.uid] = Explosion(defender.x, defender.y, batch)
    return dead_vehicles, dead_bases, explosions


class Explosion:

    def __init__(self, x, y, batch):
        self.animate = 10
        self.opacities = np.linspace(255, 0, self.animate)
        self.sprite = pyglet.sprite.Sprite(img=config.images['explosion'],
                                           x=x,
                                           y=y,
                                           batch=batch)

    def update(self):
        self.animate -= 1
        if self.animate >= 0:
            self.sprite.opacity = self.opacities[self.animate]
        else:
            self.sprite.delete()
        #     return True
        # return False


def fight_old(players, ng):
    # cooldown = 1
    # dist = all_distances(players)
    combats = {}
    dead_vehicles = {}
    dead_bases = {}
    for name, player in players.items():
        for child in player.children:
            igrid = int(child.x) // ng
            jgrid = int(child.y) // ng
            key = f'{igrid},{jgrid}'
            li = [child]
            if child.kind == 'base':
                li += list(child.mines.values())
            if key not in combats:
                combats[key] = {name: li}
            elif name not in combats[key]:
                combats[key][name] = li
            else:
                combats[key][name] += li
    for c in combats.values():
        if len(c) > 1:
            keys = list(c.keys())
            for name in keys:
                for team in set(keys) - {name}:
                    for attacker in c[name]:
                        for defender in c[team]:
                            defender.health -= attacker.attack
                            defender.make_label()
                            if defender.health <= 0:
                                if defender.kind == 'base':
                                    if team not in dead_bases:
                                        dead_bases[team] = []
                                    dead_bases[team].append(defender.uid)
                                    attacker.owner.owner.score += 1
                                else:
                                    if team not in dead_vehicles:
                                        dead_vehicles[team] = []
                                    dead_vehicles[team].append(defender.uid)
                                print(
                                    f"{defender.team}'s {defender.kind} was destroyed "
                                    f"by {attacker.team}'s {attacker.kind} at "
                                    f"{defender.x}, {defender.y}")
    return dead_vehicles, dead_bases
