# Multi-Room_Chat_Game

This project consists of a text-based multiplayer game where players can interact in different "rooms," take and drop items, and communicate with each other. The system is composed of three main components:

discovery.py: Manages the directory of available rooms.
room.py: Handles the state and interactions within a single room.
player.py: A client interface for a player to join rooms and interact with the game.

Getting Started
Prerequisites
Python 3.x installed on your system.
Access to a command line interface (CLI) or terminal.

Running the Discovery Server
Open a terminal.
Navigate to the directory containing discovery.py.
Run the server using Python:
  python discovery.py
  
Starting a Room Server
Open a new terminal window.
Navigate to the directory containing room.py.
Run the following command with the desired arguments:
  python room.py "Room Name" "Room Description" [Item1 Item2 ...]

Optional flags for room connections:
-n: Connecting room to the north.
-s: Connecting room to the south.
-e: Connecting room to the east.
-w: Connecting room to the west.
-u: Connecting room upwards.
-d: Connecting room downwards.


Connecting as a Player
Open a new terminal window.
Navigate to the directory containing player.py.
Start the player client using Python:
python player.py
Follow the on-screen prompts to navigate through the game.

Features
Players can join or leave rooms.
Look around to see room descriptions and items.
Take or drop items within rooms.
Move to other rooms by going in the specified directions.
Communicate with other players in the same room.
Discovery server to keep track of all active rooms.

Commands
join: Enter a room.
exit: Leave the room.
look: Get a description of the room and see items/players.
take <item>: Take an item present in the room.
drop <item>: Drop an item into the room.
say <message>: Communicate with others in the room.
<direction>: Move in a specified direction if the room has a connection.
Graceful Shutdown
Use Ctrl+C in the terminal running room.py to trigger a graceful shutdown, which will deregister the room from the discovery server and notify all connected clients.

Author
Joel Daniel
