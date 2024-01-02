import socket as s
from connection_pool import ConnectionPool
from variables import HOST, PORT, INTERNET_ADDRESS_FAMILY, SOCKET_TYPE, BUFFER, encode_format
from data_utils import DataUtils


class Server():
    def __init__(self):
        self.HOST = HOST
        self.PORT = PORT
        self.INTERNET_ADDRESS_FAMILY = INTERNET_ADDRESS_FAMILY
        self.SOCKET_TYPE = SOCKET_TYPE
        self.BUFFER = BUFFER
        self.data_utils = DataUtils()
        self.connection_pool = ConnectionPool(self, 10, 100)
        self.encode_format = encode_format
        self.is_running = True

    def start(self):
        with s.socket(self.INTERNET_ADDRESS_FAMILY, self.SOCKET_TYPE) as server_socket:
            print("SERVER'S UP...")
            server_socket.bind((self.HOST, self.PORT))
            server_socket.listen()
            try:
                while self.is_running:
                    client_socket, address = server_socket.accept()
                    try:
                        client_handler = self.connection_pool.get_connection(client_socket, address)
                        client_handler.run()
                        if len(self.connection_pool.connections_in_use_list) >= 100:
                            connections_to_close = list(self.connection_pool.connections_in_use_list)
                            for handler in connections_to_close:
                                handler.stop_message()
                                self.connection_pool.release_connection(handler)
                                self.is_running = False
                    except Exception as e:
                        print(f"Error handling client {address}: {e}")
            except KeyboardInterrupt:
                print("Server stopped by user.")
            finally:
                server_socket.close()


if __name__ == "__main__":
    server = Server()
    server.start()
