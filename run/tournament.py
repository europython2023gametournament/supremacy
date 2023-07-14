# SPDX-License-Identifier: BSD-3-Clause

import importlib
import glob

import supremacy


players = {}
for repo in glob.glob("*_ai"):
    ai = importlib.import_module(f"{repo}")
    players[ai.CREATOR] = ai

supremacy.start(
    players=players,
    test=False,
    safe=True,
    time_limit=8 * 60,
    fullscreen=True,
)
