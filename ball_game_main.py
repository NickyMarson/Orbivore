import pyxel
from player import Player
from ball import Ball

class App:
    def __init__(self): # Constructor for the App class
        pyxel.init(160, 120, quit_key=pyxel.KEY_ESCAPE) # Initialize window (Width, Height, Quit Key)
        pyxel.title = "Salutations Huzz" # Window name

        self.player = Player(80, 60) # Create an instance of a player at (X, Y)

        self.balls = [] # Array of balls
        self.spawn_timer = 0 # Set spawn timer to 0
        self.spawn_interval = 45 # Number of frames between ball spawns, lower = more spawns
        self.spawn_cap = 100 # Spawn cap for number of balls
        
        self.score = 0 # Game score

        pyxel.run(self.update, self.draw) # Starts game loop, call update on self, then call draw on self at 30 FPS

    def update(self): # Logic like input handling, physics, game state
        if pyxel.btn(pyxel.KEY_Q): # If Q is pressed then close window
            pyxel.quit()
        
        self.player.update() # Update player

        self.spawn_timer += 1 # Increment spawn timer every frame

        if self.spawn_timer >= self.spawn_interval and len(self.balls) < self.spawn_cap: # If spawn timer reached 60 frames and spawn cap not reached
            self.balls.append(Ball(radius=5, color=8)) # Create a Ball instance and add it to the Ball array
            self.spawn_timer = 0 # Reset spawn timer

        alive = [] # Array of balls that are alive
        for ball in self.balls:
            ball.update()
            if ball.collides_with(self.player):
                self.score += 1 # Ball and player collided so increment score
            else:
                alive.append(ball) # Ball and player didn't collide so append to to alive array
        self.balls = alive # Keep all balls that didn't collide with player, avoids lag by ignoring balls that collided

    def draw(self): # Defines anything drawn on screen
        pyxel.cls(0) # Clears screen with color 0 = black

        self.player.draw() # Draw player
        for ball in self.balls:
            ball.draw()

        pyxel.text(5, 5, f"Score: {self.score}", 7) # Draw text (X, Y, String, Text Color)

App() # Creates an instance of the App class, calls constructor and runs game