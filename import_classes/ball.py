import pyxel
import random
from import_variables.constants import player_color

class Ball:
    def __init__(self, radius=8, color=8):
        self.radius = radius
        self.x = random.uniform(radius, pyxel.width - 1 - radius)
        self.y = -radius
        self.vx = random.uniform(-1, 1) # Generate random velocity between a and b
        self.vy = 0
        
        self.gravity = random.uniform(0.2, 1) # Gravity to make balls fall

        excluded_colors = {0, 7, player_color} # Background, Text, Player Colors
        available_colors = [c for c in range(16) if c not in excluded_colors]
        self.color = random.choice(available_colors) # Select a color from the available colors for the current ball color

    def update(self):
        self.vy += self.gravity # Apply gravity to ball

        self.x += self.vx # Move ball by velocity
        self.y += self.vy

        max_x = pyxel.width - 1 - self.radius # Max/Min values to set wall boundaries
        min_x = self.radius
        max_y = pyxel.height - 1 - self.radius

        # Bouncy walls mechanic (Left/Right)
        if self.x < min_x: # If past the left x-boundary
            self.x = min_x # Snap player to boundary
            self.vx = -self.vx # Invert velocity to bounce player
        elif self.x > max_x: # If past the right x-boundary
            self.x = max_x
            self.vx= -self.vx

        # Bouncy walls mechanic (Only bottom)
        if self.y > max_y: # If past the bottom y-boundary
            self.y = max_y
            self.vy = -self.vy

    def draw(self):
        pyxel.circ(int(self.x), int(self.y), self.radius, self.color)

    def collides_with(self, player):
        dx = self.x - player.x # Difference in x and y between ball and player
        dy = self.y - player.y
        r = self.radius + player.radius # Total radius of player and ball combined
        return dx*dx + dy*dy < r*r # If difference is < combined radius that means they have to be colliding