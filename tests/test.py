from supremacy.core.engine import Engine

from template_ai import PlayerAi

# names = [
#     'Neil', 'Drew', 'Simon', 'Jankas', 'Greg', 'Mads', 'Afonso', 'Sun', 'Troels',
#     'Piotr'
# ]
names = ['Neil', 'Drew', 'Simon', 'Jankas']

players = []
for name in names:
    player = PlayerAi()
    player.creator = name
    players.append(player)

eng = Engine(players=players, high_contrast=True)
eng.run()
