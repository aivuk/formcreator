# -*- coding: utf-8 -*-

from formcreator import *

cat_desc = markdown(u"""
Exemplo usando o cat
===========

O ***formulário*** a seguir irá pegar ou um arquivo que você der upload, ou
algum arquivo no sistema e exibir o conteúdo abaixo.

""")

cat = Form("cat", name="cat", desc=cat_desc, dirs=["updir"])

cat += File( u'Filename or Path'
           , u'Name of file/directory to run ls -l'
           , upload_directory='updir')

cat += SelectFile( u'Filename or Path'
                 , files_directory='updir')

cat += Doc("""
***Texto separador***


Pode conter imagens como:

![Fractal](http://static.neatorama.com/images/2008-01/fractal-art-alfred-laing-spiral-fantasy.jpg)

""")

cat += Text( u'Filename or Path'
           , u'Name of file/directory to run ls -l')

cat += Boolean( u'Test boolean'
              , cmd_opt="-l")

def duplica(num, exp=1, to_exp=False):
    if to_exp:
        return 2*(num**exp)
    else:
        return 2*num

dup =  Form(duplica, desc="Show file contents", name="func", output_type="html")

dup += Integer( u'Número'
                 , u'Número que será multiplicado')

dup += Integer( u'Expoente'
                 , u'Expoente do número'
                 , cmd_opt='exp')

dup += Boolean( u'Eleva ao expoente'
                 , cmd_opt='to_exp')

cowsay = Form("cowsay")
cowsay += TextArea("Texto")
cowsay += Doc("""

Olha a Vaca!
===========
Programa que desenha uma _vaca_.

![Fractal](http://static.neatorama.com/images/2008-01/fractal-art-alfred-laing-spiral-fantasy.jpg)

""")

test_app = MainApp('Testing', [cat, dup, cowsay])
test_app.run()
