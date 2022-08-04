"""
  Функции управления системой `умный дом`
"""

import os
import yaml
import yeelight
from pprint import pprint


def load_smart_devices_info():
  """
  Загрузка списка умных устройств из конфигурационного файла
  """
  # Набор всех умных устройств
  smart_devices = {}
  
  home_dir = os.path.dirname(os.path.abspath(__file__))
  file_yaml = os.path.join(home_dir, 'config', 'smart_devices.yaml')
  
  if not os.path.isfile(file_yaml):
    print(f'\nНе найден файл конфигурации устройств умного дома "{file_yaml}"!\n')
    return smart_devices
  
  try:
    with open(file_yaml, encoding='utf-8') as f:
      data = yaml.safe_load_all(f)
      
      # Список умных ламп
      bulbs = []
      # Умная лампа по умолчанию
      default_bulb = {}
      
      for device_raw in data:        
        type = device_raw.get('type', None)
        name = device_raw.get('name', '')
        default = device_raw.get('default', False)
                
        if type == 'bulb':
          # Умная лампа
          bulb = {}
          bulb['type'] = type
          bulb['name'] = name          
          bulb['default'] = default
          bulb['ip'] = device_raw.get('ip', None),
          bulb['port'] = device_raw.get('port', None),
          bulb['model'] = device_raw.get('model', 'simple') # ('simple' | 'color')
          bulb['color_mode'] = device_raw.get('color_mode', 0)
          bulb['ct'] = device_raw.get('ct', 2700)
          bulb['hue'] = device_raw.get('hue', 359)
          bulb['sat'] = device_raw.get('sat', 100)
          bulb['bright'] = device_raw.get('bright', 50)
          bulb['rgb'] = device_raw.get('rgb', '16711935') 
          bulb['power'] = device_raw.get('power', 'off')
          
          bulbs.append(bulb)
          
          if default and not default_bulb:
            default_bulb = bulb
        
      smart_devices['bulbs'] = bulbs
      smart_devices['default_bulb'] = default_bulb
      
  except Exception as e:
    print(e)
    smart_devices = {}
  
  return smart_devices


if __name__=='__main__':
  pass  
    
  smart_devices = load_smart_devices_info()
  if smart_devices:
    print('\nSmart devices:\n')
    pprint(smart_devices)
