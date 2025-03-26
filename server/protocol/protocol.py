from common.utils import *
import logging

BATCH_BET_CODE = 2
AGENCY_BATCH_CODE = 2

BET_CODE = 1
AGENCY_CODE = 1
NAME_CODE = 2
SURNAME_CODE = 3
DOCUMENT_CODE = 4
BIRTHDATE_CODE = 5
BETNUMBER_CODE = 6

ACK_BET_CODE = 3

INT_LENGTH = 4
CODE_LENGTH = 2
ISODATE_LENGTH = 10
BOOL_LENGTH = 1

class Protocol:
  def __init__(self):
    pass
    

  def define_initial_buffer_size(self):
    return CODE_LENGTH + INT_LENGTH 
  
  def define_msg_len(self, initial_msg: bytearray):
    msg_code = int.from_bytes(initial_msg[:CODE_LENGTH ], byteorder='big')
    msg_len = int.from_bytes(initial_msg[CODE_LENGTH:CODE_LENGTH + INT_LENGTH ], byteorder='big')
    return msg_len
  
  def decode(self, msg: bytearray):
    msg_code = int.from_bytes(msg[:CODE_LENGTH], byteorder='big')

    final_msg = []
    if msg_code == BET_CODE:
      bet, _ = self.__decode_bet_msg(msg, CODE_LENGTH)
      final_msg.append(bet)
    elif msg_code == BATCH_BET_CODE:
      final_msg.extend(self.__decode_batch_bet_msg(msg))
    return final_msg
  

  def __decode_batch_bet_msg(self, msg) -> int:
    amount_read = CODE_LENGTH
    msg_len = int.from_bytes(msg[amount_read:amount_read + INT_LENGTH ], byteorder='big')
    
    amount_read += INT_LENGTH
    total_len = msg_len + amount_read
    bets = []
    amount_bets = 0
    agency_number = 0
    while amount_read < total_len:
      code: int = int.from_bytes(msg[amount_read:amount_read + CODE_LENGTH ], byteorder='big')
      amount_read += CODE_LENGTH
      
      if code == AGENCY_BATCH_CODE:
        agency_number, amount_read = self.__decode_int_to_str(msg, amount_read)
      elif code == BET_CODE:
        amount_bets += 1
        bet, amount_read = self.__decode_bet_msg(msg, amount_read, agency_number)
        if bet != None:
          bets.append(bet)
      else:
        logging.error(f"Invalid code number found: {code}")
        return bets, amount_bets
    return bets, amount_bets

  def __decode_bet_msg(self, msg, amount_read, agency_number = "0"):
    msg_len = int.from_bytes(msg[amount_read:amount_read + INT_LENGTH ], byteorder='big')
    
    amount_read += INT_LENGTH
    total_len = msg_len + amount_read
    bet = Bet(agency_number, "", "", "", datetime.date.min.isoformat(), "0")
    while amount_read < total_len:
      code: int = int.from_bytes(msg[amount_read:amount_read + CODE_LENGTH ], byteorder='big')
      amount_read += CODE_LENGTH
      
      try:
        if code == AGENCY_CODE:
          bet.agency, amount_read = self.__decode_int_to_str(msg, amount_read)
        elif code == NAME_CODE:
          bet.first_name, amount_read = self.__decode_variable_str(msg, amount_read)
        elif code == SURNAME_CODE:
          bet.last_name, amount_read = self.__decode_variable_str(msg, amount_read)
        elif code == DOCUMENT_CODE:
          bet.document, amount_read = self.__decode_int_to_str(msg, amount_read)
        elif code == BIRTHDATE_CODE:
          bet.birthdate, amount_read = self.__decode_iso_date(msg, amount_read)
        elif code == BETNUMBER_CODE:
          bet.number, amount_read = self.__decode_int_to_str(msg, amount_read)
        else:
          logging.error(f"Invalid code number found: {code}")
          return None, total_len # don't return a bet but move to the next one
      except (ValueError, UnicodeDecodeError) as e:
        logging.error(f"Invalid value in param | Error: {e}")
        return None, total_len # don't return a bet but move to the next one
    
    return bet, amount_read

  def __decode_int_to_str(self, msg: bytearray, amount_read: int):
    number = str(int.from_bytes(msg[amount_read:amount_read + INT_LENGTH ], byteorder='big'))
    return number, amount_read + INT_LENGTH
  
  def __decode_variable_str(self, msg: bytearray, amount_read: int):
    string_len = int.from_bytes(msg[amount_read:amount_read + INT_LENGTH ], byteorder='big')
    amount_read += INT_LENGTH
    string = (msg[amount_read:amount_read + string_len]).decode('utf-8')
    return string, amount_read + string_len
  
  def __decode_iso_date(self, msg: bytearray, amount_read: int):
    birtdateISO = (msg[amount_read:amount_read + ISODATE_LENGTH]).decode('utf-8')
    return datetime.date.fromisoformat(birtdateISO), amount_read + ISODATE_LENGTH


  def create_ack_msg(self, result: bool):
    message = bytearray()
    # code|<result>
    message.extend(ACK_BET_CODE.to_bytes(CODE_LENGTH, byteorder='big'))
    message.extend(result.to_bytes(BOOL_LENGTH, byteorder='big'))
    return message
  
  