"""
  Процедуры для работы с чатом Rocket.Chat
"""

__all__ = [
  'rocket_chat_send_message',
  'rocket_chat_send_hello',
  'rocket_chat_get_all_standup_info',
  'rocket_chat_send_my_standup',
]

from os import path
from datetime import datetime
from pprint import pprint
import re

from rocketchat_API.rocketchat import RocketChat
from requests import sessions

from utils import sleep, run_os_command

# Реквизиты для входа в Rocket.Chat
from config.config import (
  ROCKET_CHAT_SERVER,
  ROCKET_CHAT_LOGIN,
  ROCKET_CHAT_PWD,
  
  ROCKET_CHAT_CHANNEL_HELLO,
  ROCKET_CHAT_CHANNEL_STAND_UP,
  
  ROCKET_CHAT_MESSAGE_HELLO,
  
  WHATTODO_NAME
)

proxy_dict = {}

# ---------------------------------------------------------------------------

base_dir = path.dirname(path.abspath(__file__))

#today = datetime.today().strftime('%Y-%m-%d')
#RESULT_TXT = path.join(BASE_DIR, f"result_{today}.txt")

whattodo_file = path.join(base_dir, 'stand_up', f'{WHATTODO_NAME}.txt')
whattodo_last_file = path.join(base_dir, 'stand_up', f'{WHATTODO_NAME}_last.txt')

# ---------------------------------------------------------------------------


def rocket_chat_send_message(message, to_channel):
  """
  Отправить сообщение в канал Рокет.Чат
  """
  result = False
  
  with sessions.Session() as session:
    try:
      rock = RocketChat(ROCKET_CHAT_LOGIN, ROCKET_CHAT_PWD, server_url=ROCKET_CHAT_SERVER, session=session)
    except Exception as e:
      print(e)
      rock = None
      
    if rock:
      try:
        resp = rock.chat_post_message(message, channel=to_channel)
      except Exception as e:
        print(e)
        resp = None
        
      if resp and resp.status_code == 200:
        result = True        
  
  return result
  
  
def rocket_chat_send_hello(to_channel=ROCKET_CHAT_CHANNEL_HELLO):
  """
  Отправить приветствие в общий канал Рокет.Чата
  """
  result = rocket_chat_send_message(ROCKET_CHAT_MESSAGE_HELLO, to_channel=to_channel)
  
  rc = 'SUCCESS' if result else 'ERROR'
  print(f"'hello' -> #{to_channel}: {rc}!")
  
  return result
  
  
def rocket_chat_send_my_standup(to_channel=ROCKET_CHAT_CHANNEL_STAND_UP):
  """
  Отправить информацию 'что делал / что буду делать' в канал "планёрка"
  """
  result = False
  text = ''
  
  try:
    with open(whattodo_file, encoding='utf-8') as f:
      whattodo_str = f.read()
  except Exception as e:
    print(e)
    whattodo_str = ''

  try:
    with open(whattodo_last_file, encoding='utf-8') as f:
      whattodo_last_str = f.read()
  except Exception as e:
    print(e)
    whattodo_last_str = ''

  # Если что-то нашли для отправки, и оно отличается от содержимого, отправленного в прошлый раз, то отправляем.
  # Учитываем, что в начале текста может быть комментарий, его отправлять не нужно.
  if whattodo_str:
    
    # Убираем комментарий в начале
    text = re.split('[%]{5,}\n', whattodo_str)[-1]
    text = text.strip().strip('\n').strip()
  
    # Проверяем различия с предыдущей отправкой
    if text and text != whattodo_last_str:
      text_to_send = f'```\n{text}\n```'
      
      # Отправка
      result = rocket_chat_send_message(text_to_send, to_channel=to_channel)      
      
      # В случае успешной отправки - сохраним текст
      if result:
        now = datetime.now()
        whattodo_send_file = path.join(base_dir, 'stand_up', f'{WHATTODO_NAME}_send_{now.strftime("%Y-%m-%d_%H-%M-%S_%f")}.txt')
        
        try:
          with open(whattodo_last_file, 'w', encoding='utf-8') as f:
            f.write(text)  
        except Exception as e:
          print(e)

        try:
          with open(whattodo_send_file, 'w', encoding='utf-8') as f:
            f.write(text)  
        except Exception as e:
          print(e)
    
    rc = 'SUCCESS' if result else 'ERROR'
    print(f"[WHATTODO] -> #{to_channel}: {rc}!")
  
  return result


