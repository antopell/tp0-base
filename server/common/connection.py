import socket
import logging
import signal

from protocol.protocol import *
from common.utils import *
from multiprocessing import Condition, Value, Process, Lock



class Connection():
  def __init__(self, client_sock, has_winners, amount_agencies, clients_map, winners_map, lock_bets):
    self.client_sock = client_sock
    self.has_winners = has_winners
    self.protocol = Protocol()
    self.amount_agencies = amount_agencies
    self.clients_map = clients_map
    self.winners_map = winners_map
    self.lock_bets = lock_bets

  def _graceful_exit(self, _sig, _frame):
    self.client_sock.close()
    exit(0)

  def run(self):
    """
    Read message from a specific client socket and closes the socket

    If a problem arises in the communication with the client, the
    client socket will also be closed
    """
    signal.signal(signal.SIGTERM, self._graceful_exit)
    signal.signal(signal.SIGINT, self._graceful_exit)
    try:
      batch_ended = False
      agency_number = -1
      while not batch_ended:
        action, message = self.__get_action()
        if action == ActionType.CLOSE:
          break
        if action == ActionType.WAIT_FOR_WINNERS:
          agency_number = self.__get_confirmation(message)
          break
        
        # action == ActionType.GET_BETS:
        bets, amount, batch_ended = self.__get_bets(message)
        with self.lock_bets:
          store_bets(bets)

        if not batch_ended:
          success = len(bets) == amount
          if success:
            logging.info(f'action: apuesta_recibida | result: success | cantidad: {len(bets)}')
          else:
            logging.info(f'action: apuesta_recibida | result: fail | cantidad: {len(bets)}')
      
          self.__send_ack(success)
      
      self.clients_map.update({agency_number: self.client_sock})

      with self.has_winners:
        if len(self.clients_map) == self.amount_agencies:
          self.__define_winners()
        
        self.has_winners.wait()
        self.__send_winners(agency_number)
    except OSError as e:
      logging.error(f"action: receive_message | result: fail | error: {e}")
    finally:
      self.client_sock.close()

  def __define_winners(self):
      logging.info("action: sorteo | result: success")
      for winning_bet in load_bets():
        winner_list = self.winners_map.get(winning_bet.agency, [])
        if not has_won(winning_bet):
          continue
        winner_list.append(winning_bet.document)
        self.winners_map.update({winning_bet.agency: winner_list})
      self.has_winners.notify_all()
  
  def __get_action(self) -> ActionType: 
    read_amount = self.protocol.define_action_buffer_size()
    action = bytearray()
    closed_socket = self.__full_recv(action, read_amount)
    
    if closed_socket:
        return ActionType.CLOSE, action
    return self.protocol.decode_action(action), action

  def __get_bets(self, action: bytearray):
    read_amount = self.protocol.define_initial_buffer_size()
    message = action
    closed_socket = self.__full_recv(message, read_amount)
    if closed_socket:
        return [], 0, closed_socket
    read_amount = self.protocol.define_msg_len(message)
    closed_socket = self.__full_recv(message, read_amount)
    bets, amount_bets = self.protocol.decode(message)
    return bets, amount_bets, closed_socket
  
  def __full_recv(self, buffer: bytearray, amount_to_read: int) -> bool:
    amount_read = 0
    while amount_read < amount_to_read:
      msg = self.client_sock.recv(amount_to_read - amount_read)
      if len(msg) == 0:
        return True
      buffer.extend(msg)
      amount_read += len(msg)
    return False

  def __send_ack(self, result: bool):
    message = self.protocol.create_ack_msg(result)
    self.client_sock.sendall(message)

  def __get_confirmation(self, action: bytearray) -> int:
    read_amount = self.protocol.define_buffer_size_confirmation()
    message = action
    closed_socket = self.__full_recv(message, read_amount)
    if closed_socket:
      return -1
    return self.protocol.decode_confirmation(message)
    
  def __send_winners(self, agency_number):
    message = self.protocol.create_winners_msg(self.winners_map.get(agency_number, []))
    try: 
      self.client_sock.sendall(message)
    except OSError as e:
      logging.error(f"action: send_winners | result: fail | error: {e}")
    finally:
      self.client_sock.close()