# SPDX-License-Identifier: BSD-3-Clause
import numpy as np
from typing import Callable


def control_vehicles(
    info: dict, game_map: np.ndarray, tank: Callable, ship: Callable, jet: Callable
):
    """
    This function will call the appropriate vehicle control function for each vehicle type.

    Parameters
    ----------
    info : dict
        A dictionary containing all the information about the game.
    game_map : np.ndarray
        A 2D numpy array containing the game map.
        1 means land, 0 means water, -1 means no info.
    tank : Callable
        The function to call for controlling tanks.
    ship : Callable
        The function to call for controlling ships.
    jet : Callable
        The function to call for controlling jets.
    """
    if "tanks" in info:
        for v in info["tanks"]:
            tank(v, info, game_map)
    if "ships" in info:
        for v in info["ships"]:
            ship(v, info, game_map)
    if "jets" in info:
        for v in info["jets"]:
            jet(v, info, game_map)


class BuildQueue:
    """
    A class to manage the build queue for bases.

    Parameters
    ----------
    queue : list
        A list of strings specifying the build order.
    cycle : bool
        Whether to cycle through the build queue or not.
        If False, the last item in the queue will be repeated indefinitely.

    Returns
    -------
    build :
        The object (mine or vehicle) that was built by the base.
    """

    def __init__(self, queue: list, cycle: bool = False):
        self.queue = queue
        self.cycle = cycle
        self.inds = {}

    def __call__(self, base):
        if base.uid not in self.inds:
            self.inds[base.uid] = 0
        kind = self.queue[self.inds[base.uid]]
        if base.crystal > base.cost(kind):
            kwargs = {}
            if kind != "mine":
                kwargs["heading"] = 360 * np.random.random()
            build = getattr(base, f"build_{kind}")(**kwargs)
            if self.inds[base.uid] == len(self.queue) - 1:
                if self.cycle:
                    self.inds[base.uid] = 0
            else:
                self.inds[base.uid] += 1
            return build