def rocket_chat_get_all_standup_info(from_channel=ROCKET_CHAT_CHANNEL_STAND_UP):
  """
  Получить информацию из канала "планёрка" о том, что делали другие
  """ 
  info = []
  
  with sessions.Session() as session:
    try:
      rock = RocketChat(ROCKET_CHAT_LOGIN, ROCKET_CHAT_PWD, server_url=ROCKET_CHAT_SERVER, session=session)
    except Exception as e:
      print(e)
      rock = None
      
    if rock:
      try:
        room_id = rock.channels_info(channel=from_channel).json()['channel']['_id']
      except Exception as e:
        print(e)
        room_id = None
      
      if room_id:
        try:
          today = datetime.today().strftime('%Y-%m-%d')
          messages = rock.channels_history(room_id=room_id, unreads=True, oldest=today).json()['messages']          
        except Exception as e:
          print(e)
          messages = None
          
        if messages:
          for message in messages:
            rch_user = message['u']['name']
            
            rch_message = message['msg'].replace('```','')                  
            rch_message = re.sub('\(http://[^)]*\)', '', rch_message)            
            #!todo!
            #rch_message = rch_message.replace('XXX', '')
            
            text = f'### {rch_user} ##:\n{rch_message}\n\n'
            info.append(text)
          
  return info
  

def rocket_chat_get_unreads_msg_count(type='im'):
  """
  Получить количество непрочитанных собщений, из личных чатов либо общих каналов
  """
  if type not in ['im', 'channel']: return None
  
  now = datetime.now()
  dt_updated_since = now.replace(hour = now.hour - 8).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
  dt_oldest = now.replace(hour = now.hour - 8).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
  print(now, dt_updated_since, dt_oldest)
  
  unreads = None

  with sessions.Session() as session:
    # Попытка соединения с сервером
    try:
      rock = RocketChat(ROCKET_CHAT_LOGIN, ROCKET_CHAT_PWD, server_url=ROCKET_CHAT_SERVER, session=session)
    except Exception as e:
      print(e)
      rock = None
      
    if rock:
      # Список личных чатов, либо каналов
      try:        
        if type == 'im':
          room_list = rock.im_list().json()['ims']
        elif type == 'channel':
          room_list = rock.channels_list().json()['channels']
        else:
          room_list = None          
        
        #room_list = rock.rooms_get(updatedSince=dt_updated_since).json()['update']
        #room_list = rock.rooms_get().json()['update']        
        #pprint(rock.channels_history(room_id=room_id, unreads=True, oldest=dt_oldest).json()['messages'])
        
      except Exception as e:
        print(e)
        room_list = None
              
      if room_list:
        sleep(2)
        unreads = 0
        
        # Цикл по списку личных чатов, либо каналов
        for room in room_list:
          #if room['t'] == 'p':
          #print(room)
          
          try:
            if type == 'im':
              room_counter = rock.im_counters(room_id = room['_id']).json()
            elif type == 'channel':
              room_counter = rock.channels_counters(room_id = room['_id']).json()
            else:
              room_counter = None
          except Exception as e:
            print(e)
            room_counter = None
            
          #pprint(room_counter)
            
          if room_counter:
            unreads_value = room_counter.get('unreads', None)
            if unreads_value: unreads += unreads_value
          sleep(5)
        
  return unreads
  

def get_unreads_im_msg_count():
  """
  Получить количество непрочитанных собщений, из личных чатов
  """
  return rocket_chat_get_unreads_msg_count(type='im')


def get_unreads_channel_msg_count():
  """
  Получить количество непрочитанных собщений, из общих каналов
  """
  return rocket_chat_get_unreads_msg_count(type='channel')
  

if __name__=='__main__':
  print('HELLO FROM ROCKET.CHAT ENGINE!\n')
  
  #print(rocket_chat_get_unreads_msg_count())
  #print(rocket_chat_get_unreads_msg_count(type='channel'))
  #print(get_unreads_im_msg_count())
  #print(get_unreads_channel_msg_count())
