import os, sys
import yaml
import re
from pprint import pprint

import config.config as conf
import utils


def from_camel_to_snake_case(name):
  """
  Преобразование имени из из `CamelCase` в `snake_case`
  """
  #todo: re.compile
  try:
    result = '_'.join( re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', name)).split() ).lower()
  except Exception as e:
    print(e)
    result = name
  return result


def load_reactions_map(type, is_action_valid_proc):
  """
  Загрузка `карты реакций` из конфигурации
  Возможно указать тип для карты реакций, задаваемых пользователем, (type='system' | 'user')
  """
  reactions_map = []

  home_dir = os.path.dirname(os.path.abspath(__file__))
  
  if type == 'user':
    file_yaml = os.path.join(home_dir, 'config', 'user_logic.yaml')
  else:
    type = 'system'
    file_yaml = os.path.join(home_dir, 'config', 'logic.yaml')
  
  try:
    with open(file_yaml, encoding='utf-8') as f:
      data = yaml.safe_load_all(f)
    
      for reaction_raw in data:
      
        key_phrase_exact   = reaction_raw.get('key_phrase_exact', [])
        key_phrase_partial = reaction_raw.get('key_phrase_partial', [])
        result_type        = reaction_raw.get('result_type', 'speech').lower()
        result_speech      = reaction_raw.get('result_speech', [])
        result_action      = reaction_raw.get('result_action', '')
        action_need_parameter_text = reaction_raw.get('action_need_parameter_text', 0)
        
        # Проверка корректности заполнения блоков реакций
        if (not key_phrase_exact and not key_phrase_partial) \
           or not result_type \
           or not (result_type in ['speech', 'action', 'user_action']) \
           or (result_type == 'speech' and not result_speech) \
           or (result_type in ['action', 'user_action'] and not result_action):
          continue
        
        # Требуемые преобразования
        if key_phrase_exact:
          key_phrase_exact = [k.lower().replace('%robot_name%', conf.ROBOT_NAME.lower()) for k in key_phrase_exact]
          
        if key_phrase_partial:
          key_phrase_partial = [k.lower().replace('%robot_name%', conf.ROBOT_NAME.lower()) for k in key_phrase_partial]
        
        if result_type in ['action', 'user_action'] and result_action:
          result_action_snake_case = from_camel_to_snake_case(result_action)
          result_action = f'act_{result_action_snake_case}'

          reaction_type = type          
          
          # Корректировка типа действия
          if result_type == 'action':
            reaction_type = 'system'
          elif result_type == 'user_action':
            reaction_type = 'user'
          
          # Проверка существования указанной action-процедуры в системе
          if not is_action_valid_proc(result_action, reaction_type=reaction_type):
            continue
                
        # Формируем внутренний блок реакции на действие пользователя
        reaction = {}        
        reaction['type'] = type
        reaction['key_phrase_exact'] = key_phrase_exact
        reaction['key_phrase_partial'] = key_phrase_partial
        reaction['result_type'] = result_type
        reaction['result_speech'] = result_speech          
        reaction['result_action'] = result_action
        reaction['action_need_parameter_text'] = action_need_parameter_text        
        
        reactions_map.append(reaction)
        
  except Exception as e:
    print(e)
    reactions_map = []
    
  return reactions_map
  
  
def make_reaction_via_map(text, reactions_map, say_proc, run_action_proc):
  """
  Определить реакцию (действие) системы на основании карты реакций.
  Текст должен приходить в нижнем регистре.
  """
  if not reactions_map or not text:
    return False
    
  result = False
    
  ##text = text.lower()
  
  for reaction in reactions_map:
    reaction_type = reaction['type']
    
    key_phrase_exact = reaction['key_phrase_exact']
    key_phrase_partial = reaction['key_phrase_partial']
    
    # Проверка на соответствие ключевым фразам
    if (key_phrase_exact and utils.check_any_exact_match(text, key_phrase_exact)) \
       or (key_phrase_partial and utils.check_any_partial_match(text, key_phrase_partial)):
      
      result_type = reaction['result_type']      
      
      result_action = reaction['result_action']
      send_text = text if reaction['action_need_parameter_text'] == 1 else ''
      
      if result_type == 'speech':
        for speech_text in reaction['result_speech']:
          say_proc(speech_text)
          
      elif result_type == 'action':
        run_action_proc(result_action, text=send_text, reaction_type='system')
      
      elif result_type == 'user_action':
        run_action_proc(result_action, text=send_text, reaction_type='user')
        
      result = True
      break

  return result
  

if __name__=='__main__':
  pass
