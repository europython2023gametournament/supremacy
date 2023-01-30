import numpy as np
import turtle

SPEED = {'tank': 45, 'ship': 60, 'jet': 60}
HEALTH = {'tank': 70, 'ship': 100, 'jet': 100}
ATTACK = {'tank': 20, 'ship': 30, 'jet': 0}
COST = {'tank': 200, 'ship': 1000, 'jet': 400, 'mine': 500}


class Vehicle:

    def __init__(self, x, y, color, team, kind, heading=0):
        self.team = team
        self.speed = SPEED[kind]
        self.health = HEALTH[kind]
        self.attack = ATTACK[kind]
        self.cost = COST[kind]

        self.avatar = turtle.Turtle()
        self.avatar.speed(0)
        self.avatar.penup()
        self.avatar.setx(x)
        self.avatar.sety(y)
        self.avatar.color(color)
        self.avatar.shape(kind)
        self.avatar.setheading(heading)

    @property
    def x(self) -> int:
        return int(self.avatar.xcor())

    @property
    def y(self) -> int:
        return int(self.avatar.ycor())

    @property
    def position(self) -> np.ndarray:
        return np.array(self.avatar.position()).astype(int)

    @property
    def heading(self) -> float:
        return self.avatar.heading()

    @heading.setter
    def heading(self, angle: float):
        return self.avatar.setheading(angle)

    @property
    def vector(self) -> np.ndarray:
        h = self.heading * np.pi / 180.0
        return np.array([np.cos(h), np.sin(h)])

    def ray_trace(self, dt: float) -> np.ndarray:
        vt = self.speed * dt
        ray = self.vector.reshape((2, 1)) * np.linspace(1, vt, int(vt) + 1)
        return (np.array(self.avatar.position()).reshape((2, 1)) + ray).astype(int)

    def get_distance(self, pos: tuple) -> float:
        return np.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2)


class Tank(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='tank', **kwargs)

    def move(self, dt, path):
        no_obstacles = (np.sum(path == 0)) == 0
        if no_obstacles:
            self.avatar.forward(self.speed * dt)


class Ship(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='ship', **kwargs)

    def move(self, dt):
        self.avatar.forward(self.speed * dt)


class Jet(Vehicle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, kind='jet', **kwargs)

    def move(self, dt):
        self.avatar.forward(self.speed * dt)
