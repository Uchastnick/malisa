import os, sys
import importlib

# -----------------------------------------------------------------------------
# Директория основного скрипта робота
home_dir = os.path.dirname(os.path.abspath(__file__))

# Трюк для одновременной работы с импортируемыми модулями
# как в локальном режиме, так и в режиме пакета
if home_dir not in sys.path: sys.path.append(home_dir)

# -----------------------------------------------------------------------------
# Базовая Конфигурация по умолчанию
config_name = 'config.ini'

if not os.path.isfile(os.path.join(home_dir, 'config', config_name)):
  raise SystemExit(f'\nНе найден основной файл конфиграции "./config/{config_name}"!\n\a')

try:
  #import config.config as conf
  #conf = importlib.import_module(f'config.config')

  from utils import load_config
  config = load_config(config_name)

except Exception as e:
  print(e)
  raise SystemExit(f'Обнаружена проблема в файле конфигурации "./config/{config_name}"!\n\a')
  
# Режим отладки и вывода служебных сообщений
DEBUG = (getattr(config.other, 'debug', 0) == 1)

# -----------------------------------------------------------------------------

# Имя робота
ROBOT_NAME = config.main.robot_name

ROBOT_NAME_LOWER = ROBOT_NAME.lower()
ROBOT_NAME_LENGTH = len(ROBOT_NAME_LOWER)

# Звуковой сигнал по готовности
BEEP_WHEN_READY = getattr(config.main, 'beep_when_ready', 0)

# -----------------------------------------------------------------------------

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

NIGHT_MODE = (getattr(config.main, 'night_mode', 0) == 1)

ANSI_CYAN_BRIGHT = Fore.CYAN + (Style.BRIGHT if not NIGHT_MODE else '')
ANSI_GREEN_BRIGHT = Fore.GREEN + (Style.BRIGHT if not NIGHT_MODE else '')
ANSI_YELLOW_BRIGHT = Fore.YELLOW + (Style.BRIGHT if not NIGHT_MODE else '')
ANSI_BLACK_ON_WHITE = Back.WHITE + Fore.BLACK
ANSI_STYLE_RESET = Style.RESET_ALL

# Использование SpeechDispatcher + RHVoice в системах Linux
using_speechd_engine = False

if os.name == 'posix' and config.engine.use_speech_dispatcher_in_linux == 1:
  try:
    # Голосовой движок для систем Linux
    import speechd
    using_speechd_engine = True
  except ImportError as e:
    using_speechd_engine = False
    print(e)
    print(f'\nНе удалось загрузить модуль Speech Dispatcher!\n\a')

if os.name == 'nt' or not using_speechd_engine:
  # Голосовой движок по умолчанию
  import pyttsx3

from gtts import gTTS

# Временный mp3-файл для работы с внешним источником генерации речи
TMP_MP3_FILE = os.path.join(home_dir, 'tmp', 'gTTS.mp3')

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

try:
  import pyautogui
  pyautogui.PAUSE = 2
  screen_size = pyautogui.size()
except:
  screen_size = [0, 0]
  
x_center, y_center = round(screen_size[0]/2), round(screen_size[1]/2)

# Использование мыши для левши
USING_LEFT_HANDED_MOUSE = (getattr(config.autoit, 'using_left_handed_mouse', 0) == 1)

from utils import (
  sleep, 
  beep, 
  run_os_command,
  detect_file_encoding,
  check_any_exact_match,
  check_any_partial_match,
  extract_value_from_text,
  play_sound,
  beep_sound
)

import yaml
from inputimeout import inputimeout, TimeoutOccurred

import webbrowser as web

import re

import fitz

from googletrans import Translator

import psutil

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

# Функции для работы с системой `умный дом`
import smarthome as smart

# Набор устройств умного дома, загружается из файла конфигурации `config/smart_devices.yaml`
smart_devices = {}

# -----------------------------------------------------------------------------

# Поиск в Википедии
import wikipedia as wiki

# Максимальное количество предложений, возвращаемых при поиске в Википедии
WIKI_SENTENCES_COUNT = getattr(config.wiki, 'wiki_sentences_count', 5)

# -----------------------------------------------------------------------------

# Скорость чтения книг (текста большого объема)
BOOKS_READING_SPEED = getattr(config.reading, 'books_reading_speed', 1.1)

# Скорость чтения 
WIKI_READING_SPEED = getattr(config.wiki, 'wiki_reading_speed', 1.2)

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

# Каталог библиотеки книг
BOOKS_DIR = os.path.join(home_dir, 'books')

books_dir_external = getattr(config.reading, 'external_library_of_books_path', '')
if books_dir_external: BOOKS_DIR = books_dir_external

if not os.path.isdir(BOOKS_DIR):
  raise SystemExit(f'Внимание! Не найден каталог с библиотекой книг ("{BOOKS_DIR}")!\n\a')

# Чтение книги порциями
# Размер блока данных
READ_CHUNK_SIZE = getattr(config.reading, 'read_chunk_size', 256)

# Разделитель предложений в тексте
SENTENCE_DELIMITER = getattr(config.reading, 'sentence_delimiter', '. ')
  
# -----------------------------------------------------------------------------

# Браузер для поиска в web
web_browser = None

# -----------------------------------------------------------------------------

# Google-переводчик
translator = None

# -----------------------------------------------------------------------------

# Распознавание речи оффлайн (на локальном хосте)

# Локальное распознавание ключевых фраз
# Даже если основное распознавание происходит через интернет, предварительно будет локально проверяться - адресована ли фраза роботу
SR_LOCAL_FOR_KEYPHRASE = (getattr(config.engine, 'speech_recognition_local_for_keyphrase', 0) == 1)

# Использование Vosk Engine для локального распознавания
SR_LOCAL_VIA_VOSK = (getattr(config.engine, 'speech_recognition_local_via_vosk', 0) == 1)

vosk_reco_ru = None
vosk_reco_en = None
vosk_reco_de = None

VOSK_FRAME_RATE = 16000

if SR_LOCAL_VIA_VOSK or SR_LOCAL_FOR_KEYPHRASE:
  import vosk

# -----------------------------------------------------------------------------

