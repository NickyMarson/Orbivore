import pyxel
from movement import get_acceleration_input
from constants import player_color

class Player:
    def __init__(self, x, y):
        self.x = x # Position
        self.y = y
        self.vx = 0 # Velocity
        self.vy = 0

        self.accel = 0.4 # Acceleration
        self.max_speed = 4 # Maximum speed possible
        self.friction = 0.95 # Friction coefficient
        self.radius = 8 # Player radius

    def update(self):
        ax, ay = get_acceleration_input()

        self.vx += ax * self.accel # Apply acceleration to the velocity
        self.vy += ay * self.accel

        speed = (self.vx ** 2 + self.vy ** 2) ** 0.5 # Clamp velocity to +/- max_speed
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.vx *= scale # Account for diaginal movement speed > single direction movement
            self.vy *= scale

        self.x += self.vx # Move player by velocity
        self.y += self.vy

        radius = 5 # Player size/radius
        max_x = pyxel.width - 1 - self.radius # Max/Min values to set wall boundaries
        min_x = self.radius
        max_y = pyxel.height - 1 - self.radius
        min_y = self.radius

        # Bouncy walls mechanic (Left/Right)
        if self.x < min_x: # If past the left x-boundary
            self.x = min_x # Snap player to boundary
            self.vx = -self.vx # Invert velocity to bounce player
        elif self.x > max_x: # If past the right x-boundary
            self.x = max_x
            self.vx= -self.vx

        # Bouncy walls mechanic (Up/Down)
        if self.y < min_y: # If past the top y-boundary
            self.y = min_y
            self.vy = -self.vy
        elif self.y > max_y: # If past the bottom y-boundary
            self.y = max_y
            self.vy = -self.vy
            

        self.vx *= self.friction # Apply friction to player
        self.vy *= self.friction
    
    def draw(self):
        pyxel.circ(int(self.x), int(self.y), self.radius, player_color) # Draw player as a circle (X, Y, Radius, Color)