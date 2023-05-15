# SPDX-License-Identifier: BSD-3-Clause

import template_ai
import neil_ai

import supremacy

names = [
    'Afonso',
    'Drew',
    'Greg',
    'Jankas',
    'Mads',
    'Simon',
    'Sun',
]

players = {name: template_ai for name in names}
players['Neil'] = neil_ai

supremacy.start(players=players,
                high_contrast=False,
                time_limit=8 * 60,
                crystal_boost=5)
