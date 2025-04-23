import pyxel

def get_acceleration_input():
    ax, ay = 0, 0

    if pyxel.btn(pyxel.KEY_LEFT):
        ax = -1
    if pyxel.btn(pyxel.KEY_RIGHT):
        ax = 1
    if pyxel.btn(pyxel.KEY_UP):
        ay = -1
    if pyxel.btn(pyxel.KEY_DOWN):
        ay = 1

    return ax, ay