"""
  Функции управления системой `умный дом`
"""

import os
import yaml
import yeelight as yee
from pprint import pprint

import colors

import utils
config = utils.load_config()

# Цветовая температура по умолчанию, для устройства освещения по умолчанию
BULB_COLOR_TEMP_DEFAULT = config.smarthome.bulb_color_temp_default
# Яркость по умолчанию, для устройства освещения по умолчанию
BULB_BRIGHTNESS_DEFAULT = config.smarthome.bulb_brightness_default


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
        brand = device_raw.get('brand', None)
        name = device_raw.get('name', None)
        default = device_raw.get('default', False)
                
        if type == 'bulb':
          # Умная лампа
          
          # !ВНИМАНИЕ! В текущей версии поддерживаются только лампы Yeelight
          if brand != 'yeelight':
            continue
          
          bulb = {}
          bulb['type'] = type
          bulb['brand'] = brand
          bulb['name'] = name          
          bulb['default'] = default
          bulb['ip'] = device_raw.get('ip', None)
          bulb['port'] = device_raw.get('port', None)
          bulb['model'] = device_raw.get('model', 'mono') # ('mono' | 'color')
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


def get_bulb(bulb_info, auto_on=True, effect="smooth"):
  """
  Инициализировать и вернуть устройство освещения на основании информации из конфигурации
  """
  if not bulb_info: return None
  bulb = None
  
  brand = bulb_info.get('brand', None)
  ip    = bulb_info.get('ip', None)
  port  = bulb_info.get('port', None)
  
  if ip:
    if brand == 'yeelight':
      try:
        bulb = yee.Bulb(ip=ip, auto_on=auto_on, effect=effect)
      except Exception as e:
        print(e)
        print('Ошибка!')
        bulb = None
  
  return bulb
  
  
def light_on(bulb_info):
  """
  Включение света
  """
  if not bulb_info: return False
  result = False
  
  bulb = get_bulb(bulb_info)
  
  if bulb:
    try:
      bulb.turn_on()
      result = True
    except Exception as e:
      print(e)
      print('Ошибка!')
      result = False
      
  return result

  
def light_off(bulb_info):
  """
  Выключение света
  """
  if not bulb_info: return False
  result = False

  bulb = get_bulb(bulb_info)
  
  if bulb:  
    try:
      bulb.turn_off(effect="sudden")
      result = True
    except Exception as e:
      print(e)
      print('Ошибка!')
      result = False
      
  return result
  
  
def light_normal(bulb_info):
  """
  Обычный свет (базовые параметры)
  """
  if not bulb_info: return False
  result = False
  
  bulb = get_bulb(bulb_info)
  
  if bulb:
    try:
      bulb.set_color_temp(BULB_COLOR_TEMP_DEFAULT)
      bulb.set_brightness(BULB_BRIGHTNESS_DEFAULT)
      
      result = True
    except Exception as e:
      print(e)
      print('Ошибка!')
      result = False
      
  return result
  

def light_alarm(bulb_info):
  """
  Тревога! (индикация светом)
  """
  if not bulb_info: return False
  result = False

  bulb = get_bulb(bulb_info)
  
  if bulb:  
    try:
      #bulb_props = bulb.get_properties()
      #todo
      bulb.set_rgb(255, 0, 0)
      #bulb.set_brightness(50)
      #bulb.start_flow(yeelight.flows.alarm(duration=1000))
      
      result = True
    except Exception as e:
      print(e)
      print('Ошибка!')
      result = False
      
  return result
  

def light_color(bulb_info, color='white'):
  """
  Включение лампы и установка заданного цвета
  """
  if not bulb_info: return False
  result = False
  
  model = bulb_info.get('model', 'mono')
  if model != 'color':
    return False

  bulb = get_bulb(bulb_info)
  
  if bulb and color:  
    try:
      #bulb_props = bulb.get_properties()
      (r, g, b) = colors.get_rgb_for_color(color_name = color)
      bulb.set_rgb(r, g, b)      
      
      #(h, s, v) = colors.get_hsv_for_color(color_name = color)
      #bulb.set_hsv(h, s, v) 
      #bulb.set_brightness(50)
      
      result = True
    except Exception as e:
      print(e)
      print('Ошибка!')
      result = False
      
  return result


def light_brightness(bulb_info, brightness):
  """
  Установка яркости на заданное количество процентов (10-100)
  """
  if not bulb_info: return False
  result = False

  bulb = get_bulb(bulb_info)
  
  if bulb and brightness:
  
    bright = brightness
    if bright < 10:
      bright = 10
    elif bright > 100:
      bright = 100
    
    try:
      bulb.set_brightness(bright)
      result = True
    except Exception as e:
      print(e)
      print('Ошибка!')
      result = False
      
  return result


def light_color_temperature(bulb_info, color_temperature):
  """
  Установка цветовой температуры на указанную величину (1500-7700)
  """
  if not bulb_info: return False
  result = False

  bulb = get_bulb(bulb_info)
  
  if bulb and color_temperature:
  
    color_temp = color_temperature
    if color_temp < 1500:
      color_temp = 1500
    elif color_temp > 7700:
      color_temp = 7700
    
    try:
      bulb.set_color_temp(color_temp)
      result = True
    except Exception as e:
      print(e)
      print('Ошибка!')
      result = False
      
  return result


if __name__=='__main__':
  pass  
    
  #smart_devices = load_smart_devices_info()
  #if smart_devices:
  #  print('\nSmart devices:\n')
  #  pprint(smart_devices)
  
  #pprint(colors.get_rgb_for_color('blue'))
  #pprint(colors.get_hsv_for_color('orange'))
