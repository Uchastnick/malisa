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

  if text:
    m.say(text)

  #############################
  # END                       #
  #############################

if __name__=='__main__':
  action(text='Привет. Как дела?')
