import turtle


class Graphics:

    def __init__(self, game_map):

        self.game_map = game_map
        self.nx = self.game_map.nx
        self.ny = self.game_map.ny
        self.ng = self.game_map.ng
        self.screen = turtle.Screen()
        self.screen.clearscreen()

        self.screen.setup(width=self.nx, height=self.ny)
        self.screen.setworldcoordinates(0, 0, self.nx, self.ny)

        cv = self.screen.getcanvas()
        cv.adjustScrolls()

        self.screen.bgpic('background.png')
        cv.itemconfig(self.screen._bgpic, anchor="sw")


#
