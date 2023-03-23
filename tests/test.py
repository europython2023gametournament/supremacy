# SPDX-License-Identifier: BSD-3-Clause

import template_ai

import supremacy

names = [
    'Neil', 'Drew', 'Simon', 'Jankas', 'Greg', 'Mads', 'Afonso', 'Sun', 'Troels',
    'Piotr'
]

players = {name: template_ai for name in names}

supremacy.start(players=players,
                high_contrast=False,
                time_limit=8 * 60,
                crystal_boost=1)
