from formcreator import *

webCmd = wCmd("ls", desc="ls -l")

webCmd += Text('path'
              , u'Filename or Path'
              , u'Name of file/directory to run ls -l'
              , cmd_opt='-l')

webCmd += Text('path2'
              , u'Filename or Path'
              , u'Name of file/directory to run ls -l'
              , cmd_opt='-a')

catCmd =  wCmd("cat", desc="Show file contents")

catCmd += File('file'
              , u'Filename'
              , u'Name of file/directory to run ls -l')

test_app = MainApp('Testing', [webCmd, catCmd])
test_app.run()
