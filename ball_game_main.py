import pyxel
from player import Player
from ball import Ball

# --------------------GLOBAL FUNCTIONS--------------------

# Centers text horizontally
def centerTextHorizontal(text):
    return (pyxel.width - len(text) * 4) // 2

# Draws all options from the input parameters
def drawOptionList(title, options, selected_index, y_start, spacing_x, spacing_y, color_selected_bg, color_selected_text, color_unselected_text, mode):
    pyxel.text(centerTextHorizontal(title), 50, title, 14)

    if mode == "horizontal":
        cols = len(options)
        rows = 1
    elif mode == "grid":
        cols = 2 # Num columns
        rows = (len(options) + cols - 1) // cols # Dynamically get num rows

    max_option_len = max(len(opt) for opt in options)
    fixed_rect_width = max_option_len * 4 + 10  # 4px per character + 10px padding
    rect_height = 12

    total_col_width = fixed_rect_width + spacing_x # Add spacing_x to the distance between columns to avoid overlapping rectangles
    total_width = total_col_width * cols - spacing_x  # Avoid extra gap at end
    base_x = (pyxel.width - total_width) // 2

    for i, option in enumerate(options): # Enumerate over the options array and draw all options dynamically in a grid pattern
        row = i // cols # Get current row
        col = i % cols # Get current column

        if mode == "grid" and row == rows - 1 and len(options) % 2 == 1 and col == 0: # Check if current option is last row and only 1 option in row
            rect_x = (pyxel.width - fixed_rect_width) // 2 # If so then center it instead of making it in the grid pattern
        else: # X position spacing between columns
            rect_x = base_x + col * total_col_width

        y = y_start + row * spacing_y # Y position spacing between rows

        text_offset_x = (fixed_rect_width - len(option) * 4) // 2 # Adjust x to center text inside the fixed-width rect
        text_x = rect_x + text_offset_x

        if i == selected_index:
            pyxel.rectb(rect_x, y - 3, fixed_rect_width, rect_height, 5) # Darker border around option
            pyxel.rect(rect_x, y - 3, fixed_rect_width, rect_height, color_selected_bg) # Highlighted background
            pyxel.text(text_x, y, option, color_selected_text) # Selected option text
        else:
            pyxel.rectb(rect_x, y - 3, fixed_rect_width, rect_height, 5) # Darker border around option
            pyxel.text(text_x, y, option, color_unselected_text) # Unselected option

# Handles scrolling on menus (vertical list)
def handleVerticalList(key_up, key_down, selected_index, options_length):
    if pyxel.btnp(key_down):
        selected_index = (selected_index + 1) % options_length
    elif pyxel.btnp(key_up):
        selected_index = (selected_index - 1) % options_length
    return selected_index

# Handles scrolling on menus (horizontal list)
def handleHorizontalList(key_left, key_right, selected_index, options_length, prev_col):
    if pyxel.btnp(key_left):
        if selected_index > 0:
            selected_index -= 1
        else:
            selected_index = options_length - 1  # Wrap to last
        prev_col = selected_index

    elif pyxel.btnp(key_right):
        if selected_index < options_length - 1:
            selected_index += 1
        else:
            selected_index = 0  # Wrap to first
        prev_col = selected_index

    return selected_index, prev_col

