import socket
import logging
import signal

from protocol.protocol import *
from common.utils import *

AMOUNT_AGENCIES = 5


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

        clients_map = dict()
        while self.continue_running or len(clients_map) == AMOUNT_AGENCIES:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(clients_map, client_sock)
        
        logging.info("action: sorteo | result: success")
        clients_winners_map = dict()
        for winning_bet in load_bets():
            if not has_won(winning_bet):
                continue
            winner_list = clients_winners_map.get(winning_bet.agency, [])
            winner_list.append(winning_bet.document)        


    def __handle_client_connection(self, clients_map, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            batch_ended = False
            agency_number = -1
            while not batch_ended:
                action, message = self.__get_action(client_sock)
                if action == ActionType.CLOSE:
                    break
                if action == ActionType.WAIT_FOR_WINNERS:
                    agency_number = self.__get_confirmation(client_sock, message)
                    break
                
                # action == ActionType.GET_BETS:
                bets, amount, batch_ended = self.__get_bets(client_sock, message)
                store_bets(bets)
                if not batch_ended:
                    success = len(bets) == amount
                    if success:
                        logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(bets)}')
                    else:
                        logging.info(f'action: apuesta_recibida | result: fail | cantidad: {len(bets)}')
                
                    self.__send_ack(success, client_sock)
            
            clients_map[agency_number] = client_sock
            logging.info(f"map: {clients_map} | agency_number: {agency_number}")
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            # client_sock.shutdown(socket.SHUT_WR) # allows reading
            # client_sock.close()
            pass

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
    
    def __get_action(self, client_sock: socket.socket) -> ActionType: 
        read_amount = self.protocol.define_action_buffer_size()
        action = bytearray()
        closed_socket = self.__full_recv(action, read_amount, client_sock)
        
        if closed_socket:
            return ActionType.CLOSE, action
        return self.protocol.decode_action(action), action

    def __get_bets(self, client_sock: socket.socket, action: bytearray):
        read_amount = self.protocol.define_initial_buffer_size()
        message = action
        closed_socket = self.__full_recv(message, read_amount, client_sock)
        if closed_socket:
            return [], 0, closed_socket
        read_amount = self.protocol.define_msg_len(message)
        closed_socket = self.__full_recv(message, read_amount, client_sock)
        bets, amount_bets = self.protocol.decode(message)
        return bets, amount_bets, closed_socket
        
    def __full_recv(self, buffer: bytearray, amount_to_read: int, socket: socket.socket) -> bool:
        amount_read = 0
        while amount_read < amount_to_read:
            msg = socket.recv(amount_to_read - amount_read)
            if len(msg) == 0:
                return True
            buffer.extend(msg)
            amount_read += len(msg)
        return False
    
    def __send_ack(self, result: bool, socket: socket.socket):
        message = self.protocol.create_ack_msg(result)
        socket.sendall(message)

    def __get_confirmation(self, client_sock: socket.socket, action: bytearray) -> int:
        read_amount = self.protocol.define_buffer_size_confirmation()
        message = action
        closed_socket = self.__full_recv(message, read_amount, client_sock)
        if closed_socket:
            return -1
        return self.protocol.decode_confirmation(message)
    