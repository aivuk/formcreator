formcreator
===========

_formcreator_ is a program that creates simple web forms for
your programs or python functions, without requiring to write
any webprogramming code.

Onde simple example, with you want to create a simple form for
the _man_ program, you can just write the code:

```python

from formcreator import *

man  = Form("man")
man += Boolean("Apropos mode?", cmd_opt="-k")
man += Text("What manual page?")

app = MainApp("Man interface", [man])
app.run()
```

You can run the program above with:

```
$ python app.py
```

If you go to your browser at _http://localhost:5000_, you will
see the form:

![Imgur](http://i.imgur.com/CT6lZQp.png)

You can use other fields types like __TextArea__, __File__ for file uploads, 
__SelectFile__ for a widget where you can select a file from a directory,
simple numerical types like __Integer__, __Decimal__ and __Float__. You can
insert Markdown text between the fields of your form with the special type __Doc__:

```python

from formcreator import *

man  = Form("man")
man += Boolean("Apropos mode?", cmd_opt="-k")
man += Doc("""
Man web interface
=================

This is a simple example of a _form_ with
two fields. 

![Tux image])(http://images.all-free-download.com/images/graphiclarge/linux_tux_1_107532.jpg)

""")
man += Text("What manual page?")

app = MainApp("Man interface", [man])
app.run()
```

A MainApp can have more than one form inside, you just need to pass the
forms like:

```python
app = MainApp("Example", [man, cowsay, convert])
```

If the first argument to __Form__ is not a string and is a python function,
the form created you be for this function:

```python
from formcreator import *

def f(x, d=1):
	return x**d

simple  = Form(f)
simple += Integer("A number")
simple += Integer("Other number", cmd_opt="d")

app = MainApp("Function example", [simple])
app.run()
```

When the form is for a function, all fields with _cmd_opt_ arguments will be passed
like keywords arguments for the python function.
If you want to see contents of one or more directories in the webinterface, 
you just need to pass the _dirs_ argument to __Form__:

```python
Form(f, dirs=["updir"])
```

And you will see this on the form page:

![Directory contents](http://i.imgur.com/KkPrU6d.png)

This is usefull when the output of your function or programa is a file. In this case
you can use that widget to download the new file created.

You can see the more complex example [test_app.py](https://github.com/aivuk/formcreator/blob/master/test_app.py) in the repository.

TODO
-----

* User access control.
* Save form sessions.
* Better widgets for file selection.
* Other types of fields (Select, Checkbox, etc).
* Handle cases when program do not terminate. 
