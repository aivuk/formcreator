from formcreator import *

webCmd = wCmd("cat", desc="Show file contents")
webCmd.add( 'file'
          , u'Filename'
          , u'Name of file/directory to run ls -l'
          , field_type=wtforms.FileField )

test_app = MainApp('Testing', [webCmd])
test_app.run()
