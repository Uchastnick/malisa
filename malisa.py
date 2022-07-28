import os, sys

# -----------------------------------------------------------------------------
# Директория основного скрипта робота
home_dir = os.path.dirname(os.path.abspath(__file__))

# Трюк для одновременной работы с импортируемыми модулями
# как в локальном режиме, так и в режиме пакета
if home_dir not in sys.path: sys.path.append(home_dir)

# -----------------------------------------------------------------------------
# Базовая Конфигурация по умолчанию

if not os.path.isfile(os.path.join(home_dir, 'config', 'config.py')):
  print(f'\nНе найден основной файл конфиграции "./config/config.py"!\n\a')
  sys.exit(0)

try:
  import config.config as conf
except Exception as e:
  print('Обнаружена проблема в файле конфигурации "./config/config.py"!\n\a')
  print(e)

# -----------------------------------------------------------------------------

import importlib

import subprocess
import threading

import random

import time
from datetime import datetime, timedelta

import locale

from pprint import pprint

from colorama import init as init_color
init_color(autoreset=True)
from colorama import ansi, Fore, Back, Style

NIGHT_MODE = False

ANSI_CYAN_BRIGHT = Fore.CYAN + (Style.BRIGHT if not NIGHT_MODE else '')
ANSI_GREEN_BRIGHT = Fore.GREEN + (Style.BRIGHT if not NIGHT_MODE else '')
ANSI_YELLOW_BRIGHT = Fore.YELLOW + (Style.BRIGHT if not NIGHT_MODE else '')
ANSI_BLACK_ON_WHITE = Back.WHITE + Fore.BLACK
ANSI_STYLE_RESET = Style.RESET_ALL

import pyttsx3
from gtts import gTTS
import speech_recognition as sr

import sqlite3

import requests

try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET

import json
import feedparser
from pyperclip import copy as copyclip, paste as pasteclip

import pyautogui
pyautogui.PAUSE = 2

screen_size = pyautogui.size()
x_center, y_center = round(screen_size[0]/2), round(screen_size[1]/2)

import pyaimp

from utils import (
  sleep, 
  beep, 
  beep_sound,
  run_os_command,
  detect_file_encoding,
  check_any_exact_match,
  check_any_partial_match,
  extract_value_from_text
)

import yaml
from inputimeout import inputimeout, TimeoutOccurred

import webbrowser as web
import re

import fitz

from googletrans import Translator

import psutil

import winsound
from pydub import AudioSegment

from argparse import ArgumentParser

# -----------------------------------------------------------------------------
import reaction

# Карта реакций системы на фразы пользователей.
# Расположена в отдельных файлах `config/*logic.yaml`, для удобства конфигурирования.
reactions_map = None

# -----------------------------------------------------------------------------

# Функции для работы с информацией о погоде
import weather

# -----------------------------------------------------------------------------

# Функции для загрузки новостей
import news as news_engine

# -----------------------------------------------------------------------------

# Функции для работы с радио
import radio

# -----------------------------------------------------------------------------

# Функции для работы с Rocket.Chat
import rocket

# -----------------------------------------------------------------------------

db_quotes = None
quotes = []

db_irr_verbs = None
irr_verbs = []

phrasal_verbs = []

# -----------------------------------------------------------------------------

# Подготовленные данные для изучения слов немецкого языка
import data.words_deutsch_dicts as wdd

# Набор доступных словарей для изучения слов немецкого языка
dicts_deutsch_all = [
  wdd.words_deutsch_base,

  wdd.words_deutsch_pronouns,
  wdd.words_deutsch_verbs,
  wdd.words_deutsch_words,
  #wdd.words_deutsch_numerals,

  #wdd.words_deutsch_beginners,
  #wdd.words_deutsch_phrases,
  #wdd.words_deutsch_proverbs,
]

# Сколько раз повторять одно и то же слово при показе
WORD_REPEAT_COUNT = 3

# -----------------------------------------------------------------------------

# Чтение книги порциями
READ_CHUNK_SIZE = 256 #512
SENTENCE_DELIMITER = '. '
  
# -----------------------------------------------------------------------------

# Инициализация web-поиска
if conf.WEB_BROWSER_APP:
  web.register('web_browser', None, web.BackgroundBrowser(conf.WEB_BROWSER_APP))
  web_browser = web.get('web_browser')
else:
  web_browser = web.get(None)

# -----------------------------------------------------------------------------

# Google-переводчик
translator = Translator()

# -----------------------------------------------------------------------------

tts = None
ru_voice_id = ''
en_voice_id = ''
de_voice_id = ''
current_tts_lang = ''

reco = sr.Recognizer()

# Список слов для контроля цензуры (отдельный файл)
from words import bad_words

# -----------------------------------------------------------------------------
# Возможные ответы робота при проверке статуса

robot_answers = [
  'Привет!', 'Слушаю!', 'Я готова!', 
  'Внимательно слушаю!', 'Я здесь!', 'Я!', 
  'Да?', 'Говорите!', 'Что?', 'На связи!',
]

# -----------------------------------------------------------------------------

def init_locale():
  """
  Устанавливаем языковой стандарт
  """
  #locale.setlocale(locale.LC_ALL, '') # from environment
  #locale.setlocale(locale.LC_ALL, 'ru_RU.utf8') # for Linux
  locale.setlocale(locale.LC_ALL, 'Russian') # for OS Windows  
  

def init_db_quotes():
  """
  Инициализация базы со списком цитат и мудрых мыслей
  """
  global db_quotes
  
  if not db_quotes:
    db_quotes = sqlite3.connect(os.path.join(home_dir, 'data', 'quotations.db'))
  return db_quotes

  
def init_db_irr_verbs():
  """
  Инициализация базы со списком неправильных глаголов
  """
  global db_irr_verbs
  
  if not db_irr_verbs:
    db_irr_verbs = sqlite3.connect(os.path.join(home_dir, 'data', 'irr_verbs.db'))
  return db_irr_verbs
  

def open_databases():
  """
  Открытие баз данных
  """
  init_db_quotes()
  init_db_irr_verbs()
  
  
def close_databases():
  """
  Закрытие открытых баз данных
  """
  global db_quotes
  global db_irr_verbs
  
  if db_quotes: 
    db_quotes.close()
    db_quotes = None
  
  if db_irr_verbs:
    db_irr_verbs.close()
    db_irr_verbs = None

  
def load_quotes():
  """
  Загрузка списка цитат и мудрых мыслей
  """
  global quotes
  quotes = []
  if db_quotes:      
    sql = """
      select q.num, q.text, q.isBest from quote q --where q.isBest = 1
    """  
    cursor = db_quotes.cursor()
    quotes = cursor.execute(sql).fetchall()    
  return quotes
  

def load_irr_verbs():
  """
  Загрузка списка неправильных глаголов
  """
  global irr_verbs
  irr_verbs = []
  if db_irr_verbs:      
    sql = """
      select
          v._id as id, 
          v.form_1, 
          v.form_2, 
          v.form_3, 
          v.russian
        from verbs v
    """  
    cursor = db_irr_verbs.cursor()
    irr_verbs = cursor.execute(sql).fetchall()    
  return irr_verbs
  

def load_phrasal_verbs():
  """
  Загрузка списка фразовых глаголов
  """
  global phrasal_verbs
  phrasal_verbs = []
  with open(os.path.join(home_dir, 'data', 'phrasal_verbs.json'),
            mode='r', 
            encoding='utf-8') as f:
    phrasal_verbs = json.load(f)
  return phrasal_verbs
    

def run_timer(seconds, name=None):
  """
  Запуск таймера на указанное количество секунд
  """
  beep_sound()
  sleep(seconds)
  beep_sound(3)
  ## if name: say(f'Таймер "{name}" завершён.')
  

def run_interval_timer(seconds, signal_after_seconds, name=None):
  """
  Запуск интервального таймера на указанное количество секунд
  """
  total_seconds = 0
  interval_seconds = 0
  
  now = time.time()
  maxtime = now + seconds
  
  beep_sound()
  
  # При необходимости - корректировка длительности паузы
  ## while total_seconds < seconds:
  while time.time() <= maxtime:
    total_seconds += 1
    interval_seconds += 1
    
    if interval_seconds == signal_after_seconds:
      interval_seconds = 0
      winsound.Beep(frequency=800, duration=500)
      time.sleep(0.5)
    else:    
      time.sleep(1)
  
  beep_sound(3)
  ## if name: say(f'Таймер "{name}" завершён.')
  

def make_timer(seconds, name=None):
  """
  Создать таймер на указанное количество секунд
  (создаётся в отдельном потоке)
  """
  timer = threading.Thread(target=run_timer, args=(seconds, name)).start()


def make_interval_timer(seconds, signal_after_seconds, name=None):
  """
  Создать интервальный таймер на указанное количество секунд
  (создаётся в отдельном потоке)
  """
  timer = threading.Thread(target=run_interval_timer, args=(seconds, signal_after_seconds, name)).start()


def play_clock_alarm():
  """
  Проиграть звук будильника
  """
  file_alarm = os.path.join(home_dir, 'sound', 'alarm-2.mp3')
  
  if os.path.isfile(file_alarm):
    run_os_command(
      [conf.EXTERNAL_PLAYER_APP,
       '--quiet', '--really-quiet', '--no-video', '--volume=75',
       file_alarm],
      sync=True, hide=True)
  
  
