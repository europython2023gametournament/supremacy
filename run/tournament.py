# SPDX-License-Identifier: BSD-3-Clause

import importlib
import os
import supremacy

names = [
    'afonso',
    'drew',
    # 'greg',
    # 'jankas',
    # 'mads',
    # 'neil',
    # 'piotr',
    # 'simon',
    # 'sun',
    # 'troels',
]

players = {}
for name in names:
    ai = importlib.import_module(f'{name}_ai')
    players[ai.CREATOR] = ai

current_round = 0
fname = 'scores.txt'
if os.path.exists(fname):
    with open(fname, 'r') as f:
        contents = f.readline()
    current_round = int(contents.split('=')[1].strip())

for i in range(current_round, 10):
    print(f'############# ROUND {i + 1} #############')
    supremacy.start(players=players, test=False, safe=True, time_limit=8 * 60)
    input()
