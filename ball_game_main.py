import pyxel
from player import Player
from ball import Ball

prev_col = 0 # Default prev_col state for menu vertical wraparound

# Centers text horizontally
def centerTextHorizontal(text):
    return (pyxel.width - len(text) * 4) // 2

# Draws all options from the input parameters
def drawOptionList(title, options, selected_index, y_start, spacing_x, spacing_y, color_selected_bg, color_selected_text, color_unselected_text):
    pyxel.text(centerTextHorizontal(title), 50, title, 7)

    cols = 2 # Num columns
    rows = (len(options) + cols - 1) // cols # Dynamically get num rows

    for i, option in enumerate(options): # Enumerate over the options array and draw all options dynamically in a grid pattern
        row = i // cols # Get current row
        col = i % cols # Get current column

        if row == rows - 1 and len(options) % 2 == 1 and col == 0: # Check if current option is last row and only 1 option in row
            x = centerTextHorizontal(option) # If so then center it instead of making it in the grid pattern
        else: # X position spacing between columns
            total_width = spacing_x * cols
            base_x = (pyxel.width - total_width) // 2
            x = base_x + col * spacing_x

        y = y_start + row * spacing_y # Y position spacing between rows
        rect_width = len(option) * 4 + 10 # 4 pixels per char + padding
        rect_x = x - 5 # match the 5px padding

        if i == selected_index:
            pyxel.rect(rect_x, y - 3, rect_width, 12, color_selected_bg) # Highlighted background
            pyxel.text(x, y, option, color_selected_text) # Selected option text
        else:
            pyxel.text(x, y, option, color_unselected_text) # Unselected option

# Handles scrolling on menus (list)
def handleListSelection(key_up, key_down, selected_index, options_length):
    if pyxel.btnp(key_down):
        selected_index = (selected_index + 1) % options_length
    elif pyxel.btnp(key_up):
        selected_index = (selected_index - 1) % options_length
    return selected_index

# Handles scrolling on menus (grid)
def handleGridSelection(key_up, key_down, key_left, key_right, selected_index, options_length, columns):
    rows = (options_length + columns - 1) // columns  # Total number of rows

    row = selected_index // columns # Current row
    col = selected_index % columns # Current column
    global prev_col

    # Clamp the column if invalid for the given row
    def clamp_to_valid_index(new_r, c):
        idx = new_r * columns + c
        if idx >= options_length: # Clamp col to last valid index on this row
            last_col_in_row = (options_length - 1) % columns
            idx = new_r * columns + last_col_in_row
        return idx
    
    # Current selected option logic based on player input key, has vertical and horizontal wraparound
    if pyxel.btnp(key_up): # Move up, wrap from first row to last row in same column, if possible
        new_row = (row - 1) % rows
        new_index = clamp_to_valid_index(new_row, prev_col)
        return new_index
    
    elif pyxel.btnp(key_down): # Move down, wrap from last row to first row in same column
        new_row = (row + 1) % rows
        new_index = clamp_to_valid_index(new_row, prev_col)
        return new_index
    
    elif pyxel.btnp(key_left): # Move left, wrap from leftmost column to rightmost column of same row
        if col > 0:
            col -= 1
        else: # Wrap to rightmost column of the same row
            col = (options_length - 1) % columns if (row == rows - 1) else columns - 1

        row_start_index = row * columns
        items_in_row = min(columns, options_length - row_start_index)
        if items_in_row > 1: # Update prev_col for vertical wraparound
            prev_col = col

        return row * columns + col

    elif pyxel.btnp(key_right): # Move right, wrap from rightmost column to leftmost column of same row
        if col < columns - 1 and (row * columns + col + 1) < options_length:
            col += 1
        else: # Wrap to leftmost column of the same row, always 0
            col = 0

        row_start_index = row * columns
        items_in_row = min(columns, options_length - row_start_index)
        if items_in_row > 1: # Update prev_col for vertical wraparound
            prev_col = col

        return row * columns + col

    return selected_index