# Handles scrolling on menus (grid)
def handleGridSelection(key_up, key_down, key_left, key_right, selected_index, options_length, columns, prev_col):
    rows = (options_length + columns - 1) // columns  # Total number of rows

    row = selected_index // columns # Current row
    col = selected_index % columns # Current column

    # Clamp the column if invalid index for the given row
    def clampToValidIndex(new_r, c):
        idx = new_r * columns + c
        if idx >= options_length: # Clamp col to last valid index on this row
            last_col_in_row = (options_length - 1) % columns
            idx = new_r * columns + last_col_in_row
        return idx
    
    # Current selected option logic based on player input key, has vertical and horizontal wraparound
    if pyxel.btnp(key_up): # Move up, wrap from first row to last row in same column, if possible
        new_row = (row - 1) % rows
        new_index = clampToValidIndex(new_row, prev_col)
        return new_index, prev_col
    
    elif pyxel.btnp(key_down): # Move down, wrap from last row to first row in same column
        new_row = (row + 1) % rows
        new_index = clampToValidIndex(new_row, prev_col)
        return new_index, prev_col
    
    elif pyxel.btnp(key_left): # Move left, wrap from leftmost column to rightmost column of same row
        row_start_index = row * columns
        items_in_row = min(columns, options_length - row_start_index)

        if row == rows - 1 and items_in_row == 1: # If last row, only one option, go up to previous row at col 0
            if row > 0:
                new_index = clampToValidIndex(row - 1, 0)
                return new_index, 0

        if col > 0:
            col -= 1
        else: # Wrap to rightmost column of the same row
            col = (options_length - 1) % columns if (row == rows - 1) else columns - 1

        if items_in_row > 1: # Update prev_col for vertical wraparound
            prev_col = col

        return row * columns + col, prev_col

    elif pyxel.btnp(key_right): # Move right, wrap from rightmost column to leftmost column of same row
        row_start_index = row * columns
        items_in_row = min(columns, options_length - row_start_index)

        if row == rows - 1 and items_in_row == 1: # If last row, only one option, go up to previous row at col 1
            if row > 0 and columns > 1:
                new_index = clampToValidIndex(row - 1, 1)
                return new_index, 1

        if col < columns - 1 and (row * columns + col + 1) < options_length:
            col += 1
        else: # Wrap to leftmost column of the same row, always 0
            col = 0

        if items_in_row > 1: # Update prev_col for vertical wraparound
            prev_col = col

        return row * columns + col, prev_col

    return selected_index, prev_col

# --------------------APP CLASS--------------------

