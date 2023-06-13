import json
import sys

class Game:
    def __init__(self, map_file):
        self.map_file = map_file
        self.map = self.load_map(map_file)
        if not self.map:
            sys.exit('Error loading map file.')
        self.player = Player()
        self.current_room = self.map.get('start')
        if not self.current_room:
            sys.exit('Missing "start" key in map file.')
        self.command_palette = {
            'n': self.move_player,
            's': self.move_player,
            'w': self.move_player,
            'e': self.move_player,
            'take': self.player.pick_up_item,
            'use': self.player.use_item,
            # 'inspect': self.player.inspect_item,
            'l': self.current_room.look_around,
            'i': self.player.check_inventory,
            'help': self.print_help,
            'restart': self.restart_game,
            'quit': self.quit_game
        }

    def load_map(self, filename):
        try:
            with open(filename, 'r') as f:
                room_data = json.load(f).get('rooms')
            if not room_data:
                print('Missing "rooms" key in map file.')
                return None
            return {room_name: Room(room_data[room_name]) for room_name in room_data}
        except (FileNotFoundError, json.JSONDecodeError):
            print(f'Error loading file "{filename}" or not a valid JSON.')
            return None

    def move_player(self, direction):
        new_room = self.current_room.move_player(direction)
        if new_room:
            self.current_room = self.map.get(new_room)

    def play(self):
        while True:
            self.current_room.describe()
            command = input('>').split()
            print('')
            if len(command) == 0:
                print('Please input a command.')
                continue
            action = command[0].lower()
            args = command
            print(args)
            if action in self.command_palette:
                self.command_palette[action](*args)
            else:
                print('Invalid command.')

    def print_help(self):
        print('Commands: n, s, w, e, take [item], use [item], look, inventory, help, restart, quit')

    def restart_game(self):
        print("Game has successfully been restarted")
        self.__init__(self.map_file)

    def quit_game(self):
        exit()

class Room:
    def __init__(self, room_data):
        self.room_data = room_data

    def describe(self):
        print(self.room_data['description'])
        if self.room_data['items']:
            print('You see: ' + ', '.join(self.room_data['items']))

    def move_player(self, direction):
        if direction in self.room_data:
            return self.room_data[direction]
        else:
            print('You can\'t go that way.')
            return None

    def look_around(self):
        for direction in ['n', 's', 'w', 'e']:
            if direction in self.room_data:
                print(f'To the {direction} you see a {self.room_data[direction]}')

class Player:
    def __init__(self):
        self.inventory = []

    def pick_up_item(self, item, room):
        if item in room.room_data['items']:
            self.inventory.append(item)
            room.room_data['items'].remove(item)
            print(f'You now have the {item}.')
        else:
            print('There is no such item here.')

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