class App:
    def __init__(self): # Constructor for the App class
        pyxel.init(256, 256, title="Salutations Huzz", quit_key=pyxel.KEY_ESCAPE) # Initialize window (Width, Height, Quit Key)

        self.state = "menu" # Start on menu
        self.menu_options = ["Start", "Leaderboards", "Settings"]
        self.leaderboard_options = ["Gurt: Yo", "Yo: Gurt", "Rt: Ts is option 3", "3: WHAAAAAT"]
        self.selected_index = 0

        pyxel.run(self.update, self.draw) # Starts game loop, call update on self, then call draw on self at 30 FPS

    def update(self): # Logic like input handling, physics, game state
        if pyxel.btnp(pyxel.KEY_Q): # If Q is pressed then close window
            pyxel.quit()

        # Check which state is active and update it
        if self.state == "menu":
            self.updateMenu()
        if self.state == "game":
            self.updateGame()
        elif self.state == "leaderboards":
            self.updateLeaderboards()
        elif self.state == "settings":
            self.updateSettings()

    def updateMenu(self): # Update menu state
        columns = 2
        #self.selected_index = handleListSelection(pyxel.KEY_UP, pyxel.KEY_DOWN, self.selected_index, len(self.menu_options))
        self.selected_index = handleGridSelection(pyxel.KEY_UP, pyxel.KEY_DOWN, pyxel.KEY_LEFT, pyxel.KEY_RIGHT,
        self.selected_index, len(self.menu_options), columns)

        if pyxel.btnp(pyxel.KEY_RETURN):
            selected_option = self.menu_options[self.selected_index]

            if selected_option == "Start":
                self.startGame() # Initialize objects for game
            elif selected_option == "Leaderboards":
                self.state = "leaderboards"  # Change state to leaderboards
            elif selected_option == "Settings":
                # Settings screen added here
                #self.state = "settings"  # Change state to settings
                pass

    def updateLeaderboards(self):
        if not hasattr(self, "selected_leaderboard"):
            self.selected_leaderboard = 0

        self.selected_leaderboard = handleListSelection(pyxel.KEY_UP, pyxel.KEY_DOWN, self.selected_leaderboard, len(self.leaderboard_options))

        if pyxel.btnp(pyxel.KEY_M): # If M is pressed, go back to menu
            self.state = "menu"

    def updateSettings(self):
        # Logic for settings screen (e.g., changing settings)
        if pyxel.btnp(pyxel.KEY_M): # If M is pressed, go back to menu
            self.state = "menu"

    def updateGame(self): # Update game state
        if pyxel.btnp(pyxel.KEY_M): # If M is pressed, go back to menu
            self.state = "menu"
            self.clearGame() # Clear game objects to free memory
            return

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

    def draw(self): # Draws whichever state is currently active
        pyxel.cls(0) # Clears screen with color 0 = black

        # Check which state is active and draw it
        if self.state == "menu":
            self.drawMenu()
        elif self.state == "game":
            self.drawGame()
        elif self.state == "leaderboards":
            self.drawLeaderboards()
        elif self.state == "settings":
            self.drawSettings()

    def drawMenu(self): # Draws menu
        drawOptionList(title="Salutations Huzz", options=self.menu_options, selected_index=self.selected_index,
        y_start=100, spacing_x=50, spacing_y=20, color_selected_bg=6, color_selected_text=0, color_unselected_text=7)

        menu_instruction = "Use UP/DOWN arrow keys to select, ENTER to confirm"
        pyxel.text(centerTextHorizontal(menu_instruction), 180, menu_instruction, 5) # Menu instructions
    
    def drawLeaderboards(self): # Draws Leaderboards menu
        pyxel.text(centerTextHorizontal("Leaderboards"), 50, "Leaderboards", 7)

        self.selected_leaderboard = getattr(self, "selected_leaderboard", 0)  # Initialize if not set

        drawOptionList(title="Leaderboards", options=self.leaderboard_options, selected_index=self.selected_leaderboard,
        y_start=100, spacing_x=50, spacing_y=20, color_selected_bg=6, color_selected_text=0, color_unselected_text=7)

        leaderboard_instruction = "Press M to return to menu"
        pyxel.text(centerTextHorizontal(leaderboard_instruction), 200, leaderboard_instruction, 5)

    def drawSettings(self):
        pass

    def drawGame(self): # Draws game
        self.player.draw() # Draw player
        for ball in self.balls: # Draw balls
            ball.draw()

        pyxel.text(5, 5, f"Score: {self.score}", 7) # Draw text (X, Y, String, Text Color)


    def startGame(self): # Change to game state and initialize objects
        self.state = "game" # Change to game state
        self.player = Player(80, 60) # Create an instance of a player at (X, Y)
        self.balls = [] # Array of balls
        self.spawn_timer = 0 # Set spawn timer to 0
        self.spawn_interval = 45 # Number of frames between ball spawns, lower = more spawns
        self.spawn_cap = 100 # Spawn cap for number of balls
        self.score = 0 # Game score
    
    def clearGame(self): # Clears game objects to stop possible memory issues
        self.player = None
        self.balls.clear()  # Clear the balls list
        self.score = 0
        self.spawn_timer = 0

App() # Creates an instance of the App class, calls constructor and runs game