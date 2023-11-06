import socket
import signal
import sys

# Hard code Discovery Server address as requested

IP = "127.0.0.1"  # LocalHost
PORT = 2002

discoverySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

Rooms = {}

# Signal handler for graceful exiting.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    sys.exit(0)


# To register a Room server to the discovery network

def Register(room, name):
    try:
        Rooms[name] = room
    except:
        return "NOTOK"
    return "OK"


# To DeRegister a Room Server from the discovery network

def DeRegister(name):
    try:
        Rooms.pop(name)
    except:
        return "NOTOK"
    return "OK"


# To send out address of room when asked

def Lookup(name):
    try:
        return Rooms[name]
    except KeyError:
        return "NOT FOUND"
    except:
        return "NOTOK"

# Process incoming message.

def ProcessMessage(message, addr):
    words = message.split()

    if words[0] == "join":
        if len(words) == 3:
            print("connection from {}".format(addr))
            return "OK"
        elif len(words) == 2:
            print("{} has joined from {}".format(words[1], addr))
            return "OK"
        else:
            return "NOTOK"

    elif words[0] == "REGISTER":
        if len(words) == 3:
            return Register(words[1], words[2])
        else:
            return "NOTOK"

    elif words[0] == "DEREGISTER":
        if len(words) == 2:
            return DeRegister(words[1])
        else:
            return "NOTOK"

    elif words[0] == "LOOKUP":
        if len(words) == 2:
            return Lookup(words[1])
        else:
            return "NOTOK"

    else:
        return "NOTOK"


# main function

def main():
    signal.signal(signal.SIGINT, signal_handler)

    discoverySocket.bind((IP, PORT))

    print(f"Discovery will wait for servers and players at port: {PORT}")

    while True:
        message, addr = discoverySocket.recvfrom(1024)

        response = ProcessMessage(message.decode(), addr)

        discoverySocket.sendto(response.encode(), addr)


if __name__ == '__main__':
    main()
