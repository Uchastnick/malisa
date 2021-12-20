"""
  Функции для загрузки новостей из различных источников
"""

import requests
import feedparser
from pprint import pprint

from config.config import NEWS_API

RSS_LINK_AMIC = 'https://www.amic.ru/rss'
RSS_LINK_ALTAPRESS = 'https://altapress.ru/rss'
RSS_LINK_HABR = 'https://habr.com/ru/rss'

def get_news():
  """
  Получение новостей с `newsapi.org`
  """
  news = []
    
  url = f'https://newsapi.org/v2/top-headlines?country=ru&pageSize=100&sortBy=popularity&apiKey={NEWS_API}'

  #domains = 'ria.ru,rbc.ru,russian.rt.com,lenta.ru'
  #from_day = f'{datetime.now().strftime("%Y-%m-%d")}'
  
  #url = (f'https://newsapi.org/v2/everything?domains={domains}&language=ru&from={from_day}'
  #       f'&pageSize=100&sortBy=popularity&apiKey={NEWS_API}')
 
  try:
    data = requests.get(url).json()
    news = [a['title'] for a in data['articles']]
  except Exception as e:
    print(e)
    news = []
    
  return news


def get_rss_feed_titles(url):
  """
  Получение заголовков новостей из RSS-ленты!
  """
  titles = []  
  
  try:
    feed = feedparser.parse(url)
    titles = [entry.title for entry in feed.entries]
  except Exception as e:
    print(e)
    titles = []

  return titles


def get_news_amic():
  """
  Получение новостей с сайта `amic.ru`
  """
  news = []
  url = f'{RSS_LINK_AMIC}/'  
  news = get_rss_feed_titles(url)
  return news
  

def get_news_altapress():
  """
  Получение новостей с сайта `altapress.ru`
  """
  news = []  
  url = f'{RSS_LINK_ALTAPRESS}/'  
  news = get_rss_feed_titles(url)
  return news


def get_news_habr(chapter='news'):
  """
  Получение новостей с сайта `habr.com`
  Возможно указание раздела, варианты: 'news', 'best/daily', 'all/top50', 'all/all'
  """
  news = []
  url = f'{RSS_LINK_HABR}/{chapter}/?fl=ru'  
  news = get_rss_feed_titles(url)
  return news
  
  
if __name__=='__main__':
  pass
