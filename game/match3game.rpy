# This minigame is focused on matching 3 items to add to a score
init python:
    import random

    # Game grid size
    grid_width = 8
    grid_height = 8

    # Type of tiles
    tile_types = ["red", "green", "blue", "yellow", "purple", "orange", "pink", "white"]

    # Image libraries for the tiles
    tile_images = {
        "red": "red_tile",
        "green": "green_tile",
        "blue": "blue_tile",
        "yellow": "yellow_tile",
        "purple": "purple_tile",
        "orange": "orange_tile",
        "pink": "pink_tile",
        "white": "white_tile"
    }

    selected_tile_images = {
        "red": "red_tile_selected",
        "green": "green_tile_selected",
        "blue": "blue_tile_selected",
        "yellow": "yellow_tile_selected",
        "purple": "purple_tile_selected",
        "orange": "orange_tile_selected",
        "pink": "pink_tile_selected",
        "white": "white_tile_selected"
    }

    # Create transformed displayables for each tile type (normal and selected)
    transformed_tiles = {name: Transform(image_name, zoom=0.5) for name, image_name in tile_images.items()}
    transformed_selected_tiles = {name: Transform(image_name, zoom=0.5) for name, image_name in selected_tile_images.items()}

    # Set the initial selected tile to the top-left corner of the grid
    selected_tile = (0, 0)  # Set to the first tile in the grid by default

    # Score system 
    player_score = 0
    target_score = 50
    
    # Create the game grid
    def create_grid():
        grid = [[random.choice(tile_types) for _ in range(grid_width)] for _ in range(grid_height)]
        
        # Check for initial matches and regenerate until no matches are found
        while True:
            initial_matches = check_matches(grid)
            if not initial_matches:
                break  # No matches found, the grid is valid

            # Remove initial matches by replacing matched tiles with new random ones
            for y, x in initial_matches:
                grid[y][x] = random.choice(tile_types)

        return grid

    # Function to display the grid in a basic format for debugging
    def display_grid(grid):
        for row in grid:
            print(" ".join(row))

    # Function to check for matches (3 or more in a row or column)
    def check_matches(grid):
        matches = set()  # Use a set to store matched tile positions to avoid duplicates

        # Check horizontal matches
        for y in range(grid_height):
            for x in range(grid_width - 2):
                if grid[y][x] == grid[y][x + 1] == grid[y][x + 2]:
                    matches.update([(y, x), (y, x + 1), (y, x + 2)])

        # Check vertical matches
        for x in range(grid_width):
            for y in range(grid_height - 2):
                if grid[y][x] == grid[y + 1][x] == grid[y + 2][x]:
                    matches.update([(y, x), (y + 1, x), (y + 2, x)])

        return matches

    def remove_matches(grid, matches):
        # Increase the score based on the number of matched tiles
        global player_score
        player_score += len(matches)

        # Remove matched tiles by setting them to None
        for y, x in matches:
            grid[y][x] = None

        # Shift tiles down and fill empty spaces
        for x in range(grid_width):
            empty_spots = []

            # Shift non-empty tiles down and collect empty spots
            for y in range(grid_height - 1, -1, -1):
                if grid[y][x] is None:
                    empty_spots.append(y)
                elif empty_spots:
                    # Move the tile to the lowest empty spot
                    empty_y = empty_spots.pop(0)
                    grid[empty_y][x] = grid[y][x]
                    grid[y][x] = None
                    empty_spots.append(y)

        # Fill in the empty spots at the top with new random tiles
        for x in range(grid_width):
            for y in range(grid_height):
                if grid[y][x] is None:
                    grid[y][x] = random.choice(tile_types)

        # Recursively remove new matches
        new_matches = check_matches(grid)
        if new_matches:
            print("New matches found after filling:", new_matches)
            remove_matches(grid, new_matches)

    # Handle gameplay
    def swap_tiles(grid, pos1, pos2):
        y1, x1 = pos1
        y2, x2 = pos2
        grid[y1][x1], grid[y2][x2] = grid[y2][x2], grid[y1][x1]

    def handle_tile_click(y, x):
        global selected_tile, game_grid

        # If no tile is selected, select the clicked tile
        if selected_tile is None:
            selected_tile = (y, x)

        # If a tile is already selected, check for adjacency and perform a swap
        else:
            sy, sx = selected_tile

            # Check if the clicked tile is adjacent to the selected tile
            if abs(sy - y) + abs(sx - x) == 1:
                swap_tiles(game_grid, (sy, sx), (y, x))
                print("Grid after swap:")
                display_grid(game_grid)

                # Check for matches after the swap
                matches = check_matches(game_grid)
                if matches:
                    print("Match found at: ", matches)
                    remove_matches(game_grid, matches)
                    print("Grid after removing matches:")
                    display_grid(game_grid)
                else:
                    # If no match, swap the tiles back
                    swap_tiles(game_grid, (sy, sx), (y, x))

                # Deselect after the swap attempt
                selected_tile = None
            else:
                # If not adjacent, deselect the current selection
                selected_tile = None


    # Refresh the board
    def refresh_board():
        global game_grid
        game_grid = create_grid()
        print("Board has been refreshed.")
        display_grid(game_grid)

    # Initialize the game state
    game_grid = create_grid()
    print("Initial Grid:")
    display_grid(game_grid)

screen match3_minigame():
    frame:
        align (0.5, 0.5)
        has vbox

        # Display the score at the top
        text "Score: [player_score] / [target_score]" align (0.5, 0.05) size 40 color "#ffffff"

        for y in range(grid_height):
            hbox:
                for x in range(grid_width):
                    # Define a ConditionSwitch to determine the image to display
                    $ current_image = ConditionSwitch(
                        selected_tile == (y, x), transformed_selected_tiles[game_grid[y][x]],
                        True, transformed_tiles[game_grid[y][x]]
                    )

                    imagebutton:
                        idle current_image
                        hover current_image
                        action Function(handle_tile_click, y, x)

        # Add a refresh button at the top of the screen
        vbox:
            align (0.5, 0.05)
            spacing 10
            textbutton "Refresh Board" action Function(refresh_board) style "button"

        if player_score >= target_score:
            text "You Win!" size 80 color "#ffcc00" align (0.5, 0.5)  # Centered win message
            textbutton "Continue" action Return() align (0.5, 0.6)

label match3:
    "Let's play a match-3 game!"
    call screen match3_minigame

label win_screen:
    "Congratulations! You have won the match-3 game!"
    "What would you like to do?"
    menu:
        "Play Again":
            jump match3
        "Quit":
            return

    return
