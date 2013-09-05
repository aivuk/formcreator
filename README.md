formcreator
===========

_formcreator_ is a program that creates simple web forms for
your programs or python functions, without requiring any 
webprogramming code.

An example, if you want to create a simple form for
the _man_ program, you can write the code:

```python

from formcreator import *

man  = Form("man")
man += Boolean("Apropos mode?", cmd_opt="-k")
man += Text("What manual page?")

app = MainApp("Man interface", [man])
app.run()
```

And run the program above:

```
$ python app.py
```

If you go to your browser at _http://localhost:5000_ you will
see the form:

![Imgur](http://i.imgur.com/CT6lZQp.png)

You can use other field types like __TextArea__, __File__ for file uploads, 
__SelectFile__ for a widget where you can select a file from a directory,
simple numerical types like __Integer__, __Decimal__ and __Float__. Is possible
to insert any Markdown text between your form fields with the type __Doc__:

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

A MainApp can have more than one form inside, just pass the forms like:

```python
app = MainApp("Example", [man, cowsay, convert])
```

If the first argument to __Form__ is not a string and is a python function,
the form data will be used in this function:

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

In this case, all fields with _cmd_opt_ arguments will be passed
like keywords arguments for the python function.
If you want to see contents of one or more directories in the web interface, 
just pass the _dirs_ argument to __Form__:

```python
Form(f, dirs=["updir"])
```

And you will see this on the form page:

![Directory contents](http://i.imgur.com/KkPrU6d.png)

This is usefull when the output of your function or program is in a file. In the 
widget you can download any file created.

You can see a more complex example [test_app.py](https://github.com/aivuk/formcreator/blob/master/test_app.py) in the repository.

TODO
-----

* User access control.
* Save form sessions.
* Tests!
* Display image results.
* Better widgets for file selection.
* Other types of fields (Select, Checkbox, etc).
* Handle cases when program do not terminate. 
