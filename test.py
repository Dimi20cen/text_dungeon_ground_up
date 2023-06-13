import json

# Read the JSON file
with open('test.json', 'r') as f:
    game_data = json.load(f)

# Now game_data is a Python dictionary.
# You can manipulate it like any other dictionary.

# For instance, let's change the 'description' in the 'start' room
new_description = "This is the new description for the start room."
game_data['rooms']['start']['description'] = new_description

# If you want to save your changes back to the JSON file:
with open('test.json', 'w') as f:
    json.dump(game_data, f, indent=4)
