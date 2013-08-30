# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, escape, g
import wtforms
import subprocess as sp

SCRIPT_URL = '/'
SCRIPT_PATH = '.'

app = Flask(__name__)
app.config.from_pyfile('app.cfg')

class MainApp(object):

  def __init__(self, name, cmds):
        self.name = name
        self.cmds = cmds

class wCmd(object):

    def __init__(self, command, command_name, command_description):
        self.form = wtforms.form.BaseForm(())
        self.command = command
        self.command_name = command_name
        self.command_description = command_description

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

    def process(self, form_data):
        self.form.process(form_data)

    def run(self):
        cmd_parts = [self.command]
        for field in self.form:
            cmd_parts += [field.cmd_opt, field.data]

        self.stdout = sp.Popen(cmd_parts, stdout=sp.PIPE).communicate()[0].decode('utf8')

webCmd = wCmd("ls", "ls -l", "List file info")
webCmd.add( 'ls_attr'
          , '-l'
          , u'Filename'
          , u'Name of file/directory to run ls -l')

test_app = MainApp('Testing', [webCmd])

def form():
    f = webCmd

    if request.method == 'POST':
       f.process(request.form)
       f.run()
    else:
       f.stdout = ''

    return render_template('form.html', form=f.list_form(), output=f.stdout, app=test_app)

app.add_url_rule(SCRIPT_URL, 'form', form, methods=['GET', 'POST'])

if __name__ == "__main__":
    app.run(debug=True,host='127.0.0.1')


