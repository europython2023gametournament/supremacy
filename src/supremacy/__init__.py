# SPDX-License-Identifier: BSD-3-Clause

from .config import Config

config = Config()

from .engine import Engine


def start(*args, **kwargs):
    eng = Engine(*args, **kwargs)
    return eng
