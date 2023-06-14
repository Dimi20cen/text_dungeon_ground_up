import json
import sys


class Game:
    def __init__(self, map_file):
        self.map_file = map_file
        self.data = self.load_map(map_file)
        if not self.data:
            sys.exit('Error loading map file.')
        self.player = Player(self.data)
        self.current_room = Room(self.data["rooms"].get("start"), self.data)

        self.command_palette = {
            'north': self.move_player,
            'south': self.move_player,
            'west': self.move_player,
            'east': self.move_player,
            'take': self.player.pick_up_item,
            'use': self.player.use_item,
            'look': self.current_room.look_around,
            'inventory': self.player.check_inventory,
            'help': self.print_help,
            'restart': self.restart_game,
            'quit': self.quit_game
        }

    def load_map(self, filename):
        try:
            with open(filename, 'r') as f:
                game_data = json.load(f)
                return game_data
        except (FileNotFoundError, json.JSONDecodeError):
            print(f'Error loading file "{filename}" or not a valid JSON.')
            return None

    def move_player(self, direction):
        new_room = self.current_room.move_player(direction)
        if new_room:
            self.current_room = Room(self.data["rooms"].get(new_room), self.data)

    def play(self):
        print(self.data['openning'])
        while True:
            self.current_room.describe()
            command = input('>').split()
            print('')
            if len(command) == 0:
                print(self.data['genericMsgs']['missingCmd'])
                continue

            # Handle full-length direction commands
            full_directions = {'n': 'north', 's': 'south', 'w': 'west', 'e': 'east',
                               'h': 'help', 'i': 'inventory', 'l': 'look'}
            action = full_directions.get(command[0].lower(), command[0].lower())

            if action in self.command_palette:
                if action in ['inventory', 'look', 'help', 'quit', 'restart']:
                    self.command_palette[action]()
                elif action in ['north', 'south', 'west', 'east']:
                    self.command_palette[action](action)
                else:
                    try:
                        self.command_palette[action](command[1], self.current_room)
                    except:
                        print("Command should be followed by specific item. E.g. Sword")
            else:
                print(self.data['genericMsgs']['invalidCmd'])

    def print_help(self):
        print(self.data['genericMsgs']['helpCmd'])

    def restart_game(self):
        print("Game has successfully been restarted")
        self.__init__(self.map_file)

    def quit_game(self):
        sys.exit("Quitting the game...")

class Room:
    def __init__(self, room_data, data):
        self.room_data = room_data
        self.data = data 

    def describe(self):
        print(self.room_data['description'])
        if self.room_data['items']:
            print('You see: ' + ', '.join(self.room_data['items']))#############

    def move_player(self, direction):
        if direction in self.room_data:
            return self.room_data[direction]
        else:
            print(self.data['genericMsgs']['deadend'])
            return None

    def look_around(self):
        for direction in ['north', 'south', 'west', 'east']:
            if direction in self.room_data:
                print(f'To the {direction} you see a {self.room_data[direction]}')

class Player:
    def __init__(self, data):
        self.data = data
        self.inventory = []

    def pick_up_item(self, item, room):
        if item in room.room_data['items']:
            self.inventory.append(item)
            room.room_data['items'].remove(item)
            print(f'You now have the {item}.')#####
        else:
            print(self.data['genericMsgs']['noItemHere'])

    def use_item(self, item, current_room):
        if item in self.inventory:
            if item == 'key' and current_room.room_data['name'] == 'exit':
                print('You use the key and unlock the door. You have escaped!')
                exit()
            else:
                print(f'You use the {item}.')  # Add more item-usage logic here
        else:
            print('You do not have that item.')

    def check_inventory(self):
        if self.inventory == []:
            print('Your inventory is empty!')
        else:
            print('You have: ' + ', '.join(self.inventory))

if __name__ == '__main__':
    game = Game('map.json')
    game.play()
