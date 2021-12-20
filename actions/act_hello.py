try:
  import init
except: 
  pass

import malisa as m

def action(**kwargs):
  """
  Описание / Description
  """  
  
  # Распознанный внешней процедурой текст (передаётся в action-процедуру)
  text = kwargs.get('text', None)
  m.init_tts()

  #############################
  # Размещайте Ваш код здесь. #
  # Put your code here.       #
  # BEGIN                     #
  #############################  

  m.say('Привет!')
  m.say('How are you?', 'en')
  
  m.say_by_external_engine('How are you?', 'en')
  m.say_by_external_engine('Wie geht es dir?', 'de')

  if text:
    m.say(text)

  #############################
  # END                       #
  #############################

if __name__=='__main__':
  action(text='Как дела?')
