# SPDX-License-Identifier: BSD-3-Clause

import template_ai

# import my_ai

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

players = {name: template_ai for name in names}
# players["Me"] = my_ai

supremacy.start(
    players=players,
    time_limit=1 * 10,
    fullscreen=False,
    seed=None,
    high_contrast=False,
    crystal_boost=5,
)
