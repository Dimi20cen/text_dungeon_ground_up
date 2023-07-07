import json
import sys
import shutil
import os
import atexit

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib


class GameWindow(Gtk.Window):
    def __init__(self, game):
        super(GameWindow, self).__init__(title="Game")
        self.game = game

        # Create a vertical box to stack widgets
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.vbox)

        # Create a textview to show the game output
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.vbox.pack_start(self.textview, True, True, 0)

        # Create an entry for player's input
        self.entry = Gtk.Entry()
        self.vbox.pack_start(self.entry, False, True, 0)

        # When the enter key is pressed in the entry, call on_activate
        self.entry.connect("activate", self.on_activate)

    def on_activate(self, widget):
        command = widget.get_text()
        widget.set_text("")
        self.game.process_command(command, self.append_text)

    def append_text(self, text):
        buffer = self.textview.get_buffer()
        buffer.insert_at_cursor(text + "\n")

    # This will be called instead of print
    def print_to_textview(self, text):
        self.append_text(text + '\n')


class Game:
    def __init__(self, map_file):
        self.map_file = map_file
        self.data = self.load_map(map_file)
        if not self.data:
            sys.exit('Error loading map file.')
        atexit.register(self.quit_game)

        self.player = Player(self.data, self)
        self.current_room = Room(self.data["rooms"].get("start"), self.data)

        self.command_palette = {
            'north': self.move_player,
            'south': self.move_player,
            'west': self.move_player,
            'east': self.move_player,
            'take': self.player.pick_up_item,
            'use': self.player.use_item,
            'look': self.look_around,
            'inventory': self.player.check_inventory,
            'help': self.print_help,
            'restart': self.restart_game,
            'quit': self.quit_game
        }

    def load_map(self, filename):
        try:
            shutil.copyfile(filename, 'map_copy.json')
            with open('map_copy.json', 'r') as f:
                game_data = json.load(f)
                return game_data
        except FileNotFoundError:
            sys.exit('Map file not found.')
        except json.JSONDecodeError:
            sys.exit('Error decoding the map file.')

    """This function writes changes in game data (game state)
    back to the JSON file"""
    def modify_map(self, game_data):
        with open('map_copy.json', 'w') as f:
            json.dump(game_data, f, indent=4)

    """This function moves the player to a new room in the specified direction.
    If there's a required item to enter the room,
    the player must possess it to enter."""
    def move_player(self, direction):
        new_room_name = self.current_room.move_player(direction)
        if new_room_name:
            new_room_data = self.data["rooms"].get(new_room_name)
            required_item = new_room_data.get("requiredItem")

            if required_item != "none":
                if required_item not in self.data["inventory"]:
                    print(self.data['rooms'][new_room_name]['failToEnter'])
                    return

            self.npc_interactions(new_room_name)

            self.current_room = Room(new_room_data, self.data)
            self.current_room.describe_room()

    """This function defines the interactions with the enemies-npcs
    and the thieves-npcs in the room."""
    def npc_interactions(self, room_name):
        npc_type = self.data['rooms'][room_name].get('npcType')
        if npc_type != "none":
            if self.data['npcs'][npc_type].get('toDefeat') in self.data["inventory"]:
                print(self.data['npcs'][npc_type].get('youWin'))
                if self.data['npcs'][npc_type] == "enemies":
                    self.data['rooms'][room_name]['npcType'] = 'none'
                    self.data['rooms'][room_name]['npc'] = 'none'
            else:
                if npc_type == "enemies":
                    print(self.data['npcs'][npc_type].get('youLose'))
                    self.restart_game()
                if npc_type == "thieves":
                    item_to_remove = self.data['npcs'][npc_type]["desires"]
                    if item_to_remove in self.data['inventory']:
                        self.data['inventory'].remove(item_to_remove)
                        self.modify_map(self.data)
                        print(self.data['npcs'][npc_type].get('youLose'))
                    else:
                        print(self.data['npcs'][npc_type].get('youCannotLose'))
                        self.modify_map(self.data)

    """This function allows the player to examine their surroundings,
    giving a description of what's in each direction."""
    def look_around(self):
        for direction in ['north', 'south', 'west', 'east']:
            if direction in self.current_room.room_data:
                print(f'To the {direction} you see a {self.current_room.room_data[direction]}')

    def play(self):
        # Instead of getting input and printing output directly, you call
        # methods passed in as arguments. This allows the Game to be used
        # with or without a GUI.
        print("lol")
        self.append_text(self.data['openning'])
        self.current_room.describe_room()
        # No loop here. The GUI will take care of looping for us.

    def process_command(self, command, output_func):
        command = command.split()

        if len(command) == 0:
            output_func(self.data['genericMsgs']['missingCmd'])
            return

        full_directions = {'n': 'north', 's': 'south', 'w': 'west', 'e': 'east',
                        'h': 'help', 'i': 'inventory', 'l': 'look'}
        action = full_directions.get(command[0].lower(), command[0].lower())

        if action in self.command_palette:
            if action in ['inventory', 'look', 'help', 'quit', 'restart']:
                self.command_palette[action]()
            elif action in ['north', 'south', 'west', 'east']:
                self.command_palette[action](action)
            else:
                item = ' '.join(command[1:])
                self.command_palette[action](item, self.current_room)
        else:
            output_func(self.data['genericMsgs']['invalidCmd'])

        if self.current_room.room_data.get('name') == 'exit':
            self.restart_game()

        # Ensure the room is described again after a command is processed.
        self.current_room.describe_room()

    def print_help(self):
        print(self.data['genericMsgs']['helpCmd'])

    def restart_game(self):
        print("Game has successfully been restarted")
        self.__init__(self.map_file)

    def quit_game(self):
        if os.path.exists('map_copy.json'):
            os.remove('map_copy.json')
        print("Quitting the game...")


