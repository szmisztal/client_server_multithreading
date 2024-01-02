import threading
import schedule
from threading import Lock
from data_utils import DataUtils
from variables import BUFFER


class ConnectionPool:
    def __init__(self, server, min_numbers_of_connections, max_number_of_connections):
        self.server = server
        self.connections_list = []
        self.connections_in_use_list = []
        self.lock = Lock()
        self.min_number_of_connections = min_numbers_of_connections
        self.max_number_of_connections = max_number_of_connections
        self.create_start_connections()
        self.connections_manager()

    def create_start_connections(self):
        for _ in range(self.min_number_of_connections):
            connection = ClientHandler(None, None)
            self.connections_list.append(connection)

    def get_connection(self, client_socket, address):
        self.lock.acquire()
        try:
            for connection in self.connections_list:
                if connection.in_use == False:
                    connection.in_use = True
                    connection.client_socket = client_socket
                    connection.address = address
                    self.connections_in_use_list.append(connection)
                    self.connections_list.remove(connection)
                    return connection
            if len(self.connections_list) < self.max_number_of_connections \
                    and len(self.connections_list) + len(self.connections_in_use_list) < self.max_number_of_connections:
                new_connection = ClientHandler(client_socket, address)
                new_connection.in_use = True
                self.connections_in_use_list.append(new_connection)
                return new_connection
            elif len(self.connections_list) + len(self.connections_in_use_list) >= self.max_number_of_connections:
                return False
        finally:
            self.lock.release()

    def release_connection(self, connection):
        self.lock.acquire()
        try:
            if connection in self.connections_in_use_list:
                connection.in_use = False
                connection.client_socket = None
                connection.address = None
                self.connections_in_use_list.remove(connection)
                self.connections_list.append(connection)
        finally:
            self.lock.release()

    def destroy_unused_connections(self):
        self.lock.acquire()
        try:
            for connection in self.connections_list:
                if len(self.connections_list) > 11:
                    self.connections_list.remove(connection)
                    if len(self.connections_list) == 10:
                        break
        finally:
            self.lock.release()

    def keep_connections_at_the_starting_level(self):
        if len(self.connections_list) < self.min_number_of_connections:
            for _ in self.connections_list:
                connection = ClientHandler(None, None)
                self.connections_list.append(connection)
                if len(self.connections_list) == self.min_number_of_connections:
                    break

    def connections_manager(self):
        schedule.every(1).minute.do(self.keep_connections_at_the_starting_level)
        schedule.every(1).minute.do(self.destroy_unused_connections)


class ClientHandler(threading.Thread):
    _id_counter = 0

    def __init__(self, client_socket, address):
        super().__init__()
        self.client_socket = client_socket
        self.address = address
        self.BUFFER = BUFFER
        self.in_use = False
        self.data_utils = DataUtils()
        self.thread_id = self.generate_thread_id()

    @classmethod
    def generate_thread_id(cls):
        cls._id_counter += 1
        return cls._id_counter

    def stop_message(self):
        response_to_client = "PING"
        response_to_client_json = self.data_utils.serialize_to_json(response_to_client)
        self.client_socket.sendall(response_to_client_json)
        response_from_client_json = self.client_socket.recv(self.BUFFER)
        response_from_client = self.data_utils.deserialize_json(response_from_client_json)
        print(response_from_client)
        self.client_socket.close()

    def run(self):
        response_to_client = {"OK": self.thread_id}
        response_to_client_json = self.data_utils.serialize_to_json(response_to_client)
        self.client_socket.sendall(response_to_client_json)

