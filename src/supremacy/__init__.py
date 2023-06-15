# SPDX-License-Identifier: BSD-3-Clause

from .config import Config

config = Config()

from .engine import Engine


def start(players, **kwargs):
    eng = Engine(players, **kwargs)
    eng.finalize()
    return eng
