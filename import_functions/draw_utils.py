# Extra draw functions not related to a specific state
import pyxel

def drawSmallArrow(option, layout, option_state):
    info = layout[option]
    arrow_y = info["rect_y"] + (info["height"] - 12) // 2 # Vertically center arrow in box
    arrow_width = 8
    arrow_margin = 4

    if option_state == True:
        arrow_x = info["rect_x"] + info["width"] - arrow_width - arrow_margin
        pyxel.blt(arrow_x, arrow_y, 0, 32, 2, -8, 12, 0, 0) # > inside option
    elif option_state == False:
        arrow_x = info["rect_x"] + arrow_margin
        pyxel.blt(arrow_x, arrow_y, 0, 32, 2, 8, 12, 0, 0) # < inside option

def drawArrowSprites(options, selected_index, y_start, spacing_x, color_key):
    cols = len(options)
    max_option_len = max(len(opt) for opt in options)
    fixed_rect_width = max_option_len * 4 + 10 # 4px per character + 10px padding
    total_col_width = fixed_rect_width + spacing_x
    total_width = total_col_width * cols - spacing_x
    base_x = (pyxel.width - total_width) // 2

    # Calculate x/y for selected option
    col = selected_index % cols
    rect_x = base_x + col * total_col_width
    y = y_start  # Horizontal list is a single row

    # Adjust Y as needed to center with text
    pyxel.blt(rect_x + fixed_rect_width + 2, y - 5, 0, 0, 0, 16, 16, color_key)  # -> (0, 0) to (15, 15)
    pyxel.blt(rect_x - 18, y - 5, 0, 16, 0, 16, 16, color_key)  # <- (16, 0) to (31, 15)

def drawCarousel(options, selected_index, y_start, spacing_x, color_selected_bg, color_selected_text, color_unselected_text, margin=4):
    max_option_len = max(len(opt) for opt in options)
    fixed_rect_width = max_option_len * 4 + 10 # 4px per character + 10px padding
    rect_height = 16
    center_x = pyxel.width // 2 - fixed_rect_width // 2 # Center X for center option

    # Wrap index circularly
    def wrap_index(idx):
        return idx % len(options)

    # Indices of left, center, right options
    left_idx = wrap_index(selected_index - 1)
    center_idx = selected_index
    right_idx = wrap_index(selected_index + 1)

    # Positions for options: left, center, right
    positions = [
        center_x - (fixed_rect_width + spacing_x),
        center_x,
        center_x + (fixed_rect_width + spacing_x)
    ]

    option_indices = [left_idx, center_idx, right_idx]

    for pos_x, opt_idx in zip(positions, option_indices):
        option = options[opt_idx]
        y = y_start
        text_y = y + (rect_height - 8) // 2 + 1 # Vertically center

        # Center text inside rect
        text_offset_x = (fixed_rect_width - len(option) * 4) // 2
        text_x = pos_x + text_offset_x

        # Draw rect and text
        if opt_idx == selected_index:
            pyxel.rectb(pos_x, y, fixed_rect_width, rect_height, 8)
            pyxel.rect(pos_x, y, fixed_rect_width, rect_height, color_selected_bg)
            pyxel.text(text_x, text_y, option, color_selected_text)
        else:
            pyxel.rectb(pos_x, y, fixed_rect_width, rect_height, 8)
            pyxel.text(text_x, text_y, option, color_unselected_text)

    # Draw arrows
    arrow_y = y_start + (rect_height - 16) // 2
    pyxel.blt(positions[2] + fixed_rect_width + margin, arrow_y, 0, 0, 0, 16, 16, 0) # -> between right screen edge and right option
    pyxel.blt(positions[0] - 16 - margin, arrow_y, 0, 16, 0, 16, 16, 0) # <- between left screen edge and left option