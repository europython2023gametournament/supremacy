# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import pyglet

from typing import Any, Tuple

from . import config
from .tools import distance_on_torus


def fight(players, batch: Any) -> Tuple[dict, dict, dict]:
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

    def __init__(self, x: float, y: float, batch: Any):
        self.animate = 10
        self.opacities = np.linspace(0, 255, self.animate, dtype=int)
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