def make_os_alarm_clock(**kwargs):
  """
  Создать будильник в стандартном планировщике ОС

  В текущей версии - будильник однократного запуска,
  поддерживается возможность установить `на завтра`,
  либо текущий день (по умолчанию).

  Дополнительно, в текущей версии указывается день (число) без наименования месяца.
  Система будет пытаться установать будильник на ближайший указанный день.

  Если не указан день или указан текущий, и время указано более раннее, чем текущее,
  то будильник создаётся на указанное время следующего дня.
  
  Новый будильник с тем же именем - перезаписывает предыдущий.
  """
  name    = kwargs.get('name', None)
  day     = kwargs.get('day', 'today')
  hours   = kwargs.get('hours', None)
  minutes = kwargs.get('minutes', 0)
  
  if not hours:
    return
  
  run_script = os.path.join(home_dir, 'script', 'clock_alarm.bat')

  # Определим день запуска
  now = datetime.now()
  clock_day = None
  clock_day_info = ''
  
  if not day or day == 'today':
    clock_day = now
    clock_day_info = 'на "сегодня"'
    
    # Если не указан день или указан текущий, и время указано более раннее, чем текущее,
    # то будильник создаётся на указанное время следующего дня.  
    check_time = now.replace(hour=hours, minute=minutes)
    if check_time <= now:
      clock_day = now + timedelta(days=1)
      clock_day_info = 'на "завтра"'
  
  elif day == 'tomorrow':
    clock_day = now + timedelta(days=1)
    clock_day_info = 'на "завтра"'
  
  else:    
    #todo: распознавание даты, либо дня недели
    #todo2: корректировка месяца
    #todo3: обработка корректного дня месяца
    try:
      clock_day = now.replace(day=day)
      is_check_day_ok = True
    except:
      clock_day = now.replace(day=1)
      is_check_day_ok = False
      
    if not is_check_day_ok or clock_day.day < now.day:
      try:
        clock_day = clock_day.replace(
          year = clock_day.year+1 if clock_day.month==12 else clock_day.year,
          month = 1 if clock_day.month==12 else clock_day.month+1,
          day = day
        )
      except:
        #todo
        say('Ошибка!')
        return False
    
    if clock_day:
      clock_day_info = f'день месяца: {clock_day.strftime("%d")}'
    
  run_time = f'{hours:02}:{minutes:02}'
  run_day = ''

  if not name:
    name = f'Malisa Alarm Clock at {clock_day.strftime("%d-%m-%Y")} {hours:02}-{minutes:02}'
    
  # Создаём будильник при помощи стандартной системной утилиты
  schtasks_command = [
    'schtasks',
    '/create',
    '/f',
    '/tn', name,
    '/tr', f'"{run_script}"',
    '/sc', 'once',
    '/st', run_time,
  ]
  
  if clock_day:
    run_day = f'{clock_day.strftime("%d/%m/%Y")}'
    schtasks_command.extend(['/sd', run_day])

  if clock_day_info:
    say(f'{clock_day_info}, на "{run_time}"')
  
  result = run_os_command(schtasks_command, sync=True, hide=True)
  return result


def make_metronome(**kwargs):
  """
  Создать метроном с указанными параметрами.
  
  Возможность выхода по голосовой команде, после определённого числа тактов.
  Возможность прерывания по `Ctrl-C` с клавиатуры.
  """  
  bpm         = kwargs.get('bpm', conf.METRONOME_DEFAULT_BPM)
  note_count  = kwargs.get('note_count', conf.METRONOME_DEFAULT_NOTE_COUNT)
  note_length = kwargs.get('note_length', conf.METRONOME_DEFAULT_NOTE_LENGTH)
  is_accent   = kwargs.get('is_accent', conf.METRONOME_DEFAULT_IS_ACCENT)
  is_shuffle  = kwargs.get('is_shuffle', conf.METRONOME_DEFAULT_IS_SHUFFLE)
  
  if bpm < 30 or bpm > 250:
    return False

  if note_length not in [1, 2, 4, 8, 16]:
    return False

  #if note_count not in [1, 2, 3, 4, 6, 8, 12]:
  #  return False
  
  tick_length = 0.005
  play_time   = int(tick_length * 1000)
    
  bpm   = 240.0 / note_length / bpm
  delay = bpm - tick_length
  
  freq_base    = conf.METRONOME_FREQ_BASE
  freq_accent  = conf.METRONOME_FREQ_ACCENT
  freq_shuffle = conf.METRONOME_FREQ_SHUFFLE
  
  silence_in_shuffle = conf.METRONOME_USE_SILENCE_IN_SHUFFLE
  
  # Возможен выход по `Ctrl-C` с клавиатуры
  try:
    beats = 0    
    
    while True:      
      for i in range(1, note_count + 1):
        if is_accent and i == 1:
          winsound.Beep(frequency=freq_accent, duration=play_time)
        
        elif is_shuffle and i in [2, 5, 8, 11]:
          if silence_in_shuffle:
            time.sleep(tick_length)
          else:
            winsound.Beep(frequency=freq_shuffle, duration=play_time)
        
        else:
          winsound.Beep(frequency=freq_base, duration=play_time)
          
        time.sleep(delay)
      
      # Возможен выход по голосовой команде после заданного числа тактов
      beats += 1      
      if (beats % conf.METRONOME_BEATS_COUNT_BEFORE_EXIT) == 0:
        winsound.Beep(frequency=1000, duration=300)
        if check_stop(listen_timeout=2, clear_screen=False): break
        winsound.Beep(frequency=1000, duration=300)

  except KeyboardInterrupt:
    winsound.Beep(frequency=1000, duration=300)
    return True
        
  return True


def print_microphones_info():
  """
  Вывести список доступных микрофонов в системе
  """
  print('\n-- Список устройств в системе: --\n')  
  
  microphones = sr.Microphone.list_microphone_names()    
  for index, name in enumerate(microphones):
      print(f"Microphone с именем '{name}' найден для 'Microphone [device_index = {index}]'")


def print_voice_engines_info():
  """
  Вывести список доступных голосовых движков в системе
  """
  print('\n-- Список голосовых движков в системе: --\n')
  if not tts: init_tts()
  
  if tts:
    voices = tts.getProperty('voices')  
    for index, voice in enumerate(voices):
      print(f"{index}: '{voice.name}' - '{voice.id}' - {str(voice.languages)}")

      
def get_lang_tag(lang_name):
  """
  Определение кода (тега) языка по его наименованию
  """
  lang_tag = ''
  if lang_name in ['русский', 'русского']:
    lang_tag = 'ru'
  elif lang_name in ['английский', 'английского']:
    lang_tag = 'en'
  elif lang_name in ['немецкий', 'немецкого']:
    lang_tag = 'de'
  elif lang_name in ['тайский', 'тайского']:
    lang_tag = 'th'
  elif lang_name in ['суахили', 'кисвахили']:
    lang_tag = 'sw'
  elif lang_name in ['португальский', 'португальского']:
    lang_tag = 'pt'  
  elif lang_name in ['китайский', 'китайского']:
    lang_tag = 'zh-cn'
  return lang_tag
  

def get_lang_and_country_code_by_tag(lang_tag):
  """
  Определение кода языка и страны по его тэгу
  """
  code = ''
  if lang_tag == 'ru':
    code = 'ru-RU'
  elif lang_tag == 'en': 
    code = 'en-US'
  elif lang_tag == 'de': 
    code = 'de-DE'
  elif lang_tag == 'th': 
    code = 'th-TH'
  elif lang_tag == 'sw': 
    code = 'sw-KE'  
  elif lang_tag == 'pt':
    # Бразильский вариант португальского
    code = 'pt-BR'
  elif lang_tag == 'zh-cn':
    code = 'zh-CN'
  return code
  

def init_tts():
  """
  Инициализация разговорного движка.
  Определение голосов для разных языков произношения.
  """  
  global tts
  global ru_voice_id
  global en_voice_id
  global de_voice_id
  global current_tts_lang
  
  if tts: return

  tts = pyttsx3.init()

  rate = tts.getProperty('rate')
  tts.setProperty('rate', conf.SPEECH_RATE_RU)

  volume = tts.getProperty('volume')
  tts.setProperty('volume', conf.SPEECH_VOLUME)
  
  voices = tts.getProperty('voices')
  
  for voice in voices:
    #print(f'{voice.name} - {voice.id} - {voice.languages}')
    
    # Английский
    if not en_voice_id:
      if conf.SPEECH_ENGINE_EN_NAME:
        if voice.name == conf.SPEECH_ENGINE_EN_NAME: en_voice_id = voice.id
      else:
        if 'Microsoft Anna' in voice.name: en_voice_id = voice.id
    
    # Русский
    if not ru_voice_id:
      if conf.SPEECH_ENGINE_RU_NAME:
        if voice.name == conf.SPEECH_ENGINE_RU_NAME: ru_voice_id = voice.id
    
    # Немецкий
    if not de_voice_id:
      if conf.SPEECH_ENGINE_DE_NAME:
        if voice.name == conf.SPEECH_ENGINE_DE_NAME: de_voice_id = voice.id

  # По возможности, первоначально устанавливается русский язык произношения
  # Если ничего не найдено - язык по умолчанию
  if ru_voice_id:
    tts.setProperty('voice', ru_voice_id)
    tts.setProperty('rate', conf.SPEECH_RATE_RU)
    current_tts_lang = 'ru'
  
  elif en_voice_id:
    tts.setProperty('voice', en_voice_id)
    tts.setProperty('rate', conf.SPEECH_RATE_EN)
    current_tts_lang = 'en'
  
  elif de_voice_id:
    tts.setProperty('voice', de_voice_id)
    tts.setProperty('rate', conf.SPEECH_RATE_DE)
    current_tts_lang = 'de'
  
  else:
    tts.setProperty('voice', 'default')
    tts.setProperty('rate', conf.SPEECH_RATE_EN)
    current_tts_lang = 'en'
    
  return tts


def say(text, lang='ru'):
  """
  Произнести фразу.
  По умолчанию - на русском языке. При необходимости - возможно сменить язык.
  """  
  global current_tts_lang
  
  if tts:
    if lang != current_tts_lang:
      if lang == 'ru': 
        tts.setProperty('voice', ru_voice_id)
        tts.setProperty('rate', conf.SPEECH_RATE_RU)
      elif lang == 'en': 
        tts.setProperty('voice', en_voice_id)
        tts.setProperty('rate', conf.SPEECH_RATE_EN)
      elif lang == 'de': 
        tts.setProperty('voice', de_voice_id)
        tts.setProperty('rate', conf.SPEECH_RATE_DE)      
      current_tts_lang = lang
    
    tts.say(text)
    tts.runAndWait()
    
    
def is_external_player_exists():
  """
  Проверка доступности внешнего приложения для проигрывания файлов
  """
  result = run_os_command([conf.EXTERNAL_PLAYER_APP, '--help', '--really-quiet'], sync=True, hide=True)
  return result
  

