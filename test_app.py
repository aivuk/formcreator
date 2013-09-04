# -*- coding: utf-8 -*-

from formcreator import *

man_desc = markdown(u"""
Example using _man_
===========

""")

man = Form("man", name="man", desc=man_desc, dirs=["updir"])

man += Text( u'Page'
           , u'What manual page do you want?')

man += Boolean( u'Apropos mode'
              , cmd_opt="-k")

man += Boolean( u'Whatis mode'
              , cmd_opt="-f")

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
cowsay += Doc("""

What the cow needs to say?
===========

![Typical cowsay output](http://upload.wikimedia.org/wikipedia/commons/8/80/Cowsay_Typical_Output.png)

And you can see here that you can use markdown text to create text content in your forms.
""")
cowsay += TextArea("Texto")

test_app = MainApp('Testing', [man, dup, cowsay])
test_app.run()
