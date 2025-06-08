import pyxel
import random

class Leaf:
    def __init__(self):
        self.x = random.uniform(-10, -1)
        self.y = random.uniform(0, pyxel.height - 6)
        self.vx = random.uniform(0.5, 1)
        self.vy = random.uniform(-0.2, 0.2)
        self.rotation = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rotation = (self.rotation + random.uniform(3, 5)) % 360

    def draw(self):
        pyxel.blt(int(self.x), int(self.y), 0, 0, 16, 7, 6, rotate=self.rotation)