def say_by_external_engine(text, lang='ru', quiet=True, hide_external=True):
  """
  Озвучить текст другим способом, через внешние сервисы/программы.
  Добавлена возможность работать в `тихом` (скрытом) режиме.
  Добавлена возможность скрывать окно внешнего приложения.
  """
  if not quiet:
    info = 'Обработка внешним источником. Ожидайте...' 
    print(info)
    say(info)
  
  file_mp3 = os.path.join(home_dir, 'tmp', 'gTTS.mp3')
  
  try:
    external_tts = gTTS(text, lang=lang)
    external_tts.save(file_mp3)
    tts_result = True
    
  except Exception as e:
    tts_result = False
    print(f'Error when reading text: "{text}"')
    print(f'ERROR! {e}')
  
  if tts_result:
    result = run_os_command(
      [conf.EXTERNAL_PLAYER_APP,
       '--quiet', '--really-quiet', '--no-video', '--volume=50',
       file_mp3],
      sync=True,
      hide=hide_external)
  else:
    if not quiet:
      say('Ошибка!')
    
  if not quiet:
    print('Готово.')


def show_caption(caption):
  """
  Обозначить тему (заголовок) при выполнении действия
  """
  if caption:
    print(f'[{caption}]')
    say(f'{caption}:')
    

def listen_and_recognize(listen_timeout = None, lang='ru', clear_screen=True, ambient_duration=conf.AMBIENT_DURATION):
    """
    Прослушивании и распознавание речи
    (основная процедура, один шаг цикла)
    По умолчанию - на русском языке. При необходимости - возможно сменить язык.
    """
    
    text = ''
    #reco = sr.Recognizer()
    
    if clear_screen: print(ansi.clear_screen())
    
    #print('Проверка микрофона...')
    with sr.Microphone(device_index = conf.MICROPHONE_INDEX) as source:
      #print('Настройка...')      
      # Настройка обработки посторонних шумов
      reco.adjust_for_ambient_noise(source, duration = ambient_duration)
      
      if clear_screen: print('Слушаю...')
      
      try:
        audio = reco.listen(source, timeout = listen_timeout)
      except sr.WaitTimeoutError:
        audio = None
        text  = ''
    
    if audio:
      #if clear_screen: print('Услышала.')
      
      # Язык распознавания
      # По умолчанию
      reco_language = 'ru-RU'      
      
      reco_language = get_lang_and_country_code_by_tag(lang_tag = lang)
      if not reco_language: reco_language = 'ru-RU'
      
      if clear_screen: print('Распознавание...')
      
      try:     
        result = reco.recognize_google(audio, language = reco_language)
        text = result
        #print(f'Вы сказали: {text}')
      except:
        if clear_screen: print('Ошибка распознавания!')
        text = ''
    
    act_checking_time_to_sleep() ##!!
    return text
    

def check_stop(listen_timeout=3, clear_screen=True, silently=True):
  """
  Проверка возможности выхода в циклах
  """
  if not silently: say('Продолжаю?')

  text = listen_and_recognize(listen_timeout=listen_timeout, clear_screen=clear_screen).lower()
  
  if 'стоп' in text or 'хватит' in text \
      or 'окей' in text or "о'кей" in text \
      or 'нет' == text \
      or 'спасибо' in text:
    say('Окей')
    return True
  else:
    return False
  

def is_action_valid(action_name, reaction_type=None):
  """
  Проверка наличия и корректности action-процедуры по её наименованию.
  Используется при загрузке карты реакций.
  
  По умолчанию поиск осуществляется сначала среди системных процедур, потом - среди пользовательских.
  Однако, можно явно указать, в какой области проводить проверку: reaction_type == None | 'system' | 'user'
  """
  if not action_name:
    return False
    
  result = False
  action = None
  
  if (not reaction_type or reaction_type == 'system'):
    action = globals().get(action_name, None)
    
  if not action \
     and (not reaction_type or reaction_type == 'user'):
    
    if os.path.isfile(os.path.join(home_dir, 'actions', f'{action_name}.py')):
      try:
        action_external_module = importlib.import_module(f'actions.{action_name}')
      except Exception as e:
        action_external_module = None
      
      if action_external_module:
        action = getattr(action_external_module, 'action', None)
  
  if action and type(action).__name__ == 'function':
    result = True
  
  return result


def run_action(action_name, text='', reaction_type=None):
  """
  Найти и выполнить action-процедуру по её наименованию.
  Сначала ищем среди встроенных в ядро action-процедур.
  Затем - среди пользовательских action-процедур, в каталоге `actions`.
  
  По умолчанию поиск осуществляется среди всех процедур - сначала среди системных, потом - среди пользовательских.
  Однако, можно явно указать, в какой области искать процедуру: reaction_type == None | 'system' | 'user'
  """
  action_internal = None
  
  if (not reaction_type or reaction_type == 'system'):
    action_internal = globals().get(action_name, None)

    if action_internal and type(action_internal).__name__ == 'function':
      try:
        action_internal(text=text)
      except Exception as e:
        print(f'Ошибка при выполнении встроенной action-процедуры "{action_name}"!')
        print(e)
        beep()
    else:
      if reaction_type == 'system':
        print(f'Не найдена встроенная action-процедура "{action_name}"!')
        beep()

  if not action_internal \
     and (not reaction_type or reaction_type == 'user'):
    
    action_file = os.path.join(home_dir, 'actions', f'{action_name}.py')
    if not os.path.isfile(action_file):
      print(f'Ошибка. Не найден файл "actions/{action_name}.py" с внешней action-процедурой!')
      beep()
      return ##
    
    try:
      action_external_module = importlib.import_module(f'actions.{action_name}')
    except Exception as e:
      action_external_module = None
      print(f'Ошибка при загрузке внешней action-процедуры "{action_name}"!')
      print(e)      
      beep()

    if action_external_module:
      action_external = getattr(action_external_module, 'action', None)
      
      if not action_external or type(action_external).__name__ != 'function':
        print(f'Не найдена точка входа для внешней action-процедуры "{action_name}"!')
        beep()      
      else:
        try:
          action_external(text=text)
        except Exception as e:
          print(f'Ошибка при выполнении внешней action-процедуры "{action_name}"!')
          print(e)
          beep()


def load_reactions_map():
  """
  Загрузка `карты реакций` из конфигурации
  """
  global reactions_map

  # Системные реакции
  reactions_map = reaction.load_reactions_map(type='system', is_action_valid_proc=is_action_valid)
  
  if not reactions_map:
    print('Проблема при загрузки карты реакций!\n\a')
    sys.exit(0)
    
  # Пользовательские реакции
  user_reactions_map = reaction.load_reactions_map(type='user', is_action_valid_proc=is_action_valid)
  
  if not user_reactions_map:
    print('Проблема при загрузки пользовательской карты реакций!\n')

  # Пользвательские реакции объединяются с системными
  if user_reactions_map:
    reactions_map.extend(user_reactions_map)

  
def make_reaction_via_map(text):
  """
  Определить реакцию (действие) системы на основании карты реакций
  """
  result = False
  
  if reactions_map:
    result = reaction.make_reaction_via_map(text, reactions_map, say_proc=say, run_action_proc=run_action)
    
  return result


## ---------------------------------------------------------------------------------------------##
def make_reaction(text):
  """
  Основная процедура обработки команд.
  Инициируется наличием имени робота в начале фразы.
  """  
  ## act_checking_time_to_sleep() ##!!
  
  if not text: return
  
  robot_name = conf.ROBOT_NAME.lower()
  robot_name_length = len(robot_name)
    
  text = text.lower()
  isCensored = False
  
  if not text or not text.startswith(robot_name):
    #say('Ошибка распознавания!')
    #say("Не поняла Вас!")
    #say("Не для меня.")
    return
    
  # Если фраза - требует действия, убираем имя робота в начале. Иначе отдаем имя дальше.
  if text != robot_name:
    text = text[(robot_name_length + 1):].strip()

  # -- Цензура ---------------------------------------------------------------------
  for word in bad_words:
    if word in text:
      isCensored = True
      say('Ругаться не хорошо!!')
      break  
  # -- end Цензура -----------------------------------------------------------------
    
  ## -- Выбор реакции системы ------------------------------------------------- ##
  # Определение реакции (действия) системы на основании карты реакций.
  # Находим самое первое возможное действие, удовлетворяющее условиям.
  result = make_reaction_via_map(text)
    
  if not result:
    if not isCensored:
      print(f'>> {text}')
      say(f'Вы сказали: {text}. Я Вас не поняла.')    
  ## -- end Выбор реакции системы ----------------------------------------------##    
## ---------------------------------------------------------------------------------------------##

## -- ACTIONS (действия) ---------------------------------------------------------------------- ##
def act_i_am_ready(**kwargs):
  """
  Подтверждение готовности
  """
  answer = random.choice(robot_answers)
  say(answer)    

  text = listen_and_recognize()
  if text: 
    if not text.lower().startswith(conf.ROBOT_NAME.lower()):
      text = f'{conf.ROBOT_NAME} {text}'
    make_reaction(text)


def act_exit(**kwargs):
  """
  Закрытие программы-робота
  """
  close_databases()
  
  say('Пока!')
  print(ansi.clear_screen())
  sys.exit(0)
  

def act_say_anekdot(**kwargs):
  """
  Анекдот
  """
  show_caption('Анекдот')

  url = 'http://rzhunemogu.ru/Rand.aspx?CType=1'
  try:
    content = requests.get(url).text
    data = ET.fromstring(content)
    result = data[0].text
  except Exception as e:
    print(e)
    result = None
  
  if result:
    print(f'{ANSI_CYAN_BRIGHT}\n{result}\n')
    say(result)
  else:
    say('Пока не знаю ни одного!')

  
def act_say_quote(**kwargs):
  """
  Умная мысль, цитата, мудрость
  """
  show_caption('Цитата')
  
  quote = ''
  if quotes:
    quote_choice = random.choice(quotes)
    
    quote = quote_choice[1]
    is_best_quote = quote_choice[2]
    
    if quote.startswith('__'):
      is_best_quote = True
      quote = quote.strip('_')
      
  if quote:
    quote_style = ANSI_GREEN_BRIGHT if is_best_quote else ANSI_CYAN_BRIGHT
    
    print(f'{quote_style}\n {quote}\n')
    say(quote)
  else:
    say('Пока не знаю ни одной!')
  

