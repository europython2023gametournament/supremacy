# SPDX-License-Identifier: BSD-3-Clause

import importlib

import supremacy

names = [
    "John",
    "Dave",
    "Anna",
    "Greg",
    "Lisa",
    "Simon",
    "Tobias",
    "Isobel",
    "Robert",
]

players = {}
for name in names:
    ai = importlib.import_module(f"{name}_ai")
    players[ai.CREATOR] = ai

supremacy.start(
    players=players,
    test=False,
    safe=True,
    time_limit=8 * 60,
    fullscreen=True,
)
