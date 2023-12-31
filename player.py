import socket
import signal
import sys
import argparse
from urllib.parse import urlparse
import selectors

# Selector for helping us select incoming data from the server and messages typed in by the user.

sel = selectors.DefaultSelector()

# Socket for sending messages.

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server Room Address and Discovery Server Address.

room_server = ('', '')
disco_server = ('localhost', 2002)

# User name for tagging sent messages & room name

name = ''
room = ''

# Inventory of items.

inventory = []

# Directions that are possible.

connections = {
    "north": "",
    "south": "",
    "east": "",
    "west": "",
    "up": "",
    "down": ""
}


# Signal handler for graceful exiting.  Let the server know when we're gone.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    message = 'exit'
    client_socket.sendto(message.encode(), room_server)
    for item in inventory:
        message = f'drop {item}'
        client_socket.sendto(message.encode(), room_server)
    sys.exit(0)


# Simple function for setting up a prompt for the user.

def do_prompt(skip_line=False):
    if (skip_line):
        print("")
    print("> ", end='', flush=True)


# Function to join a room.

def join_room(number):
    global room_server

    message = f"join {name}"
    client_socket.settimeout(5)
    if number == 0:
        client_socket.sendto(message.encode(), disco_server)
    elif number == 1:
        client_socket.sendto(message.encode(), room_server)
    if number == 0 or number == 1:
        try:
            response, addr = client_socket.recvfrom(1024)
        except OSError as msg:
            print('Something bad happened')
            sys.exit()
        if response.decode() != "OK":
            print(response.decode())

    if number == 0 or number == 2:
        message = f"LOOKUP {room}"
        client_socket.sendto(message.encode(), disco_server)
        response, addr = client_socket.recvfrom(1024)

        server_address = urlparse(response.decode())

        if (server_address.scheme != 'room') or (server_address.port == None) or (server_address.hostname == None):
            raise ValueError
        host = server_address.hostname
        port = server_address.port
        room_server = (host, port)

        join_room(1)


# Function to handle commands from the user, checking them over and sending to the server as needed.

def process_command(command):
    global room_server
    global room

    # Parse command.

    words = command.split()

    # Check if we are dropping something.  Only let server know if it is in our inventory.

    if (words[0] == 'drop'):
        if (len(words) != 2):
            print("Invalid command")
            return
        elif (words[1] not in inventory):
            print(f'You are not holding {words[1]}')
            return

    # Send command to server, if it isn't a local only one.

    if (command != 'inventory'):
        message = f'{command}'
        client_socket.sendto(message.encode(), room_server)

    # Check for particular commands of interest from the user.

    # If we exit, we have to drop everything in our inventory into the room.

    if (command == 'exit'):
        for item in inventory:
            message = f'drop {item}'
            client_socket.sendto(message.encode(), room_server)
        sys.exit(0)

    # If we look, we will be getting the room description to display.

    elif (command == 'look'):
        response, addr = client_socket.recvfrom(1024)
        print(response.decode())

    # If we inventory, we never really reached out to the room, so we just display what we have.

    elif (command == 'inventory'):
        print("You are holding:")
        if (len(inventory) == 0):
            print('  No items')
        else:
            for item in inventory:
                print(f'  {item}')

    # If we take an item, we let the server know and put it in our inventory, assuming we could take it.

    elif (words[0] == 'take'):
        response, addr = client_socket.recvfrom(1024)
        print(response.decode())
        words = response.decode().split()
        if ((len(words) == 2) and (words[1] == 'taken')):
            inventory.append(words[0])

    # If we drop an item, we remove it from our inventory and give it back to the room.

    elif (words[0] == 'drop'):
        response, addr = client_socket.recvfrom(1024)
        print(response.decode())
        inventory.remove(words[1])

    # If we're wanting to go in a direction, we check with the room and it will tell us if it's a valid
    # direction.  We can then join the new room as we know we've been dropped already from the other one.

    elif words[0] in connections:
        response, addr = client_socket.recvfrom(1024)
        if response.decode() == "NOTOK":
            print(f'You cannot go {words[0]} from this room.')
        else:
            room = response.decode()
            join_room(2)


    # The player wants to say something ... print the response.

    elif (words[0] == 'say'):
        response, addr = client_socket.recvfrom(1024)
        print(response.decode())

    # Otherwise, it's an invalid command so we report it.

    else:
        response, addr = client_socket.recvfrom(1024)
        print(response.decode())


# Function to handle incoming messages from room.  Also look for disconnect messages to shutdown.

def handle_message_from_server(sock, mask):
    response, addr = client_socket.recvfrom(1024)
    words = response.decode().split(' ')
    print()
    if len(words) == 1 and words[0] == 'disconnect':
        print('Disconnected from server ... exiting!')
        sys.exit(0)
    else:
        print(response.decode())
        do_prompt()


# Function to handle incoming messages from user.

def handle_keyboard_input(file, mask):
    line = sys.stdin.readline()[:-1]
    process_command(line)
    do_prompt()


# Our main function.

def main():
    global name
    global client_socket
    global room

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Check command line arguments to retrieve a URL.

    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name for the player in the game")
    parser.add_argument("room", help="name of room")
    args = parser.parse_args()

    # Check the URL passed in and make sure it's valid.  If so, keep track of
    # things for later.

    name = args.name
    room = args.room

    # Send message to enter the room.
    try:
        join_room(0)
    except ValueError:
        print("This room cannot be joined, closing client")
        sys.exit()

    # Set up our selector.

    # client_socket.setblocking(False)
    sel.register(client_socket, selectors.EVENT_READ, handle_message_from_server)
    sel.register(sys.stdin, selectors.EVENT_READ, handle_keyboard_input)

    # Prompt the user before beginning.

    do_prompt()

    # Now do the selection.

    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)


if __name__ == '__main__':
    main()