def act_say_irr_verb(**kwargs):
  """
  Неправильный глагол
  """
  verb_value = ''
  
  if irr_verbs:
    verb = random.choice(irr_verbs)
    
    verb_form1 = verb[1]
    verb_form2 = verb[2]
    verb_form3 = verb[3]
    verb_ru    = verb[4]
    
    verb_value = verb_ru
    verb_forms = f'{verb_form1}, {verb_form2}, {verb_form3}.'
  
  if verb_value:
    print(f'{ANSI_GREEN_BRIGHT}\n{verb_value.upper()} ==> '
          f'{ANSI_CYAN_BRIGHT} {verb_form1.upper()} - {verb_form2.upper()} - {verb_form3.upper()}\n')
    
    say(verb_value)
    time.sleep(2)
    say(verb_forms,'en')
  else:
    say('Затрудняюсь сейчас ответить!')


def act_say_irr_verbs(**kwargs):
  """
  Неправильные глаголы в цикле
  """
  show_caption('Неправильные глаголы')
  
  while True:
    act_say_irr_verb()
    if check_stop(clear_screen=False): break
    
    
def act_say_phrasal_verb(**kwargs):
  """
  Фразовый глагол
  """
  verb_value = ''
  
  if phrasal_verbs:
    verb = random.choice(phrasal_verbs)
    variant = random.choice(verb['variations'])
    
    verb_value = f"{verb['verb']} {variant['preposition']}"
    meaning    = variant['meaning']
    
    # todo: при необходимости - отобразить и озвучить примеры
    #example    = variant['example']
  
  if verb_value:
    print(f'{ANSI_GREEN_BRIGHT}\n{verb_value.upper()} --> {ANSI_CYAN_BRIGHT}"{meaning}"\n')
    
    say(verb_value, 'en')
    time.sleep(2)
    say(meaning)
  else:
    say('Затрудняюсь сейчас ответить!')


def act_say_phrasal_verbs(**kwargs):
  """
  Фразовые глаголы в цикле
  """
  show_caption('Фразовые глаголы')
  
  while True:
    act_say_phrasal_verb()
    if check_stop(clear_screen=False): break


def act_dollar_course(**kwargs):
  """
  Курс доллара
  """
  show_caption('Доллар')
  
  url = f'https://www.cbr-xml-daily.ru/daily_json.js'
  try:
    data = requests.get(url).json()
    value = int(round( data['Valute']['USD']['Value'], 0))
  except Exception as e:
    print(e)
    value = None
  
  if value:
    info = f'Курс доллара - {value}'
    print(f'{ANSI_CYAN_BRIGHT}\n{info}')
    say(info)
  else:
    say('Не знаю')  


def act_euro_course(**kwargs):
  """
  Курс евро
  """
  show_caption('Евро')
  
  url = f'https://www.cbr-xml-daily.ru/daily_json.js'  
  try:
    data = requests.get(url).json()
    value = int(round( data['Valute']['EUR']['Value'], 0))
  except Exception as e:
    print(e)
    value = None

  if value:
    info = f'Курс евро - {value}'
    print(f'{ANSI_CYAN_BRIGHT}\n{info}')
    say(info)
  else:
    say('Не знаю')
  

def act_weather_now_info(**kwargs):
  """
  Информация о погоде в текущий момент времени
  """
  show_caption('Информация о погоде')
    
  url = (f'https://api.openweathermap.org/data/2.5/weather?q={conf.WEATHER_CITY}'
         f'&lang=ru&units=metric&APPID={conf.WEATHER_API}')
  
  now_weather_info = None  
  try:
    data = requests.get(url).json()
    #pprint(data)
    now_weather_info = weather.get_now_weather_info(data)
             
  except Exception as e:
    print(e)
    now_weather_info = None
    
  if now_weather_info:
    print(f'{ANSI_CYAN_BRIGHT}\n{now_weather_info}')
    say(now_weather_info)
  else:
    say('Информация недоступна')


def act_weather_info(**kwargs):
  """
  Информация о погоде (прогноз)
  """
  show_caption('Прогноз погоды')

  url = (f'https://api.openweathermap.org/data/2.5/onecall?lat={conf.WEATHER_PLACE_LAT}&lon={conf.WEATHER_PLACE_LON}'
         f'&exclude=minutely,hourly&lang=ru&units=metric&APPID={conf.WEATHER_API}')
  
  result = None
  try:
    data = requests.get(url).json()
    #pprint(data)
    
    current_weather = data['current']
    daily_weather_blocks = data['daily']    
    
    try:
      alerts = data['alerts']      
      # Информация об оповещениях
      alerts_info = weather.get_weather_alerts_info(alerts)
    
    except Exception as e:
      print(e)
      alerts_info = None
    
    if alerts_info:
      print(f'{ANSI_BLACK_ON_WHITE}\n{alerts_info}')
      #say(alert_info)
    
    # Информация текущего дня
    current_weather_info = weather.get_current_weather_info(current_weather)
    
    if current_weather_info:
      print(f'{ANSI_CYAN_BRIGHT}\n{current_weather_info}')
      say(current_weather_info)
    else:
      say('Информация недоступна')
      
    if check_stop(clear_screen=False):
      return
    
    # Прогноз по дням (на 7 дней)
    for daily_weather in daily_weather_blocks[1:]:
      daily_weather_info = weather.get_daily_weather_info(daily_weather)
      
      if daily_weather_info:
        print(f'{ANSI_CYAN_BRIGHT}\n{daily_weather_info}')
        say(daily_weather_info)
      else:
        say('Информация недоступна')
      
      if check_stop(clear_screen=False): break

  except Exception as e:
    print(e)
    result = None
    
  say('Обзор погоды завершён.')


def act_read_news(**kwargs):
  """
  Обзор новостей с `newsapi.org`
  """
  show_caption('Новости')
  
  news = news_engine.get_news()
    
  if news:
    for n in news:      
      # Новости только из определённых источников
      result = n.rsplit(' - ', 1)
      
      source = result[-1]
      title = result[0]
      
      # Исключаем источники
      exclude_sources_keywords = [
        'Star', 'Чемпионат', 'Sports', 'Чемпионат', 'Спорт', '.com', 
        '3DNews', 'Hi-Tech', 'Mail', 'Auto', 'Авто', 'Росбалт', 'e1.ru', 'Game', 'Player'
      ]
      if check_any_partial_match(source, exclude_sources_keywords): continue
      
      print(f'\n{title} - ({source})')
      say(title)
      #time.sleep(1)
      if check_stop(clear_screen=False): break
      
    say('Обзор завершён.')
  else:
    say('Информация недоступна')  
    

def act_read_amic_news(**kwargs):
  """
  Обзор новостей `amic.ru`
  """
  show_caption('Новости А-мик')
  
  news = news_engine.get_news_amic()
  
  if news:
    for n in news:
      print(f'\n{n}')
      say(n)
      #time.sleep(1)
      if check_stop(clear_screen=False): break
    
    say('Обзор завершён.')
  else:
    say('Информация недоступна')  
  

def act_read_altapress_news(**kwargs):
  """
  Обзор новостей `altapress.ru`
  """
  show_caption('Новости Алтапресс')

  news = news_engine.get_news_altapress()
  
  if news:
    for n in news:
      print(f'\n{n}')
      say(n)
      #time.sleep(1)
      if check_stop(clear_screen=False): break
      
    say('Обзор завершён.')
  else:
    say('Информация недоступна')
    
    
def act_read_habr_news(**kwargs):
  """
  Обзор новостей с сайта `habr.com`
  Возможно указание раздела, варианты: 'news', 'best/daily', 'all/top50', 'all/all'
  По умолчанию - `news` (актуальные новости)
  """
  chapter = kwargs.get('chapter', 'news')
  
  show_caption('Новости и статьи Хаб-ра')
  
  news = news_engine.get_news_habr(chapter=chapter)
  
  if news:
    for n in news:
      print(f'\n{n}')
      say(n)
      if check_stop(clear_screen=False): break
      
    say('Обзор завершён.')
  else:
    say('Информация недоступна')  
  

def act_read_habr_news_best_daily(**kwargs):
  """
  Обзор новостей с сайта `habr.com`
  (список статей, лучшее за день)
  """
  act_read_habr_news(chapter='best/daily')


def act_read_habr_news_all_top50(**kwargs):
  """
  Обзор новостей с сайта `habr.com`
  (список статей, топ-50)
  """
  act_read_habr_news(chapter='all/top50')
  

def act_read_habr_news_all(**kwargs):
  """
  Обзор новостей с сайта `habr.com`
  (список статей, всё подряд)
  """
  act_read_habr_news(chapter='all/all')

  
def act_memorize_text(**kwargs):
  """
  Сохранить надиктованный текст.

  Возможно сохранять многострочный текст, диктуя каждую строку отдельно.
  Для завершения записи произносится ключевая фраза "Запись завершена".

  Сформированный текст копируется в буфер обмена, а также сохраняется на диске в виде txt-файла в каталоге "./memo/",
  с актуальной меткой даты-времени в наименовании.
  """
  print('[Записать текст]')  
  say('Говорите')

  text = ''

  while True:
    #text_new = listen_and_recognize(ambient_duration=7)
    #text_new = listen_and_recognize(listen_timeout=10, clear_screen=False, ambient_duration=10)
    #text_new = listen_and_recognize(listen_timeout=3, clear_screen=False, ambient_duration=3)
    text_new = listen_and_recognize(clear_screen=False)

    if not text_new or len(text_new) == 0:
      continue

    if 'запись завершена' in text_new.lower():
      break
    else:
      print(f'{text_new}')
      text += f'{text_new}\n'
      time.sleep(0.4)
      winsound.Beep(frequency=400, duration=400)
  
  if text and len(text.replace('\n','').replace(' ', '')) > 0:
    copyclip(text)
    
    now = datetime.now()
    save_to_file = os.path.join(home_dir, 'memo', f'm_{now.strftime("%Y-%m-%d_%H-%M-%S_%f")}.txt')
    
    with open(save_to_file, 'w', encoding='utf-8') as f:
      f.write(text)    
    
    say('Сохранено в буфер обмена')
  else:
    say('Не поняла.')


