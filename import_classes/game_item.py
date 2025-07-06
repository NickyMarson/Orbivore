import pyxel
from import_variables.items import item_attributes

class GameItem:
    def __init__(self, item_name, x, y):
        self.item_name = item_name
        self.x = x
        self.y = y
        self.attributes = item_attributes[item_name]
        self.anim_name = "" # Animation type like "throw" or "explode"
        self.anim_start = pyxel.frame_count
        self.anim_finished = False # Used to repeat animation
    
    def update(self):
        return
    
    def draw(self):
        return
    
    def collides_with_ball(self, ball):
        return
    
    def collides_with_wall(self, ball):
        return