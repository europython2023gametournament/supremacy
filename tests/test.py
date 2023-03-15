# SPDX-License-Identifier: BSD-3-Clause

import supremacy
from template_ai import PlayerAi

names = [
    'Neil',
    'Drew',
    'Simon',
    'Jankas',
    'Greg',
    'Mads',
    'Afonso',
    'Sun',
    'Troels',
    # 'Piotr'
]
# names = [
#     'Neil', 'Drew', 'Simon', 'Jankas', 'Greg', 'Mads', 'Afonso', 'Sun', 'Troels',
#     'Piotr', 'Mikkel', 'Colin'
# ]
# names = ['Neil', 'Drew', 'Simon', 'Jankas', 'Greg']
# names = ['Neil', 'Drew', 'Simon']

players = []
for name in names:
    player = PlayerAi()
    player.team = name
    players.append(player)

supremacy.start(players=players, high_contrast=True, time_limit=8 * 60)
# eng.run()