def act_pc_shutdown(**kwargs):
  """
  Завершение работы компьютера
  """
  show_caption('Завершение работы')
  close_databases()
  
  say('Счастливо!')
  run_os_command(['shutdown', '/s', '/t', '15'])
  

def act_pc_restart(**kwargs):
  """
  Перезагрузка компьютера
  """
  show_caption('Перезагрузка')
  close_databases()
  
  say('Перезагрузка!')
  run_os_command(['shutdown', '/r', '/t', '10'])
  

def act_pc_shutdown_abort(**kwargs):
  """
  Отмена завершения/перезагрузки компьютера
  """
  show_caption('Отмена завершения работы')
  
  run_os_command(['shutdown', '/a'], sync=True)
  open_databases()
  say('Работайте.')


def act_vpn_connect(**kwargs):
  """
  Открыть соединение VPN
  """
  show_caption('Открываю VPN')
  
  cmd = [conf.OPENVPN_GUI_APP,
         '--show_balloon', '0', 
         '--silent_connection', '1',
         '--show_script_window', '0',
         '--config_dir', conf.OPENVPN_CONFIG_DIR,
         '--command', 'connect', conf.OPENVPN_CONFIG_FILE]
  run_os_command(cmd)
  
  sleep(10)
  say('Готово')


def act_vpn_disconnect(**kwargs):
  """
  Закрыть соединение VPN
  """
  show_caption('Закрываю VPN')
  
  cmd = [conf.OPENVPN_GUI_APP, 
         '--command', 'disconnect_all']
  run_os_command(cmd)
  
  sleep(5)
  say('Готово')


def act_mstsc_connect(**kwargs):
  """
  Открыть окно RDP
  """
  show_caption('Открываю RDP')
  
  cmd = ['mstsc', f"{os.path.join(home_dir, 'rdp', conf.RDP_CONFIG_FILE)}"]
  run_os_command(cmd)
  
  sleep(5)
  say('Готово')


def act_rocket_chat_gui_connect(**kwargs):
  """
  Открыть окно Rocket.Chat
  """
  show_caption('Открываю Рокет Чат')
  
  cmd = [conf.ROCKET_CHAT_APP]
  run_os_command(cmd)
  
  sleep(20)
  say('Готово')
  

def act_rocket_chat_gui_logon(**kwargs):
  """
  Начальная авторизация в окне Rocket.Chat
  """
  show_caption('Рокет Чат Вход')
  
  wnd = None
  try_count = 0
  
  # Ожидаем появление окна
  while True:
    sleep(2)

    try:
      wnds = pyautogui.getWindowsWithTitle(conf.ROCKET_CHAT_TITLE)
      if wnds:
        wnd = wnds[0]
        break
    except Exception as e:
      print(e)
    
    try_count += 1
    if try_count >= 30:
      break
  
  # Окно найдено
  if wnd:
    wnd.maximize()
    sleep(4)
    
    wnd.activate()
    sleep(4)
    
    pyautogui.hotkey('ctrl', '1')
    sleep(4)
    
    pyautogui.click(x=conf.ROCKET_CHAT_X_HACK, y=conf.ROCKET_CHAT_Y_HACK, button='left') # hack
    
    pyautogui.write(conf.ROCKET_CHAT_LOGIN, interval=conf.GUI_WRITE_INTERVAL)
    pyautogui.press('tab')
    pyautogui.write(conf.ROCKET_CHAT_PWD, interval=conf.GUI_WRITE_INTERVAL)
    pyautogui.press('enter')  
    
    wnd.minimize()
    
    sleep(10)
    say('Готово')  
  else:
    say('Рокет Чат не найден.')
      

def act_rocket_chat_send_hello(**kwargs):
  """
  Отправить "Привет" в рабочий (Rocket) чат
  """
  show_caption('Отправка "Привет!" в Рокет Чат')
  result = rocket.rocket_chat_send_hello()
  
  if result:
    say('Отправлено успешно!')
  else:
    say('Проблемы при отправке!')
  

def act_rocket_chat_send_bye(**kwargs):
  """
  Отправить "Пока" в рабочий (Rocket) чат
  """
  show_caption('Отправка "Пока!" в Рокет Чат')
  result = rocket.rocket_chat_send_message(conf.ROCKET_CHAT_MESSAGE_BYE, to_channel=conf.ROCKET_CHAT_CHANNEL_HELLO)
  
  if result:
    say('Отправлено успешно!')
  else:
    say('Проблемы при отправке!')

  
def act_rocket_chat_get_all_standup_info(**kwargs):
  """
  Получить информацию из канала "планёрка" о том, что делали другие
  """
  show_caption('Информация по планёрке')  
  info = rocket.rocket_chat_get_all_standup_info()
  
  if info:
    text = ''.join(info)
    
    # Отображение на экране
    text_for_print = '\n' + text.replace('###', ANSI_YELLOW_BRIGHT).replace('##', ANSI_STYLE_RESET) + '\n'
    print(text_for_print)

    # Озвучивание внешним источником, весь текст целиком, с возможностью прерывания
    ## say_by_external_engine(text, quiet=False)
    
    # Озвучивание средствами робота, частями, с возможностью прерывания после каждой части
    for message in info:
      say(message)
      if check_stop(clear_screen=False, silently=False): break
      
    say('Брифинг завершён.')    
  
  else:
    say('Информация отсутствует. Возможно, проблемы с получением.')
  
  
def act_rocket_chat_send_my_standup(**kwargs):
  """
  Отправить информацию 'что делал / что буду делать' в канал "планёрка"
  """
  show_caption('Отправка списка дел в Рокет Чат')
  result = rocket.rocket_chat_send_my_standup()
  
  if result:
    say('Отправлено успешно!')
  else:
    say('Проблемы при отправке!')
    
    
def set_system_volume(value):
  """
  Установка громкости звука ОС
  """
  run_os_command([conf.SET_VOLUME_APP, f'{value}'], sync=True)
  

def check_is_app_running(app_name):
  """
  Проверка, что указанное приложение запущено
  """
  result = False
  app_name = app_name.lower()
  
  for proc in psutil.process_iter():
    if proc.name().lower() == app_name and proc.status() == 'running':
      result = True
      break      
  
  return result
  
  
def check_is_vpn_connected():
  """
  Проверка, что запущено приложение VPN и соединение успешно установлено
  """
  result = False
  
  # Проверка процесса
  app_name = os.path.basename(conf.OPENVPN_GUI_APP)
  is_app_running = check_is_app_running(app_name)
  
  if is_app_running:
    # Дополнительная проверка лога соединения
    try:
      with open(conf.OPENVPN_LOG_FILE) as f:
        log_last_line = f.readlines()[-1]
    except:
      log_last_line = ''
    
    if log_last_line and 'Initialization Sequence Completed' in log_last_line:
      result = True
      
    #todo: при необходимости, добавить проверку доступности целевого хоста
  
  return result


def check_is_rocket_chat_gui_open():
  """
  Проверка, что запущено приложение Rocket.Chat и имеется окно для взаимодействия
  """
  result = False

  # Проверка процесса
  app_name = os.path.basename(conf.ROCKET_CHAT_APP)
  is_app_running = check_is_app_running(app_name)
  
  if is_app_running:
    # Дополнительно пытаемся найти окно приложения
    wnd = None
    try_count = 0
    
    # Ожидаем появление окна
    while True:
      sleep(2)      
      wnds = pyautogui.getWindowsWithTitle(conf.ROCKET_CHAT_TITLE)
      if wnds:
        wnd = wnds[0]
        break            
      try_count += 1
      if try_count >= 30:
        break    
    
    # Окно найдено
    if wnd:
      result = True
  
  return result
  

def act_open_workplace(**kwargs):
  """
  Комплексная инициализация удалённого рабочего места.
  Подготовка к работе удалённо.
  """
  show_caption('Настройка удалённого рабочего пространства')
  say('Ожидайте.')
  
  act_vpn_connect()
  sleep(20)
  
  if check_is_vpn_connected():
    print('VPN - ok')
    
    act_rocket_chat_gui_connect()
    sleep(10)
    print('Rocket Chat')
    
    if check_is_rocket_chat_gui_open():
      try:
        act_rocket_chat_gui_logon()
        sleep(8)
        print('Rocket Chat Logon')
      except Exception as e:
        print(e)
        print('Rocket Chat Logon Error!')

    act_mstsc_connect()
    sleep(10)
    print('RDP')
    
    #todo: возможно, сделать несколько необходимых запросов к Базе данных via SSH

  # Отправка приветствия в рабочий чат
  is_send_hello = kwargs.get('send_hello', conf.ROCKET_CHAT_IS_SEND_HELLO)
  
  if is_send_hello:  
    act_rocket_chat_send_hello()
    sleep(3)
    print('Rocket Chat Send "Hello!"')
  
  # Корректировка громкости звука
  set_system_volume(conf.SYSTEM_VOLUME_DEFAULT)

  say('Работайте.')

  
def act_checking_time_to_sleep(**kwargs):
  """
  Проверка необходимости идти спать
  """
  disable_sleep_time_checking = getattr(conf, 'DISABLE_SLEEP_TIME_CHECKING', 0)
  if disable_sleep_time_checking == 1: return
  
  now = datetime.now()
  time_to_sleep = now.replace(hour = (conf.TIME_TO_SLEEP_HOUR or 23), minute = (conf.TIME_TO_SLEEP_MINUTE or 40))
  
  # Учитываем также 'ночное время'
  if now.hour < 6: time_to_sleep -= timedelta(days=1)
  
  if now > time_to_sleep:
    beep(count=2)
    say('Пора спать, уважаемый. Время уже позднее.')
    time.sleep(3)


