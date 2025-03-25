import socket
import logging
import signal

from protocol.protocol import *
from common.utils import *

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.continue_running = True
        self.protocol = Protocol()

    def _graceful_exit(self, _sig, _frame):
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        self.continue_running = False
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

        while self.continue_running:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            batch_ended = False
            while not batch_ended:
                bets = self.__getMessage(client_sock)
                store_bets(bets)
                logging.info(f'action: apuesta_almacenada | result: success | dni: {bets[0].document} | numero: {bets[0].number}')
                
                self.__send_ack(True, client_sock)
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.shutdown(socket.SHUT_WR) # allows reading
            client_sock.close()

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
    
    def __getMessage(self, client_sock: socket.socket):
        read_amount = self.protocol.define_initial_buffer_size()
        message = bytearray()
        self.__full_recv(message, read_amount, client_sock)
        
        read_amount = self.protocol.define_msg_len(message)
        self.__full_recv(message, read_amount, client_sock)

        return self.protocol.decode(message)
        
    def __full_recv(self, buffer: bytearray, amount_to_read: int, socket: socket.socket):
        amount_read = 0
        while amount_read < amount_to_read:
            msg = socket.recv(amount_to_read - amount_read)
            buffer.extend(msg)
            amount_read += len(msg)
    
    def __send_ack(self, result: bool, socket: socket.socket):
        message = self.protocol.create_ack_msg(result)
        socket.sendall(message)
