import socket as s
from variables import HOST, PORT, INTERNET_ADDRESS_FAMILY, SOCKET_TYPE, BUFFER, encode_format
from data_utils import DataUtils


class Client:
    def __init__(self):
        self.HOST = HOST
        self.PORT = PORT
        self.INTERNET_ADDRESS_FAMILY = INTERNET_ADDRESS_FAMILY
        self.SOCKET_TYPE = SOCKET_TYPE
        self.BUFFER = BUFFER
        self.encode_format = encode_format
        self.data_utils = DataUtils()
        self.is_running = True
        self.id = None

    def start(self):
        with s.socket(INTERNET_ADDRESS_FAMILY, SOCKET_TYPE) as client_socket:
            print("CLIENT`S UP...")
            try:
                client_socket.connect((self.HOST, self.PORT))
                while self.is_running:
                    message_from_server = client_socket.recv(self.BUFFER)
                    message = self.data_utils.deserialize_json(message_from_server)
                    print(message)
                    if message == "PING":
                        response_to_server = f"PONG: {self.id}"
                        response_to_server_json = self.data_utils.serialize_to_json(response_to_server)
                        client_socket.sendall(response_to_server_json)
                        self.is_running = False
                    else:
                        self.id = message["OK"]
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                client_socket.close()


if __name__ == "__main__":
    client = Client()
    client.start()
