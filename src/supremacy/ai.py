# SPDX-License-Identifier: BSD-3-Clause

from .tools import eucledian_distance, distance_on_torus


class Ai:

    def get_distance(self,
                     xa: float,
                     ya: float,
                     xb: float,
                     yb: float,
                     shortest=True) -> float:
        if not shortest:
            return eucledian_distance(xa, ya, xb, yb)
        else:
            return distance_on_torus(xa, ya, xb, yb)
