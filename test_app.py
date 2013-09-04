# -*- coding: utf-8 -*-

from formcreator import *

man_desc = markdown(u"""
Example using _man_
===========

And showing that you can use markdown on a form description.
""")

man  = Form("man", name="man", desc=man_desc, dirs=["updir"])
man += Boolean( u'Apropos mode'
              , cmd_opt="-k")
man += Boolean( u'Whatis mode'
              , cmd_opt="-f")
man += Text( u'Page'
           , u'What manual page do you want?')

wc  = Form("wc")
wc += File("File to count", upload_directory="wc-files")
wc += SelectFile("Or select a uploaded file", files_directory="wc-files")
wc += Boolean("Lines", cmd_opt="-l")
wc += Boolean("Characters", cmd_opt="-c")
wc += Boolean("Words", cmd_opt="-w")

def calc(num, exp=1, to_exp=False):
    if to_exp:
        return 2*(num**exp)
    else:
        return 2*num

dup  =  Form(calc, name="function", output_type="html")
dup += Integer( u'Number')
dup += Integer( u'Exponent'
              , cmd_opt='exp')
dup += Doc("""
Calculate the function:

    f(n,e) = 2*(n**e)

But just use the exponent if asked.
""")
dup += Boolean( u'Use exponent?'
              , cmd_opt='to_exp')

cowsay = Form("cowsay")
cowsay += Doc("""

What the cow needs to say?
===========

![Typical cowsay output](http://upload.wikimedia.org/wikipedia/commons/8/80/Cowsay_Typical_Output.png)

And you can see here that you can use markdown text to create text content in your forms.
""")
cowsay += TextArea("Texto")

convert  = Form("convert", dirs=["images"])
convert += Integer("Degrees", cmd_opt="-rotate")
convert += File("Image", upload_directory="images")
convert += SelectFile("Or select an image below", files_directory="images")
convert += Text("New image name")

test_app = MainApp('Testing', [man, dup, cowsay, convert])
test_app.run()
