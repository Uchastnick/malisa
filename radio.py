"""
  Функционал для работы с радио (плеером) в системе
  Используется установленный плеер AIMP3
"""

__all__ = [
  'get_radio_link_by_style',
  'get_radio_link_random',
  'run_player_aimp',
  'radio_pause',
  'radio_play',
  'radio_stop', 
]

import os

from utils import (
  sleep, 
  beep, 
  run_os_command,
  extract_value_from_text
)

import random
import yaml
import pyaimp

# -----------------------------------------------------------------------------
from config.config import AIMP_PATH

# Сопоставление наименования стилей
from config.music_style import music_style_names

# Ссылки на потоковое радио для разных стилей (хранятся в отдельном файле)
radio_links = []

# -----------------------------------------------------------------------------

def load_radio_links():
  """
  Загрузка списка ссылок на потоковое радио для разных стилей
  """
  global radio_links
  
  if not radio_links:
    file_yaml = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'radio_links.yaml')
    
    try:
      with open(file_yaml, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        radio_links = data['radio_links']      
    except:
      radio_links = []
    
  return radio_links
  

def get_radio_link_by_style(message):
  """
  Выбрать ссылку на потокое радио на основании указанного стиля  
  """ 
  if not radio_links: load_radio_links()
  if not radio_links: return ''
    
  radio_link = ''
  style = ''
    
  kw_idx = -1  
  for keyword in ['стиль', 'радио']:
    kw_idx = message.lower().find(f'{keyword} ')
    kw_length = len(keyword) + 1
    if kw_idx >= 0: break
  
  if kw_idx >= 0:    
    style_in_msg = message[(kw_idx + kw_length):].strip()
    play_links = []
    
    try:
      if style_in_msg:
        print(f"Указанный стиль: ['{style_in_msg.upper()}']")
        
        style_name = music_style_names.get(style_in_msg.lower(), None)
                
        if style_name:
          play_links = radio_links[style_name]
        else:
          play_links = []
    except:
      play_links = []
      
    if play_links:
      radio_link = random.choice(play_links)
      
  return radio_link
  

def get_radio_link_random():
  """
  Получить случайную ссылку на потоковое вещание (из доступных ссылок)
  """
  if not radio_links: load_radio_links()
  if not radio_links: return ''
    
  radio_link = ''
  
  if radio_links:
    radio_style_name = random.choice([k for k in radio_links.keys()])
    
    if radio_style_name:
      radio_link = random.choice(radio_links[radio_style_name])
      print(f"['{radio_style_name}']: '{radio_link}'")
  
  return radio_link
  

def run_player_aimp():
  """
  Запуск AIMP3
  """
  cmd = [AIMP_PATH, '/PAUSE']
  run_os_command(cmd)  
  sleep(3)
  
  try:
    player = pyaimp.Client()
  except:
    player = None
    
  return player
  

def radio_pause():
  """
  Проигрывание музыки - на паузу
  """
  try:
    player = pyaimp.Client()
  except:
    player = None
  
  if player:
    state = player.get_playback_state() 
    if state == pyaimp.PlayBackState.Playing:
      player.pause()
      
  return player


def radio_play():
  """
  Запуск проигрывания музыки после паузы
  """
  try:
    player = pyaimp.Client()
  except:
    player = None
  
  if player:
    state = player.get_playback_state() 
    if state != pyaimp.PlayBackState.Playing:
      player.play()

  return player


def radio_stop():
  """
  Остановка проигрывания музыки
  """
  try:
    player = pyaimp.Client()
  except:
    player = None
  
  if player:
    state = player.get_playback_state() 
    if state != pyaimp.PlayBackState.Stopped:
      player.stop()
      
  return player


if __name__=='__main__':
  pass
  #load_radio_links()
  #print(get_radio_link_random())
  #print(get_radio_link_by_style('стиль разное'))