def wait_while_music_playing():
  """
  Версия 2.0 (экспериментальная)
  Ожидание, пока играет музыка, с частичным распознаванием команд.
  В дальнейшем планируется оптимизация указанного функционала.
  """
  while True:
    sleep(1)  
    
    try:
      player = pyaimp.Client()
    except:
      player = None
      beep()
      return
      
    if player:
      state = player.get_playback_state()      
      
      if state != pyaimp.PlayBackState.Playing:
        beep()
        return      
      
      else:
        # Возможность остановки плеера, голосовой командой с именем робота
        text = listen_and_recognize(listen_timeout=2, clear_screen=False).lower()
        if conf.ROBOT_NAME.lower() in text:
          player.pause()
          #beep()
          say('Окей')
          return
  
  
def act_radio_open_and_play(**kwargs):
  """
  Проигрывание музыки в определённом стиле
  """
  text = kwargs.get('text', '')
  use_random_link = kwargs.get('use_random_link', False)
  
  show_caption('Запуск')
  
  cmd = [conf.AIMP_PATH, '/PAUSE']
  run_os_command(cmd)
  
  sleep(3)
  try:
    player = pyaimp.Client()
  except:
    say('Проблема с запуском плеера')
    return
    
  radio_link = ''

  if use_random_link:
    # Получим случайную ссылку на потоковое вещание (из доступных ссылок)
    radio_link = radio.get_radio_link_random()
    if radio_link: say('Случайная ссылка.')
  
  else:
    # Поиск ссылки на потоковое радио на основании указанного стиля
    radio_link = radio.get_radio_link_by_style(text)
    if radio_link: say('Стиль определён.')
  
  if radio_link:
    play_object = radio_link
  else:
    # Плэйлист по умолчанию (локальный)
    say('Плейлист - по умолчанию.')
    play_object = os.path.join(home_dir, 'playlist', conf.PLAYLIST_DEFAULT)

  player.add_to_playlist_and_play(play_object)
  player.set_volume(85)
  
  sleep(2)
  wait_while_music_playing() ##


def act_radio_open_and_play_random(**kwargs):
  """
  Проигрывание музыки в определённом стиле, выбранном случайно
  """
  text = kwargs.get('text', '')
  act_radio_open_and_play(text=text, use_random_link=True)
  
  
def act_radio_pause(**kwargs):
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


def act_radio_play(**kwargs):
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
      
      sleep(2)
      wait_while_music_playing() ##


def act_radio_stop(**kwargs):
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


def act_realty_info(**kwargs):
  """
  Общая информация о ценах на недвижимость
  """
  show_caption('Статистика по недвижимости')
  
  for place in (conf.REALTY_CITIES + conf.REALTY_REGIONS):
    url = (f'https://opendata.domclick.ru/app/api/v2/places/{place}'
           f'?metric_group=offers&period=last_30_days&period_count=1&show_in=banner')

    try:
      data = requests.get(url).json()
      #pprint(data)
      
      caption = data['data']['caption']
      metrics = data['data']['metrics']
      
      metrics_info = ''      
      for m in metrics:
        metrics_info += (f"\n{m['caption']}: "
                         f"'{m['values'][0]['formatted_full']}'. "
                         f"Дельта: '{m['delta_formatted']}'. ")
      
      realty_info = f"\n###{caption}: ## {metrics_info.replace('м²', 'мкв').replace('₽', 'рублей')}"
    
    except Exception as e:
      print(e)
      realty_info = None
    
    if realty_info:
      print(realty_info.replace('###', ANSI_GREEN_BRIGHT).replace('##', ANSI_STYLE_RESET))
      say(realty_info)
    else:
      say(f'{place}: Затрудняюсь ответить')
      
    if check_stop(clear_screen=False): break
  say('Отчёт завершён.')
  

def act_current_time_info(**kwargs):
  """
  Информация о текущем времени
  """
  show_caption('Текущее время')
    
  now = datetime.now()  
  time_info_print = f'{now.strftime("%H:%M, %A, %B %d")}'
  time_info = f'{now.strftime("`%H`, `%M`. %A. %B, %d.")}'
    
  if time_info:
    print(f'{ANSI_CYAN_BRIGHT}\n {time_info_print}\n')
    say(time_info)


def act_learn_words_deutsch(**kwargs):
  """
  Изучение слов немецкого языка
  """
  show_caption('Слова немецкого языка')

  words_was_shown = {}
  
  while True:
    words = random.choice(dicts_deutsch_all)
    word = random.choice(words)
    
    value_de = word.get('value_de')
    value_de_trans = word.get('value_de_trans')
    value_ru = word.get('value_ru')

    noun_de = word.get('value_de_noun')
    part_of_speech = word.get('part_of_speech')

    phrase_de = word.get('phrase_de')
    phrase_de_trans = word.get('phrase_de_trans')
    phrase_ru = word.get('phrase_ru')

    prompt = word.get('prompt')

    # Показывать одно и то же слово не более заданного количества раз
    dict_type = word.get('dict_type', 'base')
    keyword = f'{dict_type}__{value_de if value_de else phrase_de}'

    if keyword in words_was_shown:
      count = words_was_shown[keyword]
      if count >= WORD_REPEAT_COUNT: continue
    else:
      words_was_shown[keyword] = 0    
        
    is_noun = True if (noun_de or (part_of_speech and part_of_speech.startswith('сущ.'))) else False
    word_style = ANSI_CYAN_BRIGHT if is_noun else ANSI_YELLOW_BRIGHT

    # Выводим на экран
    if value_de:
      part_of_speech = f' | {part_of_speech}' if part_of_speech else ''
      info = f"{word_style} {value_de} {ANSI_STYLE_RESET} ({value_de_trans}{part_of_speech}) - {ANSI_GREEN_BRIGHT}{value_ru.upper()}"
      print(f'\n{info}\n')

    if prompt:
      info = f"{ANSI_CYAN_BRIGHT} {prompt}"
      print(f'{info}')
    
    if phrase_de:
      info = f"{word_style} {phrase_de} {ANSI_STYLE_RESET}({phrase_de_trans}) - {ANSI_GREEN_BRIGHT}{phrase_ru}"
      print(f'{info}\n')
    
    sleep(5)
    
    # По-быстрому организуем повтор выбранного варианта
    while True:
      # Проговариваем вслух
      if value_de:
        say_by_external_engine(value_de, 'de')
        say_by_external_engine(value_ru, 'ru')

      if phrase_de:
        sleep(3)
        say_by_external_engine(phrase_de, 'de')
        say_by_external_engine(phrase_ru, 'ru')

      try:
        ii = inputimeout(prompt=('_' * 40), timeout=7)
      except TimeoutOccurred:
        ii = ''      
      if (ii == 'p'): ii = input('.' * 40) # Пауза
      if (ii == 'q'): break
      if (ii != 'r'): break
  
    #try:
    #  i = inputimeout(prompt=('_' * 60), timeout=7)
    #except TimeoutOccurred:
    #  i = ''
    #if (i == 'p'): i = input('.' * 40) # Пауза
    #if (i == 'q'): break
    
    if check_stop(clear_screen=False): break

    words_was_shown[keyword] += 1

  say('Сделано.')
  
  
def act_web_search(**kwargs):
  """
  Поиск указанноого текста в сети Интернет
  """
  text = kwargs.get('text', '')
  if not text: return
  
  show_caption('Поиск в сети')
  
  keywords = 'поиск|найди|поищи|сети|интернете|интернет'

  try:
    search_string = re.split(keywords, text)[-1].strip()
  except:
    search_string = ''
  
  if web_browser and search_string:
    web_browser.open(f'{conf.WEB_SEARCH_ENGINE_DEFAULT}{search_string}', new=2)
  
  say('Сделано.')
  

def translate_text(text, to_lang='ru', from_lang='auto'):
  """
  Перевод текста на указанный язык (используется Google-переводчик)
  """
  if not text: return ''
  result_text = ''
  
  try:
    translated = translator.translate(text, src=from_lang, dest=to_lang)
    result_text = translated.text
    pronunciation = translated.pronunciation
  except Exception as e:
    result_text = ''
    pronunciation = ''
    print(f'ERROR! {e}')
  
  return result_text


def act_translate_text(**kwargs):
  """
  Перевод текста на указанный язык (используется Google-переводчик)
  
  Общий формат команды (параметра `text`):
  "(`перевод` | `переведи`) GOALTEXT [`на` TOLANG] [(`с` |'с языка') FROMLANG]"
  
  Если язык требуемого для перевода текста отличается от русского,
  его можно будет произнести отдельно, по запросу системы.
  """
  text = kwargs.get('text', '')
  if not text: return
  
  # С какого языка
  if 'с языка' in text:
    (text, from_lang_name) = extract_value_from_text(text, 'с языка', '')
  else:
    (text, from_lang_name) = extract_value_from_text(text, 'с', '')
  
  if not from_lang_name:
    from_lang = 'auto'
  else:
    from_lang = get_lang_tag(from_lang_name)
    if not from_lang: from_lang = 'auto'
    
  # На какой язык
  (text, to_lang_name) = extract_value_from_text(text, 'на', '')  

  if not to_lang_name:
    if from_lang not in ['auto', 'ru']:
      to_lang = 'ru'
    else:
      to_lang = 'en'
  else:
    to_lang = get_lang_tag(to_lang_name)
    if not to_lang: to_lang = 'en'
  
  # Текст для перевода
  # Фишка! При необходимости - отдельное распознавание текста с учётом языка, с которого переводим
  if from_lang not in ['auto', 'ru']:
    say('Говорите.')
    text = listen_and_recognize(lang=from_lang, clear_screen=False).lower()
  else:  
    # По умолчанию - извлекаем текст из первоначальной фразы
    try:
      text = re.split('перевод|переведи', text)[-1].strip()
    except:
      text = ''
    
  if text:
    show_caption('Перевод')
    print(f'\n{ANSI_CYAN_BRIGHT}"{text}"')
    
    new_text = translate_text(f'{text}.', to_lang=to_lang, from_lang=from_lang)  
    
    if new_text:      
      print(f'[{from_lang} -> {to_lang}]\n{ANSI_CYAN_BRIGHT}"{new_text}"')
      say_by_external_engine(new_text, lang=to_lang)      
      sleep(4)
      say('Готово.')    
    
    else:
      say('Проблемы при переводе.')
  else:
    say('Не удалось распознать текст.')
  

