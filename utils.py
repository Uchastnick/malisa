"""
  Вспомогательные процедуры
"""

__all__ = [
  'sleep', 
  'beep', 
  'run_os_command',
  'detect_file_encoding',
  'check_any_exact_match',
  'check_any_partial_match',
  'extract_value_from_text'
]

import time
import subprocess
import winsound

import chardet
from chardet.universaldetector import UniversalDetector

# -----------------------------------------------------------------------------

def sleep(seconds):
  """
  Задержка (пауза)
  """
  time.sleep(seconds)
  

def beep(count=1):
  """
  Небольшой звуковой сигнал во время работы в консоли
  """
  print('\a' * count)
  
  
def beep_sound(count=1, freq=3000, duration=500):
  """
  Звуковой сигнал
  """
  for i in range(count):
    winsound.Beep(frequency=freq, duration=duration)


def run_os_command(cmd=[], sync=False, hide=False):
  """
  Запустить команду операционной системы, с параметрами.
  `cmd` - это массив, первый элемент которого - искомая команда, остальные - параметры команды.
  По умолчанию запуск происходит асинхронно (можно указать запуск c ожиданием выполнения).
  Также возможно `спрятать` окно вызываемого приложения.
  """
  result = False
  
  if cmd: 
    si = subprocess.STARTUPINFO()
    shell = False

    if hide:
      si.dwFlags |= (subprocess.STARTF_USESHOWWINDOW | subprocess.SW_HIDE)
      si.wShowWindow = subprocess.SW_HIDE
      shell=True ##

    try:      
      if sync:
        code = subprocess.call(cmd, startupinfo=si, shell=shell, stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
        if code == 0:
          result = True
        else:
          print("Ошибка при запуске!")
      
      else:
        p = subprocess.Popen(cmd, startupinfo=si, stderr=subprocess.STDOUT, stdout=subprocess.DEVNULL)
        result = True
      
    except Exception as e:
      result = False
      print(e)
      print("Ошибка при выполнении внешней команды!")
  
  return result


def detect_file_encoding(file_path):
  """
  Определить кодировку файла
  В будущем, возможно, и основной язык
  """
  encoding = None
  
  detector = UniversalDetector()
  line_count = 0
  
  for line in open(file_path, 'rb'):
    detector.feed(line)
    line_count += 1
    if detector.done or line_count >= 50: break
    
  detector.close()  
  encoding = detector.result['encoding']
  return encoding
  

def check_any_exact_match(text, keyword_list):
  """
  Проверка на точное соответствие указанного текста набору ключевых слов/фраз.
  Соответствие ищется по любому указанному ключевому слову/фразе.
  """
  return (text in keyword_list)


def check_any_partial_match(text, keyword_list):
  """
  Проверка на частичное соответствие указанного текста набору ключевых слов/фраз.
  Соответствие ищется по любому указанному ключевому слову/фразе.
  """
  #todo: сравнить скорость выполнения со способом "цикл плюс `or in`"
  return any([ (kw == text or kw in text) for kw in keyword_list ])

        
def extract_value_from_text(text, keyword, default_value=''):
  """
  Извлечь значение после ключевого слова, из текстовой строки.
  
  По соглашению, возвращается само значение ПОСЛЕ ключевого слова (либо указанное значение по умолчанию)
  и часть текстовой строки ДО ключевого слова.
  
  Поэтому, если у Вас в строке несколько пар `ключевое_слово значение`, 
  то вызывайте функцию последовательно, начиная с ключевого слова, расположенного ближе к концу строки.
  """
  (part1, keyword, part2) = text.rpartition(f'{keyword} ')
  
  if keyword:
    new_text = part1
    value = part2.strip()
  else:
    new_text = part2
    value = default_value
  
  return (new_text, value)