class Room:
    def __init__(self, room_data, data):
        self.room_data = room_data
        self.data = data

    """This function is called when player enters a room"""
    def describe_room(self):
        print(self.room_data['description'])
        if self.room_data['items']:
            print('You see: ' + ', '.join(self.room_data['items']))

    """This function checks if a move in the given direction is possible.
    If not, it informs the player they've hit a dead end."""
    def move_player(self, direction):
        if direction in self.room_data:
            return self.room_data[direction]
        else:
            print(self.data['genericMsgs']['deadend'])
            return None


class Player:
    def __init__(self, data, game):
        self.data = data
        self.game = game

    def pick_up_item(self, item, room):
        if item in room.room_data['items']:
            self.data['inventory'].append(item)
            room.room_data['items'].remove(item)
            self.game.modify_map(self.data)
            print(f'You now have the {item}.')
        else:
            print(self.data['genericMsgs']['noItemHere'])

    """This function allows the player to use an item from their inventory.
    If the room has a trader NPC,
    the player can trade with the NPC."""
    def use_item(self, item, current_room):
        if item in self.data['inventory']:
            npc_type = current_room.room_data.get('npcType')

            if npc_type == 'traders':
                if item == self.data['npcs'][npc_type]['desires']:
                    self.data['inventory'].remove(item)
                    sells_item = self.data['npcs'][npc_type]['sells']
                    self.data['inventory'].append(sells_item)
                    self.game.modify_map(self.data)
                    print(f"You successfully traded your {item} with the {sells_item}!")
            else:
                print(f"You can't use your {item} here, try in a different room!")
        else:
            print('You do not have such item in your inventory.')

    def check_inventory(self):
        if not self.data['inventory']:
            print(self.data['genericMsgs']['emptyInventory'])
        else:
            print('You have: ' + ', '.join(self.data['inventory']))


if __name__ == '__main__':
    game = Game('orig_map.json')
    win = GameWindow(game)
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
    game.play()