def act_read_available_books_list(**kwargs):
  """
  Озвучить список доступных книг
  """
  show_caption('Список доступных книг')
  
  for file_name in os.listdir(os.path.join(home_dir, 'books')):
    file_name_lower = file_name.lower()

    if ( file_name_lower.endswith('.txt') \
         or file_name_lower.endswith('.fb2') \
         or file_name_lower.endswith('.pdf') \
       ):

      print(f' "{file_name}"')
      say(file_name)      
      if check_stop(listen_timeout=2, clear_screen=False): break
    
  say('Обзор завершён.')
  
  
def get_random_book_file(prefer_name=''):
  """
  Выбрать случайный файл-книгу из каталога `books`
  Возможно использовать совпадение по названию
  """
  file = ''  
  files = []
  
  for file_name in os.listdir(os.path.join(home_dir, 'books')):
    file_name_lower = file_name.lower()
    
    if ( file_name_lower.endswith('.txt') \
         or file_name_lower.endswith('.fb2') \
         or file_name_lower.endswith('.pdf') \
       ) \
       and (not prefer_name or prefer_name in file_name_lower):
      files.append(file_name)  
  
  if files:
    file = random.choice(files)
    
  return file
  

def load_text_file(file_path, encoding='utf-8'):
  """
  Загрузка содержимого из текстового файла
  """
  text = ''  
  encoding = detect_file_encoding(file_path) or encoding
  
  with open(file_path, encoding=encoding) as f:
    text = f.read()
  
  return text
  
  
def load_fb2_file(file_path):
  """
  Загрузка текста из fb2-файла
  """
  text = ''
  
  tree = ET.parse(file_path)
  root = tree.getroot()

  for child in root:
    if 'body' not in child.tag: continue
    
    for el in child.iter():
      ## if 'subtitle' in el.tag: continue
      if not ('title' in el.tag \
              or 'section' in el.tag \
              or 'emphasis' in el.tag \
              or '}p' in el.tag \
      ): continue
      
      if el.text:
        text += (el.text.replace('—', '-').strip() + ' ')

  return text
  
  
def load_pdf_file(file_path):
  """
  Загрузка текста из pdf-файла
  """
  text = ''

  with fitz.open(file_path) as pdf:
    #page_count = pdf.page_count
    #title = pdf.metadata['title']
    
    for page in pdf:
      page_text = page.get_text().replace('-\n', ' ').replace('\n', ' ') #.strip()
      if page_text:
        text += (page_text + ' ')

  return text
  
  
def read_text_by_chunks(text, from_chunk=0, use_external_engine=True, lang='ru'):
  """
  Чтение текста вслух, порциями.
  Возможно указать, с какого блока по счёту начать чтение, 
  а также каким двигом читать - внешним (по умолчанию) или внутренним.
  """    
  text = text.replace('\n', ' ').replace('—', '-')
  
  text += SENTENCE_DELIMITER
  len_text = len(text)
  
  from_chunk = (from_chunk - 1) if from_chunk > 0 else 0  
  chunk_count = from_chunk
  
  is_exit = False
  
  # Озвучивание частями, в цикле
  tail = ''
  for i in range(from_chunk * READ_CHUNK_SIZE, len_text, READ_CHUNK_SIZE):
    data = text[i : i + READ_CHUNK_SIZE]
    data = tail + data
    chunk_count += 1    
    #if not data: break ##

    goal_text = ''    
    result = data.rsplit(SENTENCE_DELIMITER, 1)
    
    # Wow-Wow, Easy!
    if len(result) == 2:
      goal_text = result[0].strip()
      tail = result[1]
    else:
      goal_text = ''
      tail = result[0]
      
    if goal_text:
      goal_text += SENTENCE_DELIMITER
      
      if use_external_engine:
        say_by_external_engine(goal_text, lang=lang)
      else:
        say(goal_text, lang=lang)
          
      # !ВНИМАНИЕ: используемый внешний проигрыватель 
      # уже позволяет поставить воспроизведение на паузу, командой с клавиатуры!

      # Остановка озвучивания, голосовой командой
      if check_stop(listen_timeout=1, clear_screen=False):
        is_exit = True
        break # Стоп

  if is_exit:
    info = f'Вы остановились на блоке номер "{chunk_count}"'
    print(info)
    say(info)
        

def read_local_book(file='', prefer_name='', encoding='utf-8', from_chunk=0, use_external_engine=True, lang='ru'):
  """
  Загрузить и прочитать книгу из локального каталога
  """
  show_caption('Чтение книги')
  
  # Если файл явно не задан - выбираем случайный файл из каталога `books`
  # Возможно использовать совпадение по названию
  if not file:
    file = get_random_book_file(prefer_name=prefer_name)
    if not prefer_name: from_chunk = 0
    
  # Искомый файл
  file_path = os.path.join(home_dir, 'books', file)
  
  if os.path.isfile(file_path):
    show_caption(f'Читаем файл "{file}", с блока {from_chunk}')
    
    book = ''
    file_path = file_path.lower()
    
    if file_path.endswith('.txt'):
      book = load_text_file(file_path, encoding=encoding)
    
    elif file_path.endswith('.fb2'):
      book = load_fb2_file(file_path)
    
    elif file_path.endswith('.pdf'):
      book = load_pdf_file(file_path)
    
    if book:
      read_text_by_chunks(book, from_chunk=from_chunk, use_external_engine=use_external_engine, lang=lang)
      
    say('Чтение завершено.')
  else:
    info = 'Файл не найден'
    print(f'{info}!')
    say(f'{info}.')
    

def act_read_local_book(**kwargs):
  """
  Action-процедура, обёртка над основной процедурой.
  Загрузить и прочитать книгу из локального каталога.
  Возможность указать книгу, номер блока, с которого начинать и т.д.
  
  Общий формат команды (параметра `text`):
  text == '`чтение книги` | `прочти книгу` [`файл` FILENAME] [`название` BOOKNAME] [`с блока` BLOCK_NUMBER] [`язык` LANGNAME]'
  """  
  text = kwargs.get('text', '')
  
  # По умолчанию - русский язык
  (text, lang_name) = extract_value_from_text(text, 'язык', '')
  
  if not lang_name:
    lang = 'ru'
  else:
    lang = get_lang_tag(lang_name)
    if not lang: lang = 'ru'
  
  # По умолчанию - с начального блока
  (text, from_chunk) = extract_value_from_text(text, 'с блока', 0)
  try:
    from_chunk = int(from_chunk.replace(' ', '').replace('.',''))
  except:
    from_chunk = 0

  (text, prefer_name) = extract_value_from_text(text, 'название', '')
  (text, file) = extract_value_from_text(text, 'файл', '')
  
  read_local_book(file=file, prefer_name=prefer_name, from_chunk=from_chunk, lang=lang)


def calculate_seconds_from_text_condition(text_condition):
  """
  Вычисление общего количества секунд из условия, заданного текстом.
  
  Формат параметра `text_condition`:
  text_condition == "[HOURS `час..`] [MINUTES `минут..`] [SECONDS `секунд..`]"
  """
  if not text_condition:
    return None
    
  text_condition = text_condition.replace('одну', '1')
  
  total_seconds = 0
  result = None
  
  # todo: re.compile
  if ':' in text_condition:
    result = re.findall(r'^(?:(\d+):(\d+))?(?:(\d+) секунд\D*)?', text_condition)
  else:
    result = re.findall(r'^\D*(?:(\d+) час\D*)?(?:(\d+) минут\D*)?(?:(\d+) секунд\D*)?$', text_condition)
  
  try:
    if result and len(result) == 1:
      hours   = result[0][0]
      minutes = result[0][1]
      seconds = result[0][2]

      if seconds: total_seconds += int(seconds)
      if minutes: total_seconds += int(minutes) * 60
      if hours:   total_seconds += int(hours) * 60 * 60

      print(f'Часов: `{hours}`, минут `{minutes}`, секунд: `{seconds}`')
  except Exception as e:
    print(e)
    total_seconds = 0
    
  return total_seconds
  

def act_make_timer(**kwargs):
  """
  Создать таймер указанной длительности.
  Возможно указание наименования таймера.
  
  Чтобы превратить таймер в интервальный, воспроизводящий сигнал через заданный интервал,
  дополнительно указывается параметр `сигнал через`.
  
  Общий формат команды (параметра `text`):  
  text == "`таймер` [`название` TIMER_NAME] `на` [HOURS `час..`] [MINUTES `минут..`] [SECONDS `секунд..`] 
           [`сигнал через` [HOURS `час..`] [MINUTES `минут..`] [SECONDS `секунд..`]]"
  """  
  text = kwargs.get('text', '')
  if not text: return
  
  # Условие - через какое время подавать сигнал (для интервального таймера)
  (text, text_condition_signal_after) = extract_value_from_text(text, 'сигнал через', '')
  
  # Условие - на какое время установить таймер
  # (должно обязательно присутствовать!)
  (text, text_condition) = extract_value_from_text(text, 'на', '')
  if not text_condition: return

  # Возможное наименование таймера
  (text, timer_name) = extract_value_from_text(text, 'название', None)  

  # Разбор условий и вычисление количества секунд, на которое установить таймер
  total_seconds = 0
  if text_condition:
    total_seconds = calculate_seconds_from_text_condition(text_condition)
    
  # Для интервального таймера - разбор условий и вычисление интервала, через который подавать сигнал
  signal_after_seconds = 0  
  if text_condition_signal_after:
    signal_after_seconds = calculate_seconds_from_text_condition(text_condition_signal_after)

  if total_seconds and total_seconds > 0 and total_seconds < 1_000_000:
    show_caption('Запуск таймера')
    
    if signal_after_seconds and signal_after_seconds > 0 and signal_after_seconds < 1_000_000:
      say('(интервального)')
      # Интервальный таймер
      make_interval_timer(seconds=total_seconds, signal_after_seconds=signal_after_seconds, name=timer_name)
    else:
      # Обычный таймер (по умолчанию)
      make_timer(seconds=total_seconds, name=timer_name)
  else:
    show_caption('Ошибка при разборе параметров.')

    
