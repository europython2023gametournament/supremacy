# SPDX-License-Identifier: BSD-3-Clause

import os
import supremacy
import template_ai

# neil = PlayerAi()
# neil.team = 'Neil'

# drew = PlayerAi()
# drew.team = 'Drew'

# simon = PlayerAi()
# simon.team = 'Simon'

# jankas = PlayerAi()
# jankas.team = 'Jankas'

# players = [neil, drew, simon, jankas]

names = [
    'Neil',
    'Drew',
    'Simon',
    'Jankas',
    'Greg',
    'Mads',
]

players = {name: template_ai for name in names}

current_round = 0
fname = 'scores.txt'
if os.path.exists(fname):
    with open(fname, 'r') as f:
        contents = f.readline()
    current_round = int(contents.split('=')[1].strip())

for i in range(current_round, 10):
    supremacy.start(players=players, test=False, time_limit=8 * 60)
    input()
