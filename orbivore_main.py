import pyxel
import json
import os
import random

from import_variables.palettes import palette_list
from import_classes.player import Player
from import_classes.ball import Ball
from import_classes.leaf import Leaf
from import_functions.list_utils import buildSettingLabels, computeListLayout, drawOptionList, handleVerticalList, handleHorizontalList, handleGridSelection
from import_functions.draw_utils import drawSmallArrow, drawArrowSprites, drawCarousel
from import_functions.other_utils import centerTextHorizontal, any_key_pressed

# --------------------CONFIG FUNCTIONS--------------------

def load_config(): # Loads settings from config file
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    else:
        return {
            "Window Mode": "Windowed",
            "FPS Display": True
        }
    
def save_config(settings): # Saves settings in config file
    with open("config.json", "w") as f:
        json.dump(settings, f, indent=4)

# --------------------HELPER FUNCTIONS--------------------

def apply_palette(palette_name):
    palette = palette_list[palette_name] # Get palette dict coresponding to palette_name
    for i, hex_color in palette.items():
        pyxel.colors[i] = hex_color  # Apply hex_color to palette index

# --------------------APP CLASS--------------------

class App:
    def __init__(self): # Constructor for the App class
        pyxel.init(256, 256, title="Salutations Huzz", fps=60, quit_key=pyxel.KEY_ESCAPE) # Initialize window (Width, Height, Quit Key)
        apply_palette("edited") # Use default palette

        self.initializeInstanceVars() # Initialize all instance variables
        pyxel.load("sprite_sheet.pyxres")
        self.startMenu()
        self.startLeaves()

        pyxel.run(self.update, self.draw) # Starts game loop, call update on self, then call draw on self at 30 FPS

    # --------------------UPDATE FUNCTIONS--------------------

    def update(self): # Logic like input handling, physics, game state
        if pyxel.btnp(pyxel.KEY_Q): # If Q is pressed then close window
            pyxel.quit()

        # Check which state is active and update it
        if self.current_state == "menu":
            self.updateMenu()
        elif self.current_state == "start":
            self.updateStart()
        elif self.current_state == "game":
            self.updateGame()
        elif self.current_state == "leaderboards":
            self.updateLeaderboards()
        elif self.current_state == "settings":
            self.updateSettings()
        elif self.current_state == "graphics":
            self.updateGraphics()
        elif self.current_state == "volume":
            self.updateVolume()

        if pyxel.frame_count - self.last_fps_time >= 60:
            self.fps = 60 # Pyxel should run at 60 FPS
            self.last_fps_time = pyxel.frame_count # Count number of frames to get FPS

        if self.settings["Control Mode"] == "Keyboard & Mouse": # KB+M so get mouse position
            mouse_x = pyxel.mouse_x
            mouse_y = pyxel.mouse_y

            if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT): # Check for left click
                print(f"Mouse clicked at {mouse_x}, {mouse_y}")


        if self.current_state != "menu" and self.current_state != "game":
            if any_key_pressed(): # Check if a key pressed this frame
                self.last_input_frame = pyxel.frame_count


    def updateMenu(self): # Update menu state
        new_index, new_prev_col = self.changeCursorPosition(len(self.menu_options), 2, self.current_state, self.current_state, "grid")
        
        self.selected_menu = new_index # Update cursor position
        self.prev_col_menu = new_prev_col # Update previous column index
        self.prev_col = new_prev_col

        self.menu_spawn_timer += 1 # Increment spawn timer every frame

        # If spawn timer reached 60 frames and spawn cap not reached
        if self.menu_spawn_timer >= self.menu_spawn_interval and len(self.menu_balls) < self.menu_spawn_cap:
            self.menu_balls.append(Ball(8,8)) # Create a Ball instance and add it to the Ball array
            self.menu_spawn_timer = 0 # Reset spawn timer

        if pyxel.btnp(pyxel.KEY_EQUALS): # Cheat button >:(
            if len(self.menu_balls) == self.menu_spawn_cap: # Spawn cap hit so just give a bunch of speed to the balls
                for ball in self.menu_balls:
                    ball.top_boundary = True
                    if ball.vy < 0:
                        ball.vy -= 0.1
                    elif ball.vy > 0:
                        ball.vy += 0.1

            while len(self.menu_balls) < self.menu_spawn_cap: # Spawns balls until spawn cap is hit
                self.menu_balls.append(Ball(8, 8))
                self.menu_spawn_timer = 0

        for ball in self.menu_balls:
            ball.update()

        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.menu_options[self.selected_menu]

            if selected_option == "Start":
                self.clearMenu() # Delete objects from main menu
                self.enter_state("start") # Change state to start
            elif selected_option == "Leaderboards":
                self.enter_state("leaderboards") # Change state to leaderboards
            elif selected_option == "Settings":
                self.enter_state("settings") # Change state to settings

    def updateStart(self):
        if self.current_state not in self.cursor_map:
            self.cursor_map[self.current_state] = 1 # Ensure middle index is started with

        new_index, new_prev_col = self.changeCursorPosition(len(self.start_options), 1, self.current_state, self.current_state, "horizontal")
        
        self.selected_start = new_index # Update cursor position
        self.prev_col_start = new_prev_col # Update previous column index
        self.prev_col = new_prev_col

        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.start_options[self.selected_start]

            if selected_option == "Normal Game":
                self.startGame() # Initialize objects for game

        if pyxel.btnp(pyxel.KEY_M): # If M is pressed, go back to menu
            self.exit_state()

    def updateLeaderboards(self):
        self.spawnLeaves()
        
        new_index, new_prev_col = self.changeCursorPosition(len(self.leaderboard_options), 2, self.current_state, self.current_state, "grid")
        
        self.selected_leaderboard = new_index # Update cursor position
        self.prev_col_leaderboard = new_prev_col # Update previous column index
        self.prev_col = new_prev_col

        if pyxel.btnp(pyxel.KEY_M): # If M is pressed, go back to menu
            self.clearLeaves()
            self.exit_state()

    def updateSettings(self):
        new_index, new_prev_col = self.changeCursorPosition(len(self.setting_options), 2, self.current_state, self.current_state, "grid")
        
        self.selected_settings = new_index # Update cursor position
        self.prev_col_settings = new_prev_col # Update previous column index
        self.prev_col = new_prev_col

        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.setting_options[self.selected_settings]

            #if selected_option == "Controls":
                #self.enter_state("controls") # Change state to controls

            if selected_option == "Graphics":
                self.enter_state("graphics") # Change state to graphics

            elif selected_option == "Volume":
                self.enter_state("volume") # Change state to volume

            elif selected_option == "FPS Display": # Toggle FPS Display
                self.settings["FPS Display"] = not self.settings["FPS Display"]
                save_config(self.settings) # Save setting to config file

            elif selected_option == "Control Mode": # Change Control Mode (rename later to have dynamic naming)
                if self.settings["Control Mode"] == "Keyboard":
                    self.settings["Control Mode"] = "Keyboard & Mouse"
                elif self.settings["Control Mode"] == "Keyboard & Mouse":
                    self.settings["Control Mode"] = "Keyboard"
                save_config(self.settings) # Save setting to config file
                self.setting_labels = buildSettingLabels(self.setting_options, self.settings)
                self.settings_layout = computeListLayout(self.setting_labels, 128, 24, 24, "grid", self.fix_width_settings)

        if pyxel.btnp(pyxel.KEY_M): # If M is pressed, go back to menu
            self.exit_state()

    def updateGraphics(self):
        new_index, new_prev_col = self.changeCursorPosition(len(self.graphics_options), 2, self.current_state, self.current_state, "grid")
        
        self.selected_graphics = new_index # Update cursor position
        self.prev_col_graphics = new_prev_col # Update previous column index
        self.prev_col = new_prev_col

        if pyxel.btnp(pyxel.KEY_M): # If M is pressed, go back to settings
            self.exit_state()

    def updateVolume(self):
        new_index, new_prev_col = self.changeCursorPosition(len(self.volume_options), 2, self.current_state, self.current_state, "grid")
        
        self.selected_volume = new_index # Update cursor position
        self.prev_col_volume = new_prev_col # Update previous column index
        self.prev_col = new_prev_col

        if pyxel.btnp(pyxel.KEY_M): # If M is pressed, go back to settings
            self.exit_state()

    def updateGame(self): # Update game state
        if pyxel.btnp(pyxel.KEY_M): # If M is pressed, go back to menu
            self.exit_state()
            self.clearGame() # Clear game objects to free memory
            return
        
        if pyxel.btnp(pyxel.KEY_EQUALS): # Cheat button >:(   (spawns balls until spawn cap is hit)
            while len(self.balls) < self.spawn_cap:
                self.balls.append(Ball(8, 8))
                self.spawn_timer = 0

        self.player.update() # Update player

        self.spawn_timer += 1 # Increment spawn timer every frame

        # If spawn timer reached 60 frames and spawn cap not reached
        if self.spawn_timer >= self.spawn_interval and len(self.balls) < self.spawn_cap:
            self.balls.append(Ball(8, 8)) # Create a Ball instance and add it to the Ball array
            self.spawn_timer = 0 # Reset spawn timer

        alive = [] # Array of balls that are alive
        for ball in self.balls:
            ball.update()
            if ball.collides_with(self.player):
                self.score += 1 # Ball and player collided so increment score
            else:
                alive.append(ball) # Ball and player didn't collide so append to to alive array
        self.balls = alive # Keep all balls that didn't collide with player, avoids lag by ignoring balls that collided

    # --------------------DRAW FUNCTIONS--------------------

    def draw(self): # Draws whichever state is currently active
        pyxel.cls(0) # Clears screen with color 0 = black

        # Check which state is active and draw it
        if self.current_state == "menu":
            self.drawMenu()
        elif self.current_state == "start":
            self.drawStart()
        elif self.current_state == "game":
            self.drawGame()
        elif self.current_state == "leaderboards":
            self.drawLeaderboards()
        elif self.current_state == "settings":
            self.drawSettings()
        elif self.current_state == "graphics":
            self.drawGraphics()
        elif self.current_state == "volume":
            self.drawVolume()
        
        self.drawGlobal()
        self.drawGlobalSettings()


    def drawGlobal(self): # Draws everything that should (almost) always be on screen
        show_back_arrow = False
        # Checks if last button press was within the last 5 seconds, if so then display back arrow
        if self.last_input_frame is not None:
            if pyxel.frame_count - self.last_input_frame < 150:
                show_back_arrow = True

        if self.current_state != "menu" and self.current_state != "game" and show_back_arrow: # Display back arrow
            pyxel.blt(4, 4, 2, 0, 0, 16, 19, 0) # Back arrow
            pyxel.blt(20, 2, 1, 0, 0, 11, 11, 0) # M for back arrow key instructions

    def drawGlobalSettings(self): # Draws everything that should be on screen based on saved settings
        if self.settings["FPS Display"] == True:
            pyxel.text(5, pyxel.height - 10, f"FPS: {self.fps}", 11) # FPS counter

        if self.settings["Control Mode"] == "Keyboard & Mouse":
            pyxel.circ(pyxel.mouse_x, pyxel.mouse_y, 2, 7) # Draw cursor

    def drawMenu(self): # Draws menu
        for ball in self.menu_balls:
            ball.draw()

        drawOptionList("Orbivore", self.menu_options, self.selected_menu, self.menu_layout, 6, 0, 7) # Draw the grid
        menu_instruction = "Use arrow keys to move between options"
        menu_instruction_2 = "ENTER to confirm, Q to quit game"
        pyxel.text(centerTextHorizontal(menu_instruction), 180, menu_instruction, 5) # Menu instructions
        pyxel.text(centerTextHorizontal(menu_instruction_2), 190, menu_instruction_2, 5) # Menu instructions

    def drawStart(self):
        pyxel.text(centerTextHorizontal("Start"), 50, "Start", 7)
        drawCarousel(self.start_options, self.selected_start, 128, 16, 6, 0, 7, 8)
    
    def drawLeaderboards(self):
        for leaf in self.leaves:
            leaf.draw()

        pyxel.text(centerTextHorizontal("Leaderboards"), 50, "Leaderboards", 7)
        self.selected_leaderboard = getattr(self, "selected_leaderboard", 0)  # Initialize if not set
        drawOptionList("Leaderboards", self.leaderboard_options, self.selected_leaderboard, self.leaderboard_layout, 6, 0, 7)

    def drawSettings(self):
        pyxel.text(centerTextHorizontal("Settings"), 50, "Settings", 7)
        drawOptionList("Settings", self.setting_labels, self.selected_settings, self.settings_layout, 6, 0, 7, self.settings)
        drawSmallArrow("FPS Display", self.settings_layout, self.settings["FPS Display"]) # Draws < or > arrow inside FPS Display option

    def drawGraphics(self):
        pyxel.text(centerTextHorizontal("Graphics"), 50, "Graphics", 7)
        drawOptionList("Graphics", self.graphics_options, self.selected_graphics, self.graphics_layout, 6, 0, 7)

    def drawVolume(self):
        pyxel.text(centerTextHorizontal("Volume"), 50, "Volume", 7)
        drawOptionList("Volume", self.volume_options, self.selected_volume, self.volume_layout, 6, 0, 7)

    def drawGame(self): # Draws game
        self.player.draw() # Draw player
        for ball in self.balls: # Draw balls
            ball.draw()

        pyxel.text(5, 5, f"Score: {self.score}", 7) # Draw game score (X, Y, String, Text Color)

    # --------------------OTHER APP FUNCTIONS--------------------

    def startGame(self): # Change to game state and initialize objects
        self.enter_state("game") # Change to game state
        self.player = Player(80, 60) # Create an instance of a player at (X, Y)
        self.balls = [] # Array of balls
        self.spawn_timer = 0 # Set spawn timer to 0
        self.spawn_interval = 90 # Number of frames between ball spawns, lower = more spawns
        self.spawn_cap = 100 # Spawn cap for number of balls
        self.score = 0 # Game score
    
    def clearGame(self): # Clears game objects to stop possible memory issues
        self.player = None # Delete player object
        self.balls.clear() # Clear the balls list
        self.score = 0
        self.spawn_timer = 0

    def startMenu(self): # Initialize ball variables for main menu background visual
        self.menu_balls = []
        self.menu_spawn_timer = 0
        self.menu_spawn_interval = 60
        self.menu_spawn_cap = 100

    def clearMenu(self): # Clears main menu objects to stop possible memory issues
        self.menu_balls.clear()
        self.menu_spawn_timer = 0

    def changeCursorPosition(self, options_length, columns, prev_col_map_key, cursor_map_key, mode):
        selected_index = self.cursor_map.get(cursor_map_key, 0) # Get cursor position or default to 0
        prev_col = self.prev_col_map.get(prev_col_map_key, 0) # Get previous column index or default to 0

        if mode == "grid":
            new_index, new_prev_col = handleGridSelection(pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT,
            selected_index, options_length, columns, prev_col)
        elif mode == "horizontal":
            new_index, new_prev_col = handleHorizontalList(pyxel.KEY_LEFT, pyxel.KEY_RIGHT, selected_index, options_length, prev_col)

        self.cursor_map[cursor_map_key] = new_index # Update cursor position
        self.prev_col_map[prev_col_map_key] = new_prev_col # Update previous column index

        return new_index, new_prev_col
    
    def startLeaves(self): # Initialize leaf variables for background visual
        self.leaves = []
        self.leaf_spawn_timer = 0
        self.leaf_spawn_interval = 60
        self.leaf_spawn_cap = 100

    def clearLeaves(self): # Clears leaf objects to stop possible memory issues
        self.leaves.clear()
        self.leaf_spawn_timer = 0

    def spawnLeaves(self): # Spawns and updates leaves
        self.leaf_spawn_timer += 1 # Increment spawn timer every frame

        # If spawn timer reached 60 frames and spawn cap not reached
        if self.leaf_spawn_timer >= self.leaf_spawn_interval and len(self.leaves) < self.leaf_spawn_cap:
            self.leaves.append(Leaf()) # Create a Leaf instance and add it to the Leaves array
            self.leaf_spawn_timer = 0 # Reset spawn timer

        for leaf in self.leaves:
            leaf.update()

    def enter_state(self, new_state): # Linked list approach to states and cursor position (enter state)
        if self.current_state:
            self.state_stack.append(self.current_state) # Append state that is being entered

        self.selected_option = self.cursor_map.get(new_state, 0) # Get default cursor position for new state or default to 0
        self.current_state = new_state # Update current state to appended state

    def exit_state(self): # Linked list approach to states and cursor position (leave state)
        if self.state_stack:
            self.cursor_map[self.current_state] = self.selected_option # Remember current cursor position before exiting
            self.prev_col_map[self.current_state] = self.prev_col # Remember current column index before exiting

            self.cursor_map.pop(self.current_state, None) # Forget cursor position of exited state
            self.prev_col_map.pop(self.current_state, None) # Forget column index of exited state

            self.current_state = self.state_stack.pop() # Pop previous state from stack and switch back
            self.selected_option = self.cursor_map.get(self.current_state, 0) # Get default cursor position for previous state or default to 0
            self.prev_col = self.prev_col_map.get(self.current_state, 0) # Get default column index for previous state or default to 0

    def initializeInstanceVars(self): # Initializes instance variables, just makes __init__() easier to read
        self.current_state = "menu" # Start on menu
        self.state_stack = [] # Tracks state path like ['menu', 'settings']
        self.cursor_map = {"menu": 0} # Tracks selected_option per state, start on menu at position 0
        self.prev_col_map = {} # Tracks previous column

        self.menu_options = ["Start", "Leaderboards", "Settings"]
        self.start_options = ["Gurt", "Normal Game", "Ts"]
        self.leaderboard_options = ["Gurt: Yo", "Yo: Gurt", "Rt: Ts is option 3", "3: WHAAAAAT"]
        self.setting_options = ["Controls", "Volume", "Graphics", "Aspect Ratio", "Control Mode", "FPS Display"]
        self.graphics_options = ["Main Menu Balls", "Colorblind Mode"]
        self.volume_options = ["Master Volume", "Other Volume (TBD)"]

        self.selected_menu = 0 # Set current main menu selected option to 0 (top left)
        self.selected_start = 1
        self.selected_leaderboard = 0
        self.selected_settings = 0
        self.selected_graphics = 0
        self.selected_volume = 0

        self.prev_col_menu = 0 # Set last main menu selected column to 0 (top left)
        self.prev_col_start = 0
        self.prev_col_leaderboard = 0
        self.prev_col_settings = 0
        self.prev_col_graphics = 0
        self.prev_col_volume = 0

        self.settings = load_config() # Load the saved settings from the config file
        self.setting_labels = buildSettingLabels(self.setting_options, self.settings)
        self.fix_width_settings = "123456789123456789"

        self.menu_layout = computeListLayout(self.menu_options, 128, 24, 24, "grid") # Calculate positions of options in a grid layout
        self.leaderboard_layout = computeListLayout(self.leaderboard_options, 128, 24, 24, "grid")
        self.settings_layout = computeListLayout(self.setting_labels, 128, 24, 24, "grid", self.fix_width_settings)
        self.graphics_layout = computeListLayout(self.graphics_options, 128, 24, 24, "grid")
        self.volume_layout = computeListLayout(self.volume_options, 128, 24, 24, "grid")

        self.last_fps_time = pyxel.frame_count # Track FPS
        self.fps = 0
        self.last_input_frame = None


App() # Creates an instance of the App class, calls constructor and runs game