def act_make_os_alarm_clock(**kwargs):
  """
  Создать простой будильник в стандартном планировщике ОС.
  
  В текущей версии - будильник однократного запуска,
  поддерживается возможность установить `на завтра`,
  либо текущий день (по умолчанию).

  Дополнительно, в текущей версии возможно указать день (число) без наименования месяца.
  Система будет пытаться установать будильник на ближайший указанный день.

  Если не указан день и время указано более раннее, чем текущее,
  то будильник создаётся на указанное время следующего дня.
  
  Новый будильник с тем же именем - перезаписывает предыдущий.
  
  Общий формат команды (параметра `text`):
  text == "`будильник` [`название` ALARM_CLOCK_NAME] [`на` (`завтра` | DAY_OF_MONTH)] `на` [HOURS `час..`] [MINUTES `минут..`]"
  """
  text = kwargs.get('text', '')
  if not text: return  

  # Условие - на какое время установить будильник
  (text, text_condition_time) = extract_value_from_text(text, 'на', '')
  if not text_condition_time: return

  # Условие - на какой день установить будильник
  (text, text_condition_day) = extract_value_from_text(text, 'на', None)
  
  # Возможное наименование будильника
  (text, alarm_clock_name) = extract_value_from_text(text, 'название', None)  

  # Разбор условий и вычисление параметров для установки будильника
  # Вычисляем время
  hours = None
  minutes = 0  
  result = None
  
  # todo: re.compile
  if ':' in text_condition_time:
    result = re.findall(r'(\d+):(\d+)', text_condition_time)
  else:
    result = re.findall(r'^\D*(?:(\d+) час\D*)?(?:(\d+) минут\D*)?$', text_condition_time)
    
  try:
    if result and len(result) == 1:
      hours   = result[0][0]
      minutes = result[0][1]
      
      minutes = int(minutes) if minutes else 0
      hours = int(hours) if hours else None
  except Exception as e:
    print(e)
    hours = None
    minutes = 0
  
  # Вычисляем день
  # По умолчанию - `сегодня`
  day = 'today'
  
  if text_condition_day:
    if 'завтра' in text_condition_day: 
      day = 'tomorrow'
    else:
      #todo: распознавание даты, либо дня недели
      try:
        day = int(text_condition_day.strip())
      except:
        pass

  print(f'День: `{day}`, Часов: `{hours}`, минут `{minutes}`')
      
  if hours:
    show_caption('Установка будильника')
    result = make_os_alarm_clock(name=alarm_clock_name, day=day, hours=hours, minutes=minutes)

    if result:
      say('Успешно.')
    else:
      say('Ошибка при установке.')  
  
  else:
    show_caption('Ошибка при разборе параметров.')


def metronome_parameters_recognize_correction(text_parameters):
  """
  Корректировка результата распознавания параметров команды создания метронома
  (когда движок распознавания неистово бунтует)
  """
  if not text_parameters: return ''
  
  # Набор данных для исправления ошибок распознавания
  replace_data = {
    'по умолчанию': f'{conf.METRONOME_DEFAULT_BPM} ударов',
    'note': ' ноты ',
    'nod': ' нот ',
    '608': '6 нот 8',
    '0 3': ' ноты ',
    '/': ' нот ',
    'минуты': 'ноты',
    'accent': 'акцент',
    'shuffle': 'шаффл',
    'шафл': 'шаффл',
    'одна': '1',
    'целая': '1',
    'целых': '1',
    'тридцатьвторых': '32',
    'тридцать вторых': '32',
    '30 вторых': '32',
    'две': '2',
    'вторая': '2',
    'вторых': '2',
    'три': '3',
    'четыре': '4',
    'четверти': '4',
    'четвертых': '4',
    'четвёртых': '4',
    'пять': '5',
    'шесть': '6',
    'восемь': '8',
    'восьмых': '8',
    'шестнадцать': '16',
    'шестнадцатых': '16',
  }

  # Корректировка
  for key, value in replace_data.items():
    text_parameters = text_parameters.replace(key, value)
    
  return text_parameters
  

def act_make_metronome(**kwargs):
  """
  Создать метроном с указанными параметрами
  
  Общий формат команды (параметра `text`):  
  text == "`метроном` [BPM `ударов`] [ (COUNT `нот..` LENGTH) | `размер` COUNT `на` LENGTH) ] [`акцент`] [`шаффл`]"
  либо
  text == "`метроном по умолчанию`"
  
  Параметр `акцент`, означает выделение сильной доли.
  Параметр `шаффл`, означает пропуск сигнала (либо особый сигнал) на среднюю долю в триолях.
  
  По умолчанию (если не указано) значения будут следующие (настраивается в `config/config.py`):
    - 90 ударов в минуту
    - размер 4/4
    - с акцентом, с сигналом на каждую долю
    
  Возможность выхода из процедуры по голосовой команде, после определённого числа тактов.
  Особый звуковой сигнал оповещает, что есть возможность выхода по специальной голосовой команде,
  в течение пары секунд.
  
  Возможность прерывания по `Ctrl-C` с клавиатуры.
  
  В случае `по умолчанию` - берутся соответствующие параметры из конфигурационного файла.
  
  Примеры корректных команд:
    '%robot_name%, метроном 90 ударов, восемь нот восьмых, акцент'
    '%robot_name%, метроном 124 удара, размер 3 на 8, с акцентом, шаффл'
    '%robot_name%, метроном по умолчанию'
  """
  text = kwargs.get('text', '')
  if not text: return  
  
  (text, text_parameters) = extract_value_from_text(text, 'метроном', '')
  if not text_parameters: return
  
  # Корректировка результатов распознавания
  text_parameters = metronome_parameters_recognize_correction(text_parameters)
  
  parse_parameters_is_ok = False
  result = None
  
  # todo: re.compile
  result = re.findall(r'^\D*(?:(\d+) удар\S*)?\s*(?:(?:размер )?(\d+)\s+(?:нот\D*|на)\s+(\w+))?(.*)$', text_parameters)
  
  try:
    if result and len(result) == 1:
      result_bpm         = result[0][0]
      result_note_count  = result[0][1]
      result_note_length = result[0][2]
      result_additional  = result[0][3]

      #todo: возможно, поменять алгоритм, разбора, запретив использование параметров по умолчанию
      
      bpm         = int(result_bpm) if result_bpm else conf.METRONOME_DEFAULT_BPM
      note_count  = int(result_note_count) if result_note_count else conf.METRONOME_DEFAULT_NOTE_COUNT
      note_length = int(result_note_length) if result_note_length else conf.METRONOME_DEFAULT_NOTE_LENGTH
      is_accent   = True if (result_additional and 'акцент' in result_additional) else conf.METRONOME_DEFAULT_IS_ACCENT
      is_shuffle  = True if (result_additional and 'шаффл' in result_additional) else conf.METRONOME_DEFAULT_IS_SHUFFLE  
      
      parse_parameters_is_ok = True
      
  except Exception as e:
    parse_parameters_is_ok = False
    print(e)
    
  if parse_parameters_is_ok:
    show_caption('Метроном')
    
    info = f'БПМ: {bpm}. "{note_count} на {note_length}".{" Акцент." if is_accent else ""}{" Шаффл." if is_shuffle else ""}'
    print(f'{ANSI_CYAN_BRIGHT} {info}')
    say(info)
    
    # Корректировка громкости
    set_system_volume(conf.METRONOME_VOLUME)
    beep_sound(freq=1000, duration=300)
    
    # Запуск метронома
    result = make_metronome(bpm=bpm, note_count=note_count, note_length=note_length, is_accent=is_accent, is_shuffle=is_shuffle)    
    
    # Корректировка громкости
    set_system_volume(conf.SYSTEM_VOLUME_DEFAULT)
    
    if result:
      say("Готово")
    else:
      say('Ошибка запуска')
  
  else:
    show_caption('Ошибка при разборе параметров')

  
#@@
## -- end ACTIONS (действия) ------------------------------------------------------------------ ##


def init_and_parse_args():
  """
  Инициализация и разбор аргументов командной строки
  """
  argparser = ArgumentParser(description='Голосовой робот-помощник')
  argparser.add_argument('--microphones', default=False, action='store_true', help='Вывести список доступных микрофонов в системе')
  argparser.add_argument('--voices', default=False, action='store_true', help='Вывести список доступных голосовых движков в системе')
  argparser.add_argument('--clock-alarm', default=False, action='store_true', help='Проиграть звук будильника')
  argparser.add_argument('--nightmode', default=False, action='store_true', help='Ночной режим')
  args = argparser.parse_args()
  return args


def setup(config_file):
  """
  Установка базовых параметров из файла конфигурации.
  Установка параметров, переопределяющих заданные по умолчанию.
  """
  pass
  
  
def init(config_file=None):
  """
  Инициализация голосового робота-ассистента.
  Открытие баз данных, настройка двигов произношения и распознавания речи.
  """
  setup(config_file)
  
  # Загрузка карты реакций
  load_reactions_map() ##
  
  # Проверка доступности внешнего приложения для проигрывания файлов
  if not is_external_player_exists():
    print(f'\nНе найдено внешнее приложения для проигрывания файлов (подразумевается наличие плеера MPV)!\n\a')
    sys.exit(0)
  
  random.seed()
  
  init_locale()
  
  init_tts()
  
  open_databases()
  
  load_quotes()
  load_irr_verbs()  
  load_phrasal_verbs()
  
  print(ansi.clear_screen())
  
  # Корректировка громкости звука
  set_system_volume(conf.SYSTEM_VOLUME_DEFAULT)


def run(config_file=None):
  """
  Основная точка входа. 
  Инициализация. 
  Запуск цикла распознавания и обработки.
  """  
  # Инициализация
  init(config_file)
  
  ##beep()
  say(f'Привет. {conf.ROBOT_NAME} на связи.')
  
  #DEBUG    
  #print('OK')
  #sys.exit(0)
  #end DEBUG
  
  while True:    
    text = listen_and_recognize()
    if text: make_reaction(text)

  
if __name__=='__main__':
  args = init_and_parse_args()

  if args.microphones:
    print_microphones_info()

  if args.voices:
    print_voice_engines_info()
    
  if args.clock_alarm:
    play_clock_alarm()
  
  # В случае запуска без дополнительных параметров - стартует робот
  if not (args.microphones or args.voices or args.clock_alarm):
    run()