tts = None
reco = None
ru_voice_id = ''
en_voice_id = ''
de_voice_id = ''
current_tts_lang = ''

# Распознавание речи через интернет, посредством Google (используется по умолчанию)
SR_REMOTE_VIA_GOOGLE = (getattr(config.engine, 'speech_recognition_remote_via_google', 1) == 1)

# -----------------------------------------------------------------------------

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
  if os.name == 'nt':
    locale.setlocale(locale.LC_ALL, 'Russian') # for OS Windows
  elif os.name == 'posix':
    locale.setlocale(locale.LC_ALL, 'ru_RU.utf8') # for Linux
  else:
    locale.setlocale(locale.LC_ALL, '') # from environment
  

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
    

def close_all():
  """
  Закрытие системных ресурсов (используется при выходе)
  """
  global tts
  
  if tts:
    if using_speechd_engine: tts.close()
  
  if os.path.exists(TMP_MP3_FILE): os.remove(TMP_MP3_FILE)
  
  close_databases()
  
  
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
  
  
def load_smart_devices():
  """
  Загрузка списка умных устройств из конфигурационного файла
  """
  global smart_devices
  smart_devices = smart.load_smart_devices_info()
    

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
      play_sound(frequency=800, duration=500)
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
      [config.app.mpv_app_path,
       '--quiet', '--really-quiet', '--no-video',
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
  
  if os.name == 'nt':
    script_name = 'clock_alarm.bat'
  else:
    script_name = 'clock_alarm.sh'
    
  run_script = os.path.join(home_dir, 'script', script_name)

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
  bpm         = kwargs.get('bpm', config.metronome.metronome_default_bpm)
  note_count  = kwargs.get('note_count', config.metronome.metronome_default_note_count)
  note_length = kwargs.get('note_length', config.metronome.metronome_default_note_length)
  is_accent   = kwargs.get('is_accent', config.metronome.metronome_default_is_accent)
  is_shuffle  = kwargs.get('is_shuffle', config.metronome.metronome_default_is_shuffle)
  
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
  
  freq_base    = config.metronome.metronome_freq_base
  freq_accent  = config.metronome.metronome_freq_accent
  freq_shuffle = config.metronome.metronome_freq_shuffle
  
  silence_in_shuffle = config.metronome.metronome_use_silence_in_shuffle
  
  # Возможен выход по `Ctrl-C` с клавиатуры
  try:
    beats = 0    
    
    while True:      
      for i in range(1, note_count + 1):
        if is_accent and i == 1:
          play_sound(frequency=freq_accent, duration=play_time)
        
        elif is_shuffle and i in [2, 5, 8, 11]:
          if silence_in_shuffle:
            time.sleep(tick_length)
          else:
            play_sound(frequency=freq_shuffle, duration=play_time)
        
        else:
          play_sound(frequency=freq_base, duration=play_time)
          
        time.sleep(delay)
      
      # Возможен выход по голосовой команде после заданного числа тактов
      beats += 1      
      if (beats % config.metronome.metronome_beats_count_before_exit) == 0:
        play_sound(frequency=1000, duration=300)
        if check_stop(listen_timeout=2, clear_screen=False): break
        play_sound(frequency=1000, duration=300)

  except KeyboardInterrupt:
    play_sound(frequency=1000, duration=300)
    return True
        
  return True


def print_microphones_info():
  """
  Вывести список доступных микрофонов в системе
  """
  microphones = sr.Microphone.list_microphone_names()

  print(ansi.clear_screen())
  print('\n-- Список устройств в системе: --\n')  
  
  for index, name in enumerate(microphones):
      if os.name == 'nt':
        try:
          name = name.encode('cp1251').decode('utf-8')
        except:
          pass
      print(f"{index}: '{name}'")
  print()


def print_voice_engines_info():
  """
  Вывести список доступных голосовых движков в системе
  """
  print('\n-- Список голосовых движков в системе: --\n')
  
  if not tts:
    init_tts()

  if tts:
    voices = get_system_voices()
    for voice in voices:
      print(f"{voice['index']}: '{voice['name']}', '{voice['id']}', '{voice['lang']}', '{voice['dialect']}'")
    print()
    if using_speechd_engine: tts.close()

      
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
  

def get_system_voices():
  """
  Получение списка установленных голосов в системе
  """
  voice_list = []
  
  if tts:
    if using_speechd_engine:
      # Используем голосовой движок посредством SpeechDispatcher
      voices = tts.list_synthesis_voices()
      for index, voice in enumerate(voices):
        (name, lang, dialect) = voice

        voice_item = {}
        voice_item['index'] = index
        voice_item['name']  = name
        voice_item['id']    = name ##
        voice_item['lang']  = lang
        voice_item['dialect'] = dialect
        voice_item['languages'] = ''
        voice_list.append(voice_item)
    
    else:
      # По умолчанию используем голосовой движок посредством PyTTSX3
      voices = tts.getProperty('voices')
      for index, voice in enumerate(voices):

        voice_item = {}
        voice_item['index'] = index
        voice_item['name']  = voice.name
        voice_item['id']    = voice.id
        voice_item['lang']  = ''
        voice_item['dialect'] = ''
        voice_item['languages'] = str(voice.languages)      
        voice_list.append(voice_item)
        
  return voice_list
  
  
def set_voice_language(lang):
  """
  Установка языка голосового движка
  Параметры: lang = ('ru' | 'en' | 'de')
  """
  global current_tts_lang
  
  if lang and lang != current_tts_lang:
    current_tts_lang = lang
    
    voice, rate = None, None

    if lang == 'ru':
      voice = ru_voice_id
      rate = config.engine.speech_rate_ru
    elif lang == 'en': 
      voice = en_voice_id
      rate = config.engine.speech_rate_en
    elif lang == 'de': 
      voice = de_voice_id
      rate = config.engine.speech_rate_de
      
    if tts and voice and rate:
    
      if using_speechd_engine:
        # Используем голосовой движок посредством SpeechDispatcher
        tts.set_language(current_tts_lang)
        tts.set_synthesis_voice(voice)
        #todo
        #tts.set_rate(rate)
      else:
        # По умолчанию используем голосовой движок посредством PyTTSX3
        tts.setProperty('voice', voice)
        tts.setProperty('rate', rate)

  
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

  if tts:
    return tts

  # Начальная инициализация
  if using_speechd_engine:
    # Используем голосовой движок посредством SpeechDispatcher
    tts = speechd.SSIPClient('malisa')
    tts.set_output_module('rhvoice')    
    tts.set_volume(int(config.engine.speech_volume) * 100)
    tts.set_punctuation(speechd.PunctuationMode.SOME)
  
  else:
    # По умолчанию используем голосовой движок посредством PyTTSX3
    tts = pyttsx3.init()
    tts.setProperty('volume', config.engine.speech_volume)
    
  # Поиск голосов для озвучивания
  voices = get_system_voices()
  
  for voice in voices:
    voice_name = voice['name']
    voice_id = voice['id']
    
    # Английский
    if not en_voice_id:
      if config.engine.speech_engine_en_name:
        if voice_name == config.engine.speech_engine_en_name:
          en_voice_id = voice_id
      else:
        if 'Microsoft Anna' in voice_name:
          en_voice_id = voice_id
    
    # Русский
    if not ru_voice_id:
      if config.engine.speech_engine_ru_name:
        if voice_name == config.engine.speech_engine_ru_name:
          ru_voice_id = voice_id
    
    # Немецкий
    if not de_voice_id:
      if config.engine.speech_engine_de_name:
        if voice_name == config.engine.speech_engine_de_name:
          de_voice_id = voice_id
          
  # По возможности, первоначально устанавливается русский язык произношения
  # Если ничего не найдено - язык по умолчанию
  if ru_voice_id:
    set_voice_language(lang='ru')
    
  elif en_voice_id:
    set_voice_language(lang='en')  
  
  elif de_voice_id:
    set_voice_language(lang='de')
  
  else:
    en_voice_id = 'default'
    set_voice_language(lang='en')
    
  return tts


def init_speech_recognizer():
  """
  Инициализация движка распознавания речи по умолчанию
  """
  global reco

  if reco:
    return reco
  
  reco = sr.Recognizer()
  return reco
  

def init_vosk_engine():
  """
  Инициализация движка локального распознавания речи - Vosk Engine
  """
  vosk.SetLogLevel(-1)

  global vosk_reco_ru
  global vosk_reco_en
  global vosk_reco_de

  vosk_model_ru = None
  vosk_model_en = None
  vosk_model_de = None

  vosk_model_ru_path = os.path.join(home_dir, 'data', 'vosk-model-small-ru')
  vosk_model_en_path = os.path.join(home_dir, 'data', 'vosk-model-small-en')
  vosk_model_de_path = os.path.join(home_dir, 'data', 'vosk-model-small-de')

  if not os.path.exists(vosk_model_ru_path):
    raise SystemExit(f'\nНе найдена модель Vosk для локального распознавания русского языка ("{vosk_model_ru_path}")!\n\a')

  if not vosk_reco_ru:
    try:
      vosk_model_ru = vosk.Model(vosk_model_ru_path)
      vosk_reco_ru = vosk.KaldiRecognizer(vosk_model_ru, VOSK_FRAME_RATE)
      vosk_reco_ru.SetWords(True)
    except Exception as e:
      print(e)
      raise SystemExit('Ошибка при инициализации механизма локального распознавания Vosk для русского языка!\n\a')
  
  if os.path.exists(vosk_model_en_path): 
    if not vosk_reco_en:
      try:
        vosk_model_en = vosk.Model(vosk_model_en_path)
        vosk_reco_en = vosk.KaldiRecognizer(vosk_model_en, VOSK_FRAME_RATE)
        vosk_reco_en.SetWords(True)  
      except Exception as e:
        print(e)
        print('Ошибка при инициализации механизма локального распознавания Vosk для английского языка!\n')
  
  if os.path.exists(vosk_model_de_path): 
    if not vosk_reco_de:
      try:
        vosk_model_de = vosk.Model(vosk_model_de_path)
        vosk_reco_de = vosk.KaldiRecognizer(vosk_model_de, VOSK_FRAME_RATE)
        vosk_reco_de.SetWords(True)
      except Exception as e:
        print(e)
        print('Ошибка при инициализации механизма локального распознавания Vosk для немецкого языка!\n')


def init_translator():
  """
  Инициализация переводчика (Google-переводчик)
  """
  global translator
  translator = Translator()
  return translator
  

def init_web_browser():
  """
  Инициализация web-браузера для поиска в web
  """
  global web_browser
  
  try:
    if config.web.web_browser_app:
      web.register('web_browser', None, web.BackgroundBrowser(config.web.web_browser_app))
      web_browser = web.get('web_browser')
    else:
      web_browser = web.get(None)

  except Exception as e:
    print(e)
    web_browser = None
  
  return web_browser


def say(text, lang='ru', speed=1.0):
  """
  Произнести фразу.
  По умолчанию - на русском языке. При необходимости - возможно сменить язык.
  """  
  if tts:
    # Установка языка голосового движка
    set_voice_language(lang=lang)
  
    if using_speechd_engine:
      # Используем голосовой движок посредством SpeechDispatcher      
      # Обеспечиваем синхронное выполнение озвучивания текста
      is_speaking = True
      
      def stop_speaking(cb_type):
        nonlocal is_speaking
        #sleep(1)
        is_speaking = False

      tts.speak(text, 
                callback = stop_speaking,
                event_types = (speechd.CallbackType.PAUSE, 
                               speechd.CallbackType.CANCEL,
                               speechd.CallbackType.END))
      while is_speaking:
        pass
    
    else:
      # По умолчанию используем голосовой движок посредством PyTTSX3
      tts.say(text)
      tts.runAndWait()


def is_external_player_exists():
  """
  Проверка доступности внешнего приложения для проигрывания файлов
  """
  result = run_os_command([config.app.mpv_app_path, '--help', '--really-quiet'], sync=True, hide=True)
  return result
  

def say_by_external_engine(text, lang='ru', quiet=True, hide_external=True, speed=1.0):
  """
  Озвучить текст другим способом, через внешние сервисы/программы.
  Добавлена возможность работать в `тихом` (скрытом) режиме.
  Добавлена возможность скрывать окно внешнего приложения.
  """
  if not quiet:
    info = 'Обработка внешним источником. Ожидайте...' 
    print(info)
    say(info)
  
  try:
    external_tts = gTTS(text, lang=lang)
    external_tts.save(TMP_MP3_FILE)
    tts_result = True
    
  except Exception as e:
    tts_result = False
    print(f'Error when reading text: "{text}"')
    print(f'ERROR! {e}')
  
  if tts_result:
    result = run_os_command(
      [config.app.mpv_app_path,
       '--quiet', '--really-quiet', '--no-video', f'--speed={speed}',
       TMP_MP3_FILE],
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
    

def listen_and_recognize(listen_timeout=None, lang='ru', clear_screen=True, ambient_duration=config.mic.ambient_duration, beep_when_ready=False):
    """
    Прослушивании и распознавание речи
    (основная процедура, один шаг цикла)
    По умолчанию - на русском языке. При необходимости - возможно сменить язык.
    """    
    text = ''
    
    with sr.Microphone(device_index = config.mic.microphone_index) as source:
      # Очистка экрана
      if clear_screen: print(ansi.clear_screen())
      
      # Настройка обработки посторонних шумов
      reco.adjust_for_ambient_noise(source, duration = ambient_duration)
      
      if clear_screen: print('Слушаю...')
      
      if BEEP_WHEN_READY or beep_when_ready: play_sound(frequency=500, duration=400) ##
      
      try:
        audio = reco.listen(source, timeout = listen_timeout)
      except sr.WaitTimeoutError:
        audio = None
        text  = ''
    
    if audio:
      #if clear_screen: print('Услышала.')
      
      # Определяем язык распознавания.
      # По умолчанию:
      reco_language = 'ru-RU'
      
      reco_language = get_lang_and_country_code_by_tag(lang_tag = lang)
      if not reco_language: reco_language = 'ru-RU'
      
      if clear_screen: print('Распознавание...')
      is_ok = True
      
      # Локальное распознавание посредством Vosk Engine
      # Также Vosk Engine используется при локальном контроле ключевых фраз (!)
      # В текущей версии - только для русского языка (!)
      if (SR_LOCAL_VIA_VOSK or SR_LOCAL_FOR_KEYPHRASE) and lang == 'ru':
        try:
          text = recognize_vosk(audio, language = reco_language)
          #print(f'[VOSK] Вы сказали: {text}')
          #sleep(2)
        except Exception as e:
          if clear_screen:
            print(e)
            print('Ошибка распознавания (Vosk Engine, local)!')
          text = ''
          is_ok = False
        
      # Локальный контроль ключевых фраз
      # Даже если основное распознавание происходит через интернет, 
      # предварительно будет локально проверяться - адресована ли фраза роботу (!)
      # В текущей версии - только для русского языка (!)
      if text and SR_LOCAL_FOR_KEYPHRASE and lang == 'ru':
        is_ok = is_keyphrase(text, language = lang)
      
      if is_ok:
        # Дальнейшее распознавание
        
        # Локальное распознавание посредством Vosk Engine (уже было проделано ранее)
        if SR_LOCAL_VIA_VOSK:
          pass
        
        # Распознавание речи через интернет, посредством Google (используется по умолчанию)
        #elif SR_REMOTE_VIA_GOOGLE:
        else:
          try:
            text = reco.recognize_google(audio, language = reco_language)
            #print(f'[Google] Вы сказали: {text}')
            #sleep(2)
          except Exception as e:
            if clear_screen:
              print(e)
              print('Ошибка распознавания (Google, remote)!')
            text = ''
            is_ok = False
    
    act_checking_time_to_sleep() ##!!
    return text
    

def is_keyphrase(text, language='ru'):
  """
  Контроль - является ли заданный текст ключевой фразой (командой), предназначенной роботу
  """
  if not text: return False
  if not text.lower().startswith(ROBOT_NAME_LOWER): return False
  return True


def recognize_vosk(audio, language='ru-RU'):
  """
  Локальное распознавание посредством библиотеки Vosk
  """
  result = ''
  
  # По умолчанию
  vosk_reco = vosk_reco_ru
  
  if language == 'en-EN':
    vosk_reco = vosk_reco_en
  elif language == 'de-DE':
    vosk_reco = vosk_reco_de
    
  if vosk_reco:
    #audio_data = audio.get_wav_data(convert_rate=VOSK_FRAME_RATE, convert_width=2)
    audio_data = audio.get_raw_data(convert_rate=VOSK_FRAME_RATE, convert_width=2)
    
    # Распознавание порциями
    CHUNK_SIZE = 16000
    i = 0

    while True:
      data = audio_data[i : i + CHUNK_SIZE]
      if len(data) == 0:
        break

      if vosk_reco.AcceptWaveform(data):
        res_json = json.loads(vosk_reco.Result())
        text = res_json['text']
        
        if text != '':
          result += f"{text} "
          
      i += CHUNK_SIZE

    res_json = json.loads(vosk_reco.FinalResult())
    result += f" {res_json['text']}"
    
    # # Распознавание целиком за один проход
    # if vosk_reco.AcceptWaveform(audio_data):
      # res_json = json.loads(vosk_reco.Result())
      # text = res_json['text']
      # print(f' 1: {text}')
      # if text != '': 
        # result = text

      # res_json = json.loads(vosk_reco.FinalResult())
      # text = res_json['text']
      # print(f' 2: {text}')
      # if text != '': 
        # result += f" {text}"

  return result.strip()


def is_stop_word(text):
  """
  Проверка наличя стоп-слова в тексте
  """
  if 'стоп' in text or 'хватит' in text \
      or 'окей' in text or "о'кей" in text \
      or 'нет' == text \
      or 'спасибо' in text:
    return True
  else:
    return False


def check_stop(listen_timeout=3, clear_screen=True, silently=True):
  """
  Проверка возможности выхода в циклах
  """
  if not silently: say('Продолжаю?')

  text = listen_and_recognize(listen_timeout=listen_timeout, clear_screen=clear_screen).lower()
  
  if is_stop_word(text):
    say('Окей')
    return True
    
  # Контроль возможной постановки на паузу и перехода в режим распознавания основных команд
  check_for_pause_and_make_shell(text) ##
    
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
  
  robot_name = ROBOT_NAME_LOWER
  robot_name_length = ROBOT_NAME_LENGTH
    
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

## @@
## -- ACTIONS (действия) ---------------------------------------------------------------------- ##
def act_i_am_ready(**kwargs):
  """
  Подтверждение готовности
  """
  answer = random.choice(robot_answers)
  say(answer)    

  text = listen_and_recognize()
  if text: 
    if not text.lower().startswith(ROBOT_NAME_LOWER):
      text = f'{ROBOT_NAME} {text}'
    make_reaction(text)


def act_exit(**kwargs):
  """
  Закрытие программы-робота
  """  
  say('Пока!')
  
  close_all()
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
    
  url = (f'https://api.openweathermap.org/data/2.5/weather?q={config.weather.weather_city}'
         f'&lang=ru&units=metric&APPID={config.weather.weather_api}')
  
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

  url = (f'https://api.openweathermap.org/data/2.5/onecall?lat={config.weather.weather_place_lat}&lon={config.weather.weather_place_lon}'
         f'&exclude=minutely,hourly&lang=ru&units=metric&APPID={config.weather.weather_api}')
  
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
    text_new = listen_and_recognize(clear_screen=False, beep_when_ready=True)

    if not text_new or len(text_new) == 0:
      continue

    text_new_lower = text_new.lower()

    if 'конец записи' in text_new_lower \
       or 'запись завершена' in text_new_lower:
      break
    else:
      print(f'{text_new}')
      text += f'{text_new}\n'
      time.sleep(0.4)
      play_sound(frequency=400, duration=400)
  
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
  say('Счастливо!')
  
  close_all()
  run_os_command(['shutdown', '/s', '/t', '15'])
  

def act_pc_restart(**kwargs):
  """
  Перезагрузка компьютера
  """
  show_caption('Перезагрузка')
  say('Перезагрузка!')

  close_all()  
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
  
  cmd = [config.app.openvpn_gui_app,
         '--show_balloon', '0', 
         '--silent_connection', '1',
         '--show_script_window', '0',
         '--config_dir', config.app.openvpn_config_dir,
         '--command', 'connect', config.app.openvpn_config_file]
  run_os_command(cmd)
  
  sleep(10)
  say('Готово')


def act_vpn_disconnect(**kwargs):
  """
  Закрыть соединение VPN
  """
  show_caption('Закрываю VPN')
  
  cmd = [config.app.openvpn_gui_app, 
         '--command', 'disconnect_all']
  run_os_command(cmd)
  
  sleep(5)
  say('Готово')


def act_mstsc_connect(**kwargs):
  """
  Открыть окно RDP
  """
  show_caption('Открываю RDP')
  
  cmd = ['mstsc', f"{os.path.join(home_dir, 'rdp', config.app.rdp_config_file)}"]
  run_os_command(cmd)
  
  sleep(5)
  say('Готово')


def act_rocket_chat_gui_connect(**kwargs):
  """
  Открыть окно Rocket.Chat
  """
  show_caption('Открываю Рокет Чат')
  
  cmd = [config.app.rocket_chat_app]
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
      wnds = pyautogui.getWindowsWithTitle(config.autoit.rocket_chat_title)
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
    
    mouse_button = 'left'
    if USING_LEFT_HANDED_MOUSE: mouse_button = 'right'
    
    pyautogui.click(x = config.autoit.rocket_chat_x_hack, y = config.autoit.rocket_chat_y_hack, button = mouse_button) # hack
    
    pyautogui.write(config.rocket.rocket_chat_login, interval = config.autoit.gui_write_interval)
    pyautogui.press('tab')
    pyautogui.write(config.rocket.rocket_chat_pwd, interval = config.autoit.gui_write_interval)
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
  result = rocket.rocket_chat_send_message(config.rocket.rocket_chat_message_bye, to_channel=config.rocket.rocket_chat_channel_hello)
  
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
  set_vol_app = config.app.set_volume_app
  if not set_vol_app:
    return

  if os.name == 'nt' \
     or (os.name == 'posix' and not set_vol_app.lower().endswith('.exe')):
    run_os_command([set_vol_app, f'{value}'], sync=True)
  

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
  app_name = os.path.basename(config.app.openvpn_gui_app)
  is_app_running = check_is_app_running(app_name)
  
  if is_app_running:
    # Дополнительная проверка лога соединения
    try:
      with open(config.app.openvpn_log_file) as f:
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
  app_name = os.path.basename(config.app.rocket_chat_app)
  is_app_running = check_is_app_running(app_name)
  
  if is_app_running:
    # Дополнительно пытаемся найти окно приложения
    wnd = None
    try_count = 0
    
    # Ожидаем появление окна
    while True:
      sleep(2)      
      wnds = pyautogui.getWindowsWithTitle(config.autoit.rocket_chat_title)
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
  is_send_hello = kwargs.get('send_hello', config.rocket.rocket_chat_is_send_hello)
  
  if is_send_hello:  
    act_rocket_chat_send_hello()
    sleep(3)
    print('Rocket Chat Send "Hello!"')
  
  # Корректировка громкости звука
  set_system_volume(config.engine.system_volume_default)

  say('Работайте.')

  
def act_checking_time_to_sleep(**kwargs):
  """
  Проверка необходимости идти спать
  """
  disable_sleep_time_checking = getattr(config.sleep, 'disable_sleep_time_checking', 0)
  if disable_sleep_time_checking == 1: return
  
  now = datetime.now()
  time_to_sleep = now.replace(hour = (config.sleep.time_to_sleep_hour or 23), minute = (config.sleep.time_to_sleep_minute or 40))
  
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
    
    player = radio.get_player()
    if not player:
      beep()
      return
      
    else:
      if not radio.is_playing():
        beep()
        return      
      
      else:
        # Возможность остановки плеера, голосовой командой с именем робота
        text = listen_and_recognize(listen_timeout=2, clear_screen=False).lower()
        if ROBOT_NAME_LOWER in text:
          radio.radio_pause()
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
  
  player = radio.run_player_aimp()
  
  if not player:
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
    play_object = os.path.join(home_dir, 'playlist', config.radio.playlist_default)

  radio.add_to_playlist_and_play(play_object)
  radio.set_volume(85)
  
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
  radio.radio_pause()


def act_radio_play(**kwargs):
  """
  Запуск проигрывания музыки после паузы
  """
  if not radio.is_playing():
    radio.radio_play()
    sleep(2)
    wait_while_music_playing() ##


def act_radio_stop(**kwargs):
  """
  Остановка проигрывания музыки
  """
  radio.radio_stop()


def act_realty_info(**kwargs):
  """
  Общая информация о ценах на недвижимость
  """
  show_caption('Статистика по недвижимости')
  
  for place in (config.realty.realty_cities + config.realty.realty_regions):
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
  Поиск указанного текста в сети Интернет
  
  Общий формат команды (параметра `text`):
    text == "(`поиск` | `найди` | `поищи` | `в сети` | `в интернете` | `в интернет`) GOALTEXT"

  Результат поиска должен отобразиться в интернет-браузере, 
  который можно указать в файле конфигурации, либо использовать браузер по умолчанию.
  Также возможно сменить систему поиска (по умолчанию используется Яндекс).
  """
  text = kwargs.get('text', '')
  if not text: return
  
  show_caption('Поиск в сети')
  
  keywords = 'поиск|найди|поищи|сети|интернете|интернет '

  try:
    search_string = re.split(keywords, text)[-1].strip()
  except:
    search_string = ''
  
  if web_browser and search_string:
    web_browser.open(f'{config.web.web_search_engine_default}{search_string}', new=2)  
    say('Сделано.')
  else:
    say('Ошибка.')
  

def translate_text(text, to_lang='ru', from_lang='auto'):
  """
  Перевод текста на указанный язык (используется Google-переводчик)
  """
  if not translator: return ''
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
  "(`перевод` | `переведи`) GOALTEXT [`на` TOLANG] [(`с` |'с языка') FROMLANG] [`на` TOLANG]"
  
  Если язык требуемого для перевода текста отличается от русского,
  его можно будет произнести отдельно, по запросу системы.
  """
  text = kwargs.get('text', '')
  if not text: return
  
  to_lang_name = None
  
  # Обеспечим дополнительную гибкость - возможность сказать: "... [(`с` |'с языка') FROMLANG] [`на` TOLANG]"
  find_from_lang_idx = text.find('с ')
  find_to_lang_idx = text.find('на ')
  
  if find_from_lang_idx != -1 \
     and find_to_lang_idx != -1 \
     and (find_to_lang_idx > find_from_lang_idx):
    # На какой язык (указано в конце команды)
    (text, to_lang_name) = extract_value_from_text(text, 'на', '')
  
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
  if not to_lang_name:
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
  # По умолчанию - извлекаем текст из первоначальной фразы
  try:
    text = re.split('перевод|переведи', text)[-1].strip()
  except:
    text = ''

  # Фишка! При необходимости - отдельное распознавание текста с учётом языка, с которого переводим
  # Кроме того, запросим текст явно, если изначально он не был указан
  if (not text) or (from_lang not in ['auto', 'ru']):
    say('Говорите.')
    text = listen_and_recognize(lang=from_lang, clear_screen=False, beep_when_ready=True).lower()
    
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
  if not os.path.isdir(BOOKS_DIR):
    say('Внимание! Не найден каталог с библиотекой книг!')
    return
  
  show_caption('Список доступных книг')
  
  for file_name in os.listdir(BOOKS_DIR):
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
  Выбрать случайный файл-книгу из каталога BOOKS_DIR
  Возможно использовать совпадение по названию
  """
  if not os.path.isdir(BOOKS_DIR):
    say('Внимание! Не найден каталог с библиотекой книг!')
    return
  
  file = ''  
  files = []
  
  for file_name in os.listdir(BOOKS_DIR):
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
        el_text = el.text.replace('—', '-').replace('***', '') #.replace('…', '.') #.replace(' ', ' ')
        text += (el_text.strip() + ' ')

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
  
  #for i in range(from_chunk * READ_CHUNK_SIZE, len_text, READ_CHUNK_SIZE):
  i = from_chunk * READ_CHUNK_SIZE
  while i < len_text:
  
    data = text[i : i + READ_CHUNK_SIZE]
    data = tail + data
    chunk_count += 1    
    jump_blocks = 1
    
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
        say_by_external_engine(goal_text, lang=lang, speed=BOOKS_READING_SPEED)
      else:
        say(goal_text, lang=lang, speed=BOOKS_READING_SPEED)
          
      # !ВНИМАНИЕ: используемый внешний проигрыватель 
      # уже позволяет поставить воспроизведение на паузу, командой с клавиатуры!

      # Контроль голосовых команд в процессе озвучивания книги
      control_text = listen_and_recognize(listen_timeout=1, clear_screen=False).lower()

      # Возможное прерывание озвучивания, голосовой командой
      if is_stop_word(control_text):
        say('Окей')
        is_exit = True
        break # Стоп
        
      # Контроль возможной постановки на паузу и перехода в режим распознавания основных команд
      check_for_pause_and_make_shell(control_text) ##
      
      # Контроль перехода вперёд/назад на заданное количество блоков
      jump_blocks = check_for_jump(control_text)
      if jump_blocks != 0:
        tail = ''
        say(f'Переход, количество блоков: {jump_blocks}')
      else:
        jump_blocks = 1      
        
    i += (READ_CHUNK_SIZE * jump_blocks)
    if i < 0: i = 0

  if is_exit:
    real_chunk_count = int(i / READ_CHUNK_SIZE)
    info = f'Вы остановились на блоке номер "{real_chunk_count}"'
    print(info)
    say(info)
    
    
def check_for_jump(text):
  """
  Проверка перехода вперёд/назад по тексту на заданное количество блоков.
  Возвращает количество блоков со знаком. Знак минус означает движение назад, иначе - вперёд.
  Возвращает 0, если переход не требуется.
  """
  jump_blocks = 0

  if 'вперёд' in text \
     or 'вперед' in text \
     or 'назад' in text \
     or 'переход' in text \
     or 'перейти' in text:
  
    sign = +1
    if 'назад' in text: sign = -1
    
    blocks = 0
    
    (text, blocks_text) = extract_value_from_text(text, 'на', '')
    try:
      blocks = int(re.findall(r'^(\d+) блок\D*?$', blocks_text)[0])
    except:
      blocks = 0
      
    jump_blocks = sign * blocks
    
  return jump_blocks


def check_for_pause_and_make_shell(text):
  """
  Контроль возможной постановки на паузу и перехода в режим распознавания основных команд.
  Очень полезная процедура.
  """
  if 'пауза' in text:
    say('Пауза')
    
    while True:
      text = listen_and_recognize()
      text_lower = text.lower()
      
      if 'дальше' in text_lower \
         or 'продолжаем' in text_lower \
         or 'продолжить' in text_lower:
        say('Продолжаем...')
        break;
      else:
        make_reaction(text)


def read_local_book(file='', prefer_name='', encoding='utf-8', from_chunk=0, use_external_engine=True, lang='ru'):
  """
  Загрузить и прочитать книгу из локального каталога
  """
  if not os.path.isdir(BOOKS_DIR):
    say('Внимание! Не найден каталог с библиотекой книг!')
    return
  
  show_caption('Чтение книги')
  
  # Если файл явно не задан - выбираем случайный файл из каталога BOOKS_DIR
  # Возможно использовать совпадение по названию
  if not file:
    file = get_random_book_file(prefer_name=prefer_name)
    if not prefer_name: from_chunk = 0

  # Искомый файл
  file_path = os.path.join(BOOKS_DIR, file)

  if os.path.isfile(file_path):
    show_caption(f'Читаем файл "{file}", с блока {from_chunk}')
    
    book = ''
    file_path_lower = file_path.lower()
    
    if file_path_lower.endswith('.txt'):
      book = load_text_file(file_path, encoding=encoding)
    
    elif file_path_lower.endswith('.fb2'):
      book = load_fb2_file(file_path)
    
    elif file_path_lower.endswith('.pdf'):
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
    'по умолчанию': f'{config.metronome.metronome_default_bpm} ударов',
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
  
  По умолчанию (если не указано) значения будут следующие (настраивается в `config/config.ini`):
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
      
      bpm         = int(result_bpm) if result_bpm else config.metronome.metronome_default_bpm
      note_count  = int(result_note_count) if result_note_count else config.metronome.metronome_default_note_count
      note_length = int(result_note_length) if result_note_length else config.metronome.metronome_default_note_length
      is_accent   = True if (result_additional and 'акцент' in result_additional) else config.metronome.metronome_default_is_accent
      is_shuffle  = True if (result_additional and 'шаффл' in result_additional) else config.metronome.metronome_default_is_shuffle  
      
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
    set_system_volume(config.metronome.metronome_volume)
    beep_sound(freq=1000, duration=300)
    
    # Запуск метронома
    result = make_metronome(bpm=bpm, note_count=note_count, note_length=note_length, is_accent=is_accent, is_shuffle=is_shuffle)    
    
    # Корректировка громкости
    set_system_volume(config.engine.system_volume_default)
    
    if result:
      say("Готово")
    else:
      say('Ошибка запуска')
  
  else:
    show_caption('Ошибка при разборе параметров')


def wiki_search(text, lang='ru'):
  """
  Поиск указанного текста в Википедии
  """
  result_text = None

  try:
    wiki.set_lang(lang)
    result_text = wiki.summary(text, sentences = WIKI_SENTENCES_COUNT)
    result_text = result_text.replace('\n', ' ').replace('==', '.')
  except:
    result_text = None

  return result_text
  

def act_wiki_search(**kwargs):
  """
  Поиск указанноого текста в Википедии

  Общий формат команды (параметра `text`):
    text == "(`вики` | `википедия` | `поиск в википедии` | `найди в википедии` | `посмотри википедию`) GOALTEXT [`язык` LANGNAME]"

  Результат поиска отображается в консоли и озвучивается роботом.
  Возможно указать язык поиска. Также в файле конфигурации настраивается количество показываемых предложений.
  """
  text = kwargs.get('text', '')
  if not text: return
  
  use_external_engine = getattr(config.wiki, 'wiki_use_external_speech_engine', True)
  
  show_caption('Поиск в Википедии')

  # По умолчанию - русский язык
  (text, lang_name) = extract_value_from_text(text, 'язык', '')
  
  if not lang_name:
    lang = 'ru'
  else:
    lang = get_lang_tag(lang_name)
    if not lang: lang = 'ru'
    
  # Отделяем ключевые слова от искомого текста
  keywords = 'вики |википедии|википедия|википедию'
  try:
    search_string = re.split(keywords, text)[-1].strip()
  except:
    search_string = ''
    
  if search_string:
    # Поиск
    result_text = wiki_search(search_string, lang=lang)
    
    if result_text:    
      print(f'\n {result_text}\n')

      # Чтение
      # todo: возможно, задействовать механизм чтения книг `read_text_by_chunks`
      if use_external_engine:
        say('Ожидайте.')
        say_by_external_engine(result_text, lang=lang, speed=WIKI_READING_SPEED)
      else:
        say(result_text, lang=lang, speed=WIKI_READING_SPEED)
      
      say('Готово.')
    else:
      say('Ничего не найдено!')
      
  else:
    say('Не определён текст для поиска.')
  

def check_smart_bulbs():
  """
  Проверка наличия загруженной информации об умных лампах и устройствах освещения
  """
  if not smart_devices or not smart_devices['bulbs']:
    info = 'Устройства не найдены.'
    print(info)
    say(info)
    return False

  if not smart_devices['default_bulb']:
    info = 'Отсутствует лампа по умолчанию.'
    print(info)
    say(info)
    return False

  return True
  
  
def act_light_on(**kwargs):
  """
  Включение света
  
  В текущей версии релизована поддержка только основной лампы (см. файл конфигурации `config/smart_devices.yaml`)
  """  
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')

  show_caption('Свет')
  result = smart.light_on(bulb_info = smart_devices['default_bulb'])
  
  if result:
    say('Сделано.')
  else:
    say('Ошибка.')
  
  
def act_light_off(**kwargs):
  """
  Выключение света
  
  В текущей версии релизована поддержка только основной лампы (см. файл конфигурации `config/smart_devices.yaml`)
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  show_caption('Выключаю')
  result = smart.light_off(bulb_info = smart_devices['default_bulb'])
  
  if result:
    say('Сделано.')
  else:
    say('Ошибка.')
    
    
def act_light_normal(**kwargs):
  """
  Обычный свет (базовые параметры)
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  show_caption('Свет')
  result = smart.light_normal(bulb_info = smart_devices['default_bulb'])
  
  if result:
    say('Сделано.')
  else:
    say('Ошибка.')


def act_light_alarm(**kwargs):
  """
  Тревога! (индикация светом)
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  show_caption('Тревога')
  result = smart.light_alarm(bulb_info = smart_devices['default_bulb'])
  
  if not result:
    say('Ошибка.')
  
  
def act_light_red(**kwargs):
  """
  Красный свет
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  show_caption('Красный')
  result = smart.light_color(bulb_info = smart_devices['default_bulb'], color = 'red')
  
  if not result:
    say('Ошибка.')
  
  
def act_light_green(**kwargs):
  """
  Зелёный свет
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  show_caption('Зелёный')
  result = smart.light_color(bulb_info = smart_devices['default_bulb'], color = 'green')
  
  if not result:
    say('Ошибка.')
  
  
def act_light_blue(**kwargs):
  """
  Синий свет
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  show_caption('Синий')
  result = smart.light_color(bulb_info = smart_devices['default_bulb'], color = 'blue')
  
  if not result:
    say('Ошибка.')
  
  
def act_light_yellow(**kwargs):
  """
  Жёлтый свет
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  show_caption('Жёлтый')
  result = smart.light_color(bulb_info = smart_devices['default_bulb'], color = 'yellow')
  
  if not result:
    say('Ошибка.')
  
  
def act_light_orange(**kwargs):
  """
  Оранжевый свет
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  show_caption('Оранжевый')
  result = smart.light_color(bulb_info = smart_devices['default_bulb'], color = 'orange')
  
  if not result:
    say('Ошибка.')
  
  
def act_light_bluelight(**kwargs):
  """
  Голубой свет
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  show_caption('Голубой')
  result = smart.light_color(bulb_info = smart_devices['default_bulb'], color = 'bluelight')
  
  if not result:
    say('Ошибка.')
  
  
def act_light_purple(**kwargs):
  """
  Фиолетовый свет
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  show_caption('Фиолетовый')
  result = smart.light_color(bulb_info = smart_devices['default_bulb'], color = 'purple')
  
  if not result:
    say('Ошибка.')
  
  
def act_light_pink(**kwargs):
  """
  Розовый свет
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  show_caption('Розовый')
  result = smart.light_color(bulb_info = smart_devices['default_bulb'], color = 'pink')
  
  if not result:
    say('Ошибка.')
  
  
def act_light_brightness(**kwargs):
  """
  Установка яркости на заданное количество процентов (10-100)
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  bright = None
  
  # Определим значение яркости
  try:
    bright = int(re.findall(r'^\D+(\d+)\D*$', text)[0])
  except:
    info = 'Ошибка. Значение яркости не определено.'
    print(info)
    say(info)
  
  if bright:
    show_caption('Смена яркости')
    result = smart.light_brightness(bulb_info = smart_devices['default_bulb'], brightness = bright)
    
    if not result:
      say('Ошибка.')
  
  
def act_light_color_temperature(**kwargs):
  """
  Установка цветовой температуры на указанную величину (1500-7700)
  """
  if not check_smart_bulbs(): return
  text = kwargs.get('text', '')
  
  color_temp = None
  
  # Определим значение яркости
  try:
    color_temp = int(re.findall(r'^\D+(\d+)\D*$', text)[0])
  except:
    info = 'Ошибка. Значение температуры не определено.'
    print(info)
    say(info)
  
  if color_temp:
    show_caption('Смена температуры')
    result = smart.light_color_temperature(bulb_info = smart_devices['default_bulb'], color_temperature = color_temp)
    
    if not result:
      say('Ошибка.')

## @@
## -- end ACTIONS (действия) ------------------------------------------------------------------ ##


def my_except_hook(extype, value, traceback):
  """
  Перехватчик исключений
  """
  print(f'{extype} - {value} - {traceback}')
  

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
  print('Инициализация...')

  setup(config_file)
  
  # Загрузка карты реакций
  print('Загрузка карты реакций')
  load_reactions_map() ##
  
  # Проверка доступности внешнего приложения для проигрывания файлов
  if not is_external_player_exists():
    print(f'\nНе найдено внешнее приложения для проигрывания файлов (подразумевается наличие плеера MPV)!\n\a')
    sys.exit(0)
  
  random.seed()
  
  init_locale()
  
  print('Активация основного механизма распознавания речи')
  init_speech_recognizer()
  
  if SR_LOCAL_VIA_VOSK or SR_LOCAL_FOR_KEYPHRASE:
    print('Активация механизма VOSK локального распознавания речи')
    init_vosk_engine()
  
  print('Активация механизма генерации речи')
  init_tts()
  
  print('Активация переводчика')
  init_translator()
  
  print('Установка браузера для веб-поиска')
  init_web_browser()
  
  print('Открытие и загрузка локальных баз данных')
  open_databases()
  
  load_quotes()
  load_irr_verbs()  
  load_phrasal_verbs()
  
  print('Загрузка списка умных устройств')
  load_smart_devices()
  
  # Корректировка громкости звука
  set_system_volume(config.engine.system_volume_default)
  
  ##print(ansi.clear_screen())


def run(config_file=None):
  """
  Основная точка входа. 
  Инициализация. 
  Запуск цикла распознавания и обработки.
  """
  # Инициализация
  init(config_file)
  
  print(ansi.clear_screen())
  
  ##beep()
  say(f'Привет. {ROBOT_NAME} на связи.')
  
  #DEBUG
  #sys.excepthook = my_except_hook
  #print('\nOK')
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
