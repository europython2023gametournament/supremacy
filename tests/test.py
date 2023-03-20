# SPDX-License-Identifier: BSD-3-Clause

import supremacy
# from template_ai import PlayerAi
import template_ai
import neil_ai

# names = [
#     'Neil',
#     'Drew',
#     'Simon',
#     'Jankas',
#     'Greg',
#     'Mads',
#     # 'Afonso',
#     # 'Sun',
#     # 'Troels',
#     # 'Piotr'
# ]

# players = []
# for name in names:
#     player = PlayerAi()
#     player.team = name
#     players.append(player)

players = {ai.CREATOR: ai for ai in [template_ai, neil_ai]}

supremacy.start(players=players, high_contrast=True, time_limit=8 * 60, crystal_boost=1)
