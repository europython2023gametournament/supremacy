# SPDX-License-Identifier: BSD-3-Clause

import simple_ai

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
    "Oliver",
]

players = {name: simple_ai for name in names}
# players[my_ai.CREATOR] = my_ai

supremacy.start(
    players=players,
    time_limit=8 * 60,  # Time limit in seconds
    fullscreen=False,  # Set to True for fullscreen
    seed=None,  # Set seed to always generate the same map
    high_contrast=False,  # Set to True for high contrast mode
    crystal_boost=1,  # Set to > 1 to artificially increase crystal production
)
