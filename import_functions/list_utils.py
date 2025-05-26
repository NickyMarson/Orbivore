# Functions relating to lists
import pyxel
from .other_utils import centerTextHorizontal

# Calculates the grid layout for other functions to use
def computeListLayout(options, y_start, spacing_x, spacing_y, mode):
    if mode == "horizontal":
        cols = len(options)
        rows = 1
    elif mode == "grid":
        cols = 2
        rows = (len(options) + cols - 1) // cols # Dynamically get num rows

    max_option_len = max(len(opt) for opt in options)
    fixed_rect_width = max_option_len * 4 + 10 # 4px per character + 10px padding
    rect_height = 12

    total_col_width = fixed_rect_width + spacing_x # Add spacing_x to the distance between columns to avoid overlapping rectangles
    total_width = total_col_width * cols - spacing_x # Avoid extra gap at end
    base_x = (pyxel.width - total_width) // 2

    total_height = (rows - 1) * spacing_y # Total vertical space between rows
    adjusted_y_start = y_start - total_height // 2

    layout = {}

    for i, option in enumerate(options): # Enumerate over the options list and save layout info per option in a dict of dicts
        row = i // cols # Get current row
        col = i % cols # Get current column

        # Check if current option is last row and only 1 option in row
        if mode == "grid" and row == rows - 1 and len(options) % 2 == 1 and col == 0:
            rect_x = (pyxel.width - fixed_rect_width) // 2 # Center single option instead of making it in the grid pattern
        else: # X position spacing between columns
            rect_x = base_x + col * total_col_width

        y = adjusted_y_start + row * spacing_y # Y position spacing between rows

        text_offset_x = (fixed_rect_width - len(option) * 4) // 2 # Adjust x to center text inside the fixed-width rect
        text_x = rect_x + text_offset_x

        # Dict for all layout info for this option, appended to the layout dict
        layout[option] = {
            "index": i, # Accessed by layout["option_name"]["index"]
            "rect_x": rect_x,
            "rect_y": y,
            "width": fixed_rect_width,
            "height": rect_height,
            "text_x": text_x
        }

    return layout

# Draws all options from the input parameters
def drawOptionList(title, options, selected_index, layout, color_selected_bg, color_selected_text, color_unselected_text):
    pyxel.text(centerTextHorizontal(title), 50, title, 14)

    for option in options: # Loop over each option in the list, get its data, then draw the option using that data
        opt_data = layout[option]
        i = opt_data["index"]
        x = opt_data["rect_x"]
        y = opt_data["rect_y"]
        w = opt_data["width"]
        h = opt_data["height"]
        text_x = opt_data["text_x"]

        pyxel.rectb(x, y - 3, w, h, 5) # Darker border around option

        if i == selected_index:
            pyxel.rect(x, y - 3, w, h, color_selected_bg) # Highlighted background
            pyxel.text(text_x, y, option, color_selected_text) # Selected option text
        else:
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