# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, escape, g
import wtforms
import subprocess as sp

SCRIPT_URL = '/'
SCRIPT_PATH = '.'

app = Flask(__name__)
app.config.from_pyfile('app.cfg')

class wCmd(object):

    def __init__(self, command):
        self.form = wtforms.form.BaseForm(())
        self.command = command

    def add(self, name, cmd_opt, label, info=u'', field_type=wtforms.TextField, default=None):
        if name in self.form:
            print "Field name already exist"
            raise
        else:
            self.form[name] = field_type(label, description=info)
            new_field = self.form[name]
            new_field.position = len(self.form._fields) + 1
            new_field.data = default or ''
            new_field.cmd_opt = cmd_opt

    def list_form(self):
        fs = list(self.form)
        fs.sort(key = lambda x: x.position)
        return fs

    def run(self):
        sp.Popen(self.command)

webCmd = wCmd("ls")
webCmd.add( 'ls_attr'
          , '-l'
          , u'Filename'
          , u'Name of file to show attributes')

# webCmd.add( 'arg_num2'
#           , '-f'
#           , u'Número de parâmetros'
#           , u'Número entre 0 e 30')

def form():
    f = webCmd

    if request.method == 'POST':
       f.form.process(request.form)
       o = [f.command]
       for field in f.form:
           o += [field.cmd_opt, field.data]

       output = sp.Popen(o, stdout=sp.PIPE).communicate()[0]
       return render_template('form.html', output=output)
    else:
       return render_template('form.html', form=f.list_form())

app.add_url_rule(SCRIPT_URL, 'form', form, methods=['GET', 'POST'])

if __name__ == "__main__":
    app.run(debug=True,host='127.0.0.1')
