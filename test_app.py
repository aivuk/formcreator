# -*- coding: utf-8 -*-

from formcreator import *

cat_desc = markdown(u"""
Exemplo usando o cat
===========

O ***formulário*** a seguir irá pegar ou um arquivo que você der upload, ou
algum arquivo no sistema e exibir o conteúdo abaixo.

""")

webCmd = Form("cat", name="cat", desc=cat_desc, dirs=["updir"])

webCmd += File( u'Filename or Path'
              , u'Name of file/directory to run ls -l'
              , upload_directory='updir')

webCmd += SelectFile( u'Filename or Path'
                    , files_directory='updir')

webCmd += Text( u'Filename or Path'
              , u'Name of file/directory to run ls -l')

webCmd += Boolean( u'Test boolean'
                 , cmd_opt="-l")

def duplica(num, exp=1, to_exp=False):
    if to_exp:
        return 2*(num**exp)
    else:
        return 2*num

catCmd =  Form(duplica, desc="Show file contents", name="func", output_type="html")

catCmd += Integer( u'Número'
                 , u'Número que será multiplicado')

catCmd += Integer( u'Expoente'
                 , u'Expoente do número'
                 , cmd_opt='exp')

catCmd += Boolean( u'Eleva ao expoente'
                 , cmd_opt='to_exp')

cowsay = Form("cowsay")
cowsay += Text("Texto")

test_app = MainApp('Testing', [webCmd, catCmd, cowsay])
test_app.run()
