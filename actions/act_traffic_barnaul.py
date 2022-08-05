try:
  import init
except: 
  pass

import malisa as m

import requests

try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET


def get_traffic_barnaul_info():
  """
  Информация о загруженности на дорогах в городе Барнаул
  """
  result = None  
  url = 'https://export.yandex.ru/bar/reginfo.xml?region=197'
  
  try:
    content = requests.get(url).text
    xml_tree = ET.fromstring(content)

    for e in xml_tree:
      if e.tag == 'traffic':
        for traffic_ch in e:
          if traffic_ch.tag == 'region':
            for region_ch in traffic_ch:
              if region_ch.tag == 'hint' and region_ch.attrib.get('lang', '') == 'ru':
                result = region_ch.text
                break
            break
        break
  
  except Exception as e:
    print(e)
    result = None
    
  return result
  

def action(**kwargs):
  """
  Информация о загруженности на дорогах в городе Барнаул
  """  
  
  # Распознанный внешней процедурой текст (передаётся в action-процедуру)
  text = kwargs.get('text', None)
  m.init_tts()

  #############################
  # Размещайте Ваш код здесь. #
  # Put your code here.       #
  # BEGIN                     #
  #############################
  
  info = get_traffic_barnaul_info()
  
  if info:
    print(f'\n {info}')
    m.say(info)
  else:
    m.say('Информация не найдена.')

  #############################
  # END                       #
  #############################

if __name__=='__main__':
  action()
