import json
from socket import *

class ClientSocket:
    def __init__(self):
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)

    def recv_message(self, bytes):
        message, address = self.clientSocket.recvfrom(bytes)

        message_str = message.decode("utf-8")
        json_data = json.loads(message_str)

        return json_data, address

    def send_message(self, message, addr):
        if isinstance(message, str):
            self.clientSocket.sendto(message.encode('utf-8'), addr)
        else:
            print("Invalid format")

    def send_json_message(self, json_data, addr):
        try:
            self.clientSocket.sendto(json.dumps(json_data).encode('utf-8'), addr)
        except Exception:
            print("Invalid format")