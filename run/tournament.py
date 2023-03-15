# SPDX-License-Identifier: BSD-3-Clause

import supremacy
from template_ai import PlayerAi

neil = PlayerAi()
neil.team = 'Neil'

drew = PlayerAi()
drew.team = 'Drew'

simon = PlayerAi()
simon.team = 'Simon'

jankas = PlayerAi()
jankas.team = 'Jankas'

players = [neil, drew, simon, jankas]

for i in range(10):
    supremacy.start(players=players, test=False, time_limit=8 * 60)
    input()
