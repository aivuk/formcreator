# -*- coding: utf-8 -*-

from formcreator import *

webCmd = wCmd("ls", desc="ls -l", name="ls")

webCmd += Text('path'
              , u'Filename or Path'
              , u'Name of file/directory to run ls -l'
              , cmd_opt='-l')

webCmd += Text('path2'
              , u'Filename or Path'
              , u'Name of file/directory to run ls -l')

def duplica(num, exp=1):
    return 2*(num**exp)

catCmd =  wCmd(duplica, desc="Show file contents", name="func")

catCmd += Integer(u'numero'
                 , u'Número'
                 , u'Número que será multiplicado')

catCmd += Integer(u'exp'
                 , u'Expoente'
                 , u'Expoente do número'
                 , cmd_opt='exp')

test_app = MainApp('Testing', [webCmd, catCmd])
test_app.run()
