import socket
import logging
import signal
from multiprocessing import Condition, Value, Process, Manager, Lock
from ctypes import c_bool

from protocol.protocol import *
from common.utils import *
from common.connection import *

class Server:
    def __init__(self, port, listen_backlog, amount_agencies):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.continue_running = True
        self.protocol = Protocol()
        self.amount_agencies = int(amount_agencies)
        self.processes = []

    def _graceful_exit(self, _sig, _frame):
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        self.continue_running = False
        self.__kill_processes()
        exit(0)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        # Handle signal to graceful shutdown the server
        signal.signal(signal.SIGTERM, self._graceful_exit)
        signal.signal(signal.SIGINT, self._graceful_exit)

        winners_ready = Value(c_bool, False)
        has_winners = Condition()
        lock_bets = Lock()
        
        with Manager() as manager:
            clients_map = manager.dict()
            winners_map = manager.dict()

            
            while self.continue_running:
                self.__remove_closed_processes()
                client_sock = self.__accept_new_connection()
                client = Connection(client_sock, has_winners, winners_ready, self.amount_agencies, clients_map, winners_map, lock_bets)
                process = Process(target=client.run)
                self.processes.append(process)
                process.start()
        
        
    def __remove_closed_processes(self):
        active_processes = []
        for process in self.processes:
            if not process.is_alive():
               process.join()
            else:
                active_processes.append(process)

        self.processes = active_processes

    def __kill_processes(self):
        for process in self.processes:
            if not process.is_alive():
               process.join()
            else:
                process.terminate()
                process.join()


    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
    