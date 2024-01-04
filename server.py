import socket as s
import threading
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
        self.encode_format = encode_format
        self.is_running = True
        self.lock = threading.Lock()
        self.clients_list = []

    def client_thread(self, client_socket):
        message = {"OK": len(self.clients_list)}
        message_json = self.data_utils.serialize_to_json(message)
        client_socket.sendall(message_json)

    def send_ping_message_and_shut_down_server(self):
        message = "PING"
        message_json = self.data_utils.serialize_to_json(message)
        for client_socket in self.clients_list:
            client_socket.settimeout(5)
            try:
                self.lock.acquire()
                client_socket.sendall(message_json)
                response_json = client_socket.recv(BUFFER)
                response = self.data_utils.deserialize_json(response_json)
                print(response)
                client_socket.close()
                self.lock.release()
            except client_socket.timeout as e:
                print(f"Error: {e}")
                client_socket.close()

    def start(self):
        with s.socket(self.INTERNET_ADDRESS_FAMILY, self.SOCKET_TYPE) as server_socket:
            print("SERVER'S UP...")
            server_socket.bind((self.HOST, self.PORT))
            server_socket.listen()
            try:
                while self.is_running:
                    client_socket, address = server_socket.accept()
                    try:
                        self.lock.acquire()
                        self.clients_list.append(client_socket)
                        thread = threading.Thread(target = self.client_thread, args = (client_socket, ))
                        thread.start()
                        self.lock.release()
                        if len(self.clients_list) >= 100:
                            self.send_ping_message_and_shut_down_server()
                            self.is_running = False
                    except Exception as e:
                        print(f"Error: {e}")
            except KeyboardInterrupt:
                print("Server stopped by user.")
            finally:
                server_socket.close()


if __name__ == "__main__":
    server = Server()
    server.start()
