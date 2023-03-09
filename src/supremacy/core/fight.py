# SPDX-License-Identifier: BSD-3-Clause

import numpy as np


def all_distances(players):
    x = np.arange(10.)
    y = np.linspace(33., 44., 10)

    x1 = np.broadcast_to(x, (10, 10))
    x2 = x1.T
    y1 = np.broadcast_to(y, (10, 10))
    y2 = y1.T
    y2


def fight(players, ng):
    # cooldown = 1
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
