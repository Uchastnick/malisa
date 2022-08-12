"""
  Парамеры цветов и оттенков.
  Плюс вспомогательные функции.
"""

# Список цветов и оттенков
colors = {
  'default': {
    'rgb': (255, 255, 255),
    'hsv': (30, 0, 100)
  },

  'white': {
    'rgb': (255, 255, 255),
    'hsv': (30, 0, 100)
  },
  
  'red': {
    'rgb': (255, 0, 0),
    'hsv': (0, 100, 100)  
  },
  
  'green': {
    'rgb': (0, 255, 0),
    'hsv': ()
  },
  
  'blue': {
    'rgb': (0, 0, 255),
    'hsv': ()
  },
  
  'yellow': {
    'rgb': (255, 200, 0),
    'hsv': ()  
  },
  
  'orange': {
    'rgb': (255, 165, 0),
    'hsv': ()
  },
  
  'bluelight': {
    'rgb': (0, 255, 255),
    'hsv': ()  
  },
  
  'purple': {
    'rgb': (128, 0, 128),
    'hsv': ()  
  },

  'pink': {
    'rgb': (219, 112, 147),
    'hsv': ()  
  },    
}
  
  
def get_rgb_for_color(color_name):
  """
  Получить параметры (R,G,B) для указанного цвета.
  Если не найдено, возвращает по умолчанию как для белого цвета.
  """
  rgb = (255, 255, 255)
    
  color = colors.get(color_name, {})
  if color: rgb = color.get('rgb', rgb)
  
  return rgb


def get_hsv_for_color(color_name):
  """
  Получить параметры (H,S,V) для указанного цвета.
  Если не найдено, возвращает по умолчанию как для белого цвета.
  """
  hsv = (30, 0, 100)
  
  color = colors.get(color_name, {})
  if color: hsv = color.get('hsv', hsv)
  
  return hsv


if __name__=='__main__':
  pass  
