from socket import *
import json

IP = '127.0.0.1'
SERVER_PORT = 4396
address = (IP, SERVER_PORT)
BUFFER_LENGTH = 512

dataSocket = socket(AF_INET, SOCK_DGRAM)

message = {
    'Type': 0,
    '1': 'admin',
    '2': 'admin'
}

message = json.dumps(message).encode()
dataSocket.sendto(message, address)