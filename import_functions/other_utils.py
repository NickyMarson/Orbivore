# Other misc functions

import pyxel
from import_variables.main_constants import other_keys

# Centers text horizontally
def centerTextHorizontal(text):
    return (pyxel.width - len(text) * 4) // 2

def any_key_pressed(): # Checks for any keyboard input
    for key in other_keys:
        if pyxel.btnp(key):
            return True

    for key in range(256):
        if pyxel.btnp(key):
            return True
    return False