class App:
    def __init__(self): # Constructor for the App class
        pyxel.init(256, 256, title="Salutations Huzz", quit_key=pyxel.KEY_ESCAPE) # Initialize window (Width, Height, Quit Key)

        self.current_state = "menu" # Start on menu
        self.state_stack = [] # Tracks state path like ['menu', 'settings']
        self.cursor_map = {"menu": 0} # Tracks selected_option per state, start on menu at position 0
        self.prev_col_map = {} # Tracks previous column

        self.menu_options = ["Start", "Leaderboards", "Settings"]
        self.start_options = ["Gurt", "Yo", "Ts"]
        self.leaderboard_options = ["Gurt: Yo", "Yo: Gurt", "Rt: Ts is option 3", "3: WHAAAAAT"]
        self.setting_options = ["Controls", "Volume", "Graphics", "Aspect Ratio", "Windowed or Borderless", "FPS Display"]
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

        self.last_fps_time = pyxel.frame_count # Track FPS
        self.fps = 0

        self.startMenu()

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

        if pyxel.frame_count - self.last_fps_time >= 30:
            self.fps = 30 # Pyxel runs at a fixed 30 FPS
            self.last_fps_time = pyxel.frame_count # Count number of frames to get FPS

    def updateMenu(self): # Update menu state
        new_index, new_prev_col = self.changeCursorPosition(len(self.menu_options), 2, self.current_state, self.current_state, "grid")
        
        self.selected_menu = new_index # Update cursor position
        self.prev_col_menu = new_prev_col # Update previous column index
        self.prev_col = new_prev_col

        self.menu_spawn_timer += 1 # Increment spawn timer every frame

        # If spawn timer reached 60 frames and spawn cap not reached
        if self.menu_spawn_timer >= self.menu_spawn_interval and len(self.menu_balls) < self.menu_spawn_cap:
            self.menu_balls.append(Ball(radius=5, color=8)) # Create a Ball instance and add it to the Ball array
            self.menu_spawn_timer = 0 # Reset spawn timer

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

            if selected_option == "Yo":
                self.startGame() # Initialize objects for game

        if pyxel.btnp(pyxel.KEY_M): # If M is pressed, go back to menu
            self.exit_state()

    def updateLeaderboards(self):
        new_index, new_prev_col = self.changeCursorPosition(len(self.leaderboard_options), 2, self.current_state, self.current_state, "grid")
        
        self.selected_leaderboard = new_index # Update cursor position
        self.prev_col_leaderboard = new_prev_col # Update previous column index
        self.prev_col = new_prev_col

        if pyxel.btnp(pyxel.KEY_M): # If M is pressed, go back to menu
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

        self.player.update() # Update player

        self.spawn_timer += 1 # Increment spawn timer every frame

        # If spawn timer reached 60 frames and spawn cap not reached
        if self.spawn_timer >= self.spawn_interval and len(self.balls) < self.spawn_cap:
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

    # --------------------DRAW FUNCTIONS--------------------

    def draw(self): # Draws whichever state is currently active
        pyxel.cls(0) # Clears screen with color 0 = black
        pyxel.text(5, pyxel.height - 10, f"FPS: {self.fps}", 11) # FPS counter

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

    def drawMenu(self): # Draws menu
        for ball in self.menu_balls:
            ball.draw()

        drawOptionList("Orbivore", self.menu_options, self.selected_menu, 100, 50, 20, 6, 0, 7, "grid")

        menu_instruction = "Use arrow keys to move between options, ENTER to confirm"
        pyxel.text(centerTextHorizontal(menu_instruction), 180, menu_instruction, 5) # Menu instructions

    def drawStart(self):
        pyxel.text(centerTextHorizontal("Start"), 50, "Start", 7)

        drawOptionList("Start", self.start_options, self.selected_start, 100, 50, 20, 6, 0, 7, "horizontal")

        start_instruction = "Use arrow keys to move between options, ENTER to confirm"
        pyxel.text(centerTextHorizontal(start_instruction), 180, start_instruction, 5) # Menu instructions
    
    def drawLeaderboards(self):
        pyxel.text(centerTextHorizontal("Leaderboards"), 50, "Leaderboards", 7)

        self.selected_leaderboard = getattr(self, "selected_leaderboard", 0)  # Initialize if not set

        drawOptionList("Leaderboards", self.leaderboard_options, self.selected_leaderboard, 100, 50, 20, 6, 0, 7, "grid")

        leaderboard_instruction = "Press M to return to Menu"
        pyxel.text(centerTextHorizontal(leaderboard_instruction), 200, leaderboard_instruction, 5)

    def drawSettings(self):
        pyxel.text(centerTextHorizontal("Settings"), 50, "Settings", 7)

        drawOptionList("Settings", self.setting_options, self.selected_settings, 100, 50, 20, 6, 0, 7, "grid")

        settings_instruction = "Press M to return to Menu"
        pyxel.text(centerTextHorizontal(settings_instruction), 200, settings_instruction, 5)

    def drawGraphics(self):
        pyxel.text(centerTextHorizontal("Graphics"), 50, "Graphics", 7)

        drawOptionList("Graphics", self.graphics_options, self.selected_graphics, 100, 50, 20, 6, 0, 7, "grid")

        graphics_instruction = "Press M to return to Settings"
        pyxel.text(centerTextHorizontal(graphics_instruction), 200, graphics_instruction, 5)

    def drawVolume(self):
        pyxel.text(centerTextHorizontal("Volume"), 50, "Volume", 7)

        drawOptionList("Volume", self.volume_options, self.selected_volume, 100, 50, 20, 6, 0, 7, "grid")

        volume_instruction = "Press M to return to Settings"
        pyxel.text(centerTextHorizontal(volume_instruction), 200, volume_instruction, 5)

    def drawGame(self): # Draws game
        self.player.draw() # Draw player
        for ball in self.balls: # Draw balls
            ball.draw()

        pyxel.text(5, 5, f"Score: {self.score}", 7) # Draw text (X, Y, String, Text Color)

    # --------------------OTHER APP FUNCTIONS--------------------

    def startGame(self): # Change to game state and initialize objects
        self.enter_state("game") # Change to game state
        self.player = Player(80, 60) # Create an instance of a player at (X, Y)
        self.balls = [] # Array of balls
        self.spawn_timer = 0 # Set spawn timer to 0
        self.spawn_interval = 45 # Number of frames between ball spawns, lower = more spawns
        self.spawn_cap = 100 # Spawn cap for number of balls
        self.score = 0 # Game score
    
    def clearGame(self): # Clears game objects to stop possible memory issues
        self.player = None # Delete player object
        self.balls.clear() # Clear the balls list
        self.score = 0
        self.spawn_timer = 0

    def startMenu(self): # Create balls for main menu background visual
        self.menu_balls = []
        self.menu_spawn_timer = 0
        self.menu_spawn_interval = 30
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


App() # Creates an instance of the App class, calls constructor and runs game