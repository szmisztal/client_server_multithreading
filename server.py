import socket as s
import threading
from variables import HOST, PORT, INTERNET_ADDRESS_FAMILY, SOCKET_TYPE, BUFFER
from data_utils import DataUtils


class ClientHandler(threading.Thread):
    def __init__(self, client_socket, address, thread_id):
        super().__init__()
        self.data_utils = DataUtils()
        self.client_socket = client_socket
        self.address = address
        self.thread_id = thread_id

    def welcome_message(self):
        message = {"OK": self.thread_id}
        message_json = self.data_utils.serialize_to_json(message)
        self.client_socket.sendall(message_json)

    def send_ping_message_and_shut_down_the_thread(self):
        message = "PING"
        message_json = self.data_utils.serialize_to_json(message)
        self.client_socket.sendall(message_json)
        response_json = self.client_socket.recv(BUFFER)
        response = self.data_utils.deserialize_json(response_json)
        print(response)
        self.client_socket.close()


class Server():
    def __init__(self):
        self.HOST = HOST
        self.PORT = PORT
        self.INTERNET_ADDRESS_FAMILY = INTERNET_ADDRESS_FAMILY
        self.SOCKET_TYPE = SOCKET_TYPE
        self.is_running = True
        self.lock = threading.Lock()
        self.clients_list = []

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
                        thread = ClientHandler(client_socket, address, len(self.clients_list) + 1)
                        self.clients_list.append(thread)
                        thread.start()
                        thread.welcome_message()
                        self.lock.release()
                        if len(self.clients_list) >= 100:
                            for thread in self.clients_list:
                                thread.client_socket.settimeout(5)
                                try:
                                    self.lock.acquire()
                                    thread.send_ping_message_and_shut_down_the_thread()
                                    self.lock.release()
                                except thread.client_socket.timeout as e:
                                    print(f"Error: {e}, thread: {thread.thread_id} does not respond")
                                    thread.client_socket.close()
                            self.is_running = False
                    except Exception as e:
                        print(f"Error: {e}")
            except KeyboardInterrupt:
                print("Server stopped by user.")
            finally:
                print("Server`s down...")
                server_socket.close()


if __name__ == "__main__":
    server = Server()
    server.start()
