try:
  import init
except: 
  pass

import malisa as m

import requests
import lxml.html


def get_air_pollution_barnaul_info():
  """
  Получить общую информацию об уровене загрязнения воздуха в городе Барнаул
  """
  result = None  
  url = 'http://meteo22.ru'
  
  try:
    content = requests.get(url).text
    html_tree = lxml.html.fromstring(content)

    result = html_tree.xpath('.//div[@class="pollution"]//div[@class="table table10"]//div[@class="td5"]')[-2].text
    result = result.replace('г.', ' года').replace(' города', '')
  
  except Exception as e:
    print(e)
    result = None
    
  return result
  

def action(**kwargs):
  """
  Информация об уровене загрязнения воздуха в городе Барнаул
  """  
  
  # Распознанный внешней процедурой текст (передаётся в action-процедуру)
  text = kwargs.get('text', None)
  m.init_tts()

  #############################
  # Размещайте Ваш код здесь. #
  # Put your code here.       #
  # BEGIN                     #
  #############################
  
  info = get_air_pollution_barnaul_info()

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
