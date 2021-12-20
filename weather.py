from datetime import datetime, timedelta


def get_wind_direction(deg):
  """
  Определение направления ветра по величине, указанной в градусах
  """
  direction = ''  
  if deg >= 348.75 or deg < 11.25:
    direction = 'Северный'
  elif deg >= 33.75 and deg < 78.75:
    direction = 'Северо-Восточный'
  elif deg >= 78.75 and deg < 101.25:
    direction = 'Восточный'
  elif deg >= 101.25 and deg < 168.75:
    direction = 'Юго-Восточный'
  elif deg >= 168.75 and deg < 191.25:
    direction = 'Южный'
  elif deg >= 191.25 and deg < 258.75:
    direction = 'Юго-Западный'
  elif deg >= 258.75 and deg < 281.25:
    direction = 'Западный'
  elif deg >= 281.25 and deg < 348.75:
    direction = 'Северо-Западный'
  return direction
  
  
def format_float_value(value):
  """
  Форматирование значений дробной величины
  """
  return str(value).replace('.', ' и ')


def get_now_weather_info(data_json):
  """
  Получить информацию о состоянии погоды `сейчас`, из соответствующего раздела json
  """
  result = None

  temp            = round(data_json['main']['temp'], 1)
  temp_feels_like = round(data_json['main']['feels_like'], 1)
  
  pressure        = data_json['main']['pressure']
  humidity        = data_json['main']['humidity']
  
  sunrise         = datetime.fromtimestamp(data_json['sys']['sunrise'])
  sunset          = datetime.fromtimestamp(data_json['sys']['sunset'])
  
  wind_speed      = round(data_json['wind']['speed'], 1)  
  wind_deg        = data_json['wind']['deg']
  wind_direction  = get_wind_direction(wind_deg)
  
  #clouds        = data_json['clouds']['all']
  #rain          = data_json['rain']['1h']
  #snow          = data_json['rain']['1h']

  description     = data_json['weather'][0]['description']

  result = (f"  За окном '{format_float_value(temp)}' градусов,"
            f" ощущается '{format_float_value(temp_feels_like)}'.\n"
            
            f" Влажность - {humidity}.\n"
            f" Скорость ветра - '{format_float_value(wind_speed)}'."
            f" Ветер - {wind_direction}.\n"
            f"  {description.title()}.\n"
            f" Восход солнца в '{sunrise.strftime('%H:%M')}'."
            f" Закат - в '{sunset.strftime('%H:%M')}'.")
           
  return result
  
  
def get_current_weather_info(data_json):
  """
  Получить информацию о текущем состоянии погоды, из соответствующего раздела json
  """
  result = None
  
  dt              = datetime.fromtimestamp(data_json['dt'])  
  sunrise         = datetime.fromtimestamp(data_json['sunrise'])
  sunset          = datetime.fromtimestamp(data_json['sunset'])
  
  temp            = round(data_json['temp'], 1)
  temp_feels_like = round(data_json['feels_like'], 1)
  
  pressure        = data_json['pressure']
  humidity        = data_json['humidity']  
  uvi             = data_json['uvi']
  
  #visibility      = data_json['visibility']
  clouds          = data_json.get('clouds', 'нет')
  snow            = data_json.get('snow', 'нет')
  
  wind_speed      = round(data_json['wind_speed'], 1)
  wind_deg        = data_json['wind_deg']
  wind_direction  = get_wind_direction(wind_deg)
  
  description     = data_json['weather'][0]['description']

  result = (f"  Сейчас '{format_float_value(temp)}' градусов,"
            f" ощущается '{format_float_value(temp_feels_like)}'.\n"
            
            f" Влажность - {humidity}. Ультрафиолет - '{uvi}'. Облачность - {clouds}. Снег - {snow}.\n"
            f" Скорость ветра - '{format_float_value(wind_speed)}'."
            f" Ветер - {wind_direction}.\n"
            f"  {description.title()}.\n"
            f" Восход солнца в '{sunrise.strftime('%H:%M')}'."
            f" Закат - в '{sunset.strftime('%H:%M')}'.")

  return result


def get_daily_weather_info(data_json):
  """
  Получить дневной прогнозе погоды, из соответствующего раздела json
  """
  result = None

  dt              = datetime.fromtimestamp(data_json['dt'])
  sunrise         = datetime.fromtimestamp(data_json['sunrise'])
  sunset          = datetime.fromtimestamp(data_json['sunset'])
  
  moonrise        = datetime.fromtimestamp(data_json['moonrise'])
  moonset         = datetime.fromtimestamp(data_json['moonset'])
  moon_phase      = data_json['moon_phase']  

  temp_day        = round(data_json['temp']['day'], 1)
  temp_min        = round(data_json['temp']['min'], 1)
  temp_max        = round(data_json['temp']['max'], 1)
  temp_night      = round(data_json['temp']['night'], 1)
  temp_eve        = round(data_json['temp']['eve'], 1)
  temp_morn       = round(data_json['temp']['morn'], 1)
  
  temp_feels_like_day   = round(data_json['feels_like']['day'], 1)
  temp_feels_like_night = round(data_json['feels_like']['night'], 1)
  temp_feels_like_eve   = round(data_json['feels_like']['eve'], 1)
  temp_feels_like_morn  = round(data_json['feels_like']['morn'], 1)
  
  pressure        = data_json['pressure']
  humidity        = data_json['humidity']
  uvi             = data_json['uvi']
  
  #visibility      = data_json['visibility']
  clouds          = data_json.get('clouds', 'нет')
  snow            = data_json.get('snow', 'нет')
  pop             = data_json['pop']
  
  wind_speed      = round(data_json['wind_speed'], 1)
  wind_deg        = data_json['wind_deg']
  wind_direction  = get_wind_direction(wind_deg)
  wind_gust       = data_json.get('wind_gust', 'нет')
  
  description     = data_json['weather'][0]['description']

  result = (f" {dt.strftime('%B, %d. %A').title()}.\n"
            
            f"  Утром '{format_float_value(temp_morn)}' градусов,"
            f" ощущается '{format_float_value(temp_feels_like_morn)}'.\n"

            f"   Днём '{format_float_value(temp_day)}' градусов,"
            f" ощущается '{format_float_value(temp_feels_like_day)}'.\n"
            
            f"  Вечером '{format_float_value(temp_eve)}' градусов,"
            f" ощущается '{format_float_value(temp_feels_like_eve)}'.\n"
            
            f"  Ночью '{format_float_value(temp_night)}' градусов,"
            f" ощущается '{format_float_value(temp_feels_like_night)}'.\n"
            
            f" Влажность - {humidity}. Ультрафиолет - '{uvi}'. Облачность - {clouds}. Снег - {snow}.\n"
            f" Скорость ветра - '{format_float_value(wind_speed)}'."
            f" Ветер - {wind_direction}. Порывы - '{format_float_value(wind_gust)}'.\n"
            f"  {description.title()}.")
  
  return result


def get_weather_alerts_info(alerts_json_array):
  """
  Получить список оповещений из прогноза погоды, из соответствующего раздела json
  """
  alerts_info = ''
  
  for alert in alerts_json_array:
    if not alert['description']: continue
    
    event_start = datetime.fromtimestamp(alert['start'])
    event_end   = datetime.fromtimestamp(alert['end'])
    
    alerts_info += (f" {event_start.strftime('%d.%m, %Hч.')}-{event_end.strftime('%Hч.')}:"
                    f" {alert['event']}, {alert['description']}.\n")
  
  alerts_info = alerts_info.rstrip('\n')
  return alerts_info
