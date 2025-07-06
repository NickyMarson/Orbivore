# Item sprites and their attributes

# Item Box sprites
item_sprites = {
    "baseball_bat": {
        "imgbank": 0,
        "u_imgbank": 0,
        "v_imgbank": 16,
        "height_item": 16,
        "width_item": 16
    },
    "bomb": {
        "imgbank": 0,
        "u_imgbank": 16,
        "v_imgbank": 32,
        "height_item": 15,
        "width_item": 14
    }
}

# In game Item sprites + attributes
item_attributes = {
    "baseball_bat": {
        "type": "undetermined",
        "animations": {
            "idle": [
                {"frame": (0, 0, 16, 15, 14), "duration": 30} # Placeholder
            ]
        }
    },

    "bomb": {
        "type": "throwable",
        "animations": {
            "throw": {
                "frames": [
                    {"frame": (0, 16, 16, 15, 14), "duration": 30}, # Unlit thrown (0.5 sec)
                    {"frame": (0, 16, 32, 15, 14), "duration": 30} # Lit thrown
                ],
                "repeat": 1 # Play 2 frames 1 time
            },
            "explode": {
                "frames": [
                    {"frame": (0, 16, 48, 15, 14), "duration": 6}, # Explosion 1 (0.1 sec)
                    {"frame": (0, 16, 64, 15, 14), "duration": 6} # Explosion 2
                ],
                "repeat": 10 # Play 2 frames 10 times
            }
        }
    }
}