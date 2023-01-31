import pyglet

config = dict()

config['speed'] = {'tank': 20, 'ship': 60, 'jet': 60}
config['health'] = {'tank': 70, 'ship': 100, 'jet': 100}
config['attack'] = {'tank': 20, 'ship': 30, 'jet': 0}
config['cost'] = {'tank': 200, 'ship': 1000, 'jet': 400, 'mine': 500}
config['images'] = {}

config['images']
for name in ('jet', 'ship', 'tank'):
    image = pyglet.image.load('jet.png')
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
    config['images'][name] = image
