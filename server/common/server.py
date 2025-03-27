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
    
    # def __get_action(self, client_sock: socket.socket) -> ActionType: 
    #     read_amount = self.protocol.define_action_buffer_size()
    #     action = bytearray()
    #     closed_socket = self.__full_recv(action, read_amount, client_sock)
        
    #     if closed_socket:
    #         return ActionType.CLOSE, action
    #     return self.protocol.decode_action(action), action

    # def __get_bets(self, client_sock: socket.socket, action: bytearray):
    #     read_amount = self.protocol.define_initial_buffer_size()
    #     message = action
    #     closed_socket = self.__full_recv(message, read_amount, client_sock)
    #     if closed_socket:
    #         return [], 0, closed_socket
    #     read_amount = self.protocol.define_msg_len(message)
    #     closed_socket = self.__full_recv(message, read_amount, client_sock)
    #     bets, amount_bets = self.protocol.decode(message)
    #     return bets, amount_bets, closed_socket
        
    # def __full_recv(self, buffer: bytearray, amount_to_read: int, socket: socket.socket) -> bool:
    #     amount_read = 0
    #     while amount_read < amount_to_read:
    #         msg = socket.recv(amount_to_read - amount_read)
    #         if len(msg) == 0:
    #             return True
    #         buffer.extend(msg)
    #         amount_read += len(msg)
    #     return False
    
    # def __send_ack(self, result: bool, socket: socket.socket):
    #     message = self.protocol.create_ack_msg(result)
    #     socket.sendall(message)

    # def __get_confirmation(self, client_sock: socket.socket, action: bytearray) -> int:
    #     read_amount = self.protocol.define_buffer_size_confirmation()
    #     message = action
    #     closed_socket = self.__full_recv(message, read_amount, client_sock)
    #     if closed_socket:
    #         return -1
    #     return self.protocol.decode_confirmation(message)
    
    # def __send_winners(self, socket: socket.socket, agency_number, has_winners):
    #     with has_winners:
    #         logging.info("PRE WAIT")
    #         has_to_wait = True
    #         with self.has_winners.get_lock():
    #             has_to_wait = not self.has_winners.value

    #         if has_to_wait:
    #             has_winners.wait()
    #         logging.info("POST WAIT")

    #         message = self.protocol.create_winners_msg(self.winners_map[agency_number])
    #         try: 
    #             socket.sendall(message)
    #         except OSError as e:
    #             logging.error(f"action: send_winners | result: fail | error: {e}")
    #         finally:
    #             # socket.shutdown(socket.SHUT_WR) # allows reading
    #             socket.close()
            