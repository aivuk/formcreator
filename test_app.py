from formcreator import *

webCmd = wCmd("ls", "ls", "Show file contents")
webCmd.add( 'file'
          , u'Filename'
          , u'Name of file/directory to run ls -l' )

webCmd.add( 't'
          , u'Test'
          , u'blah'
          , '-l')

test_app = MainApp('Testing', [webCmd])
test_app.run()
