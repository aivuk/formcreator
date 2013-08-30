# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, escape, g
import wtforms
from functools import partial
import subprocess as sp
import os

SCRIPT_URL = '/'
SCRIPT_PATH = '.'

class MainApp(object):

    def __init__(self, name, cmds):
        self.name = name
        self.cmds = {c.name: c for c in cmds}
        self.app = Flask(__name__)
        self.app.config.from_pyfile('app.cfg')

        for i, cmd in enumerate(self.cmds.values()):
            self.app.add_url_rule(SCRIPT_URL + (cmd.name if i > 0 else ''), cmd.name, partial(self.form, cmd.name), methods=['GET', 'POST'])

    def run(self):
       self.app.run(debug=True,host='127.0.0.1')

    def form(self, cmd_name):
        f = self.cmds[cmd_name]

        if request.method == 'POST':
           f.process(request.form)
           f.run()
        else:
           f.stdout = ''

        return render_template('form.html', form=f.list_form(), output=f.stdout, app=self)

class wCmd(object):

    def __init__(self, command, name='', desc=''):
        self.form = wtforms.form.BaseForm(())
        self.command = command
        self.name = name if name else command
        self.desc = desc

    def add(self, name, label='', info=u'', cmd_opt=None,  default=None, field_type=wtforms.TextField):
        if name in self.form:
            print "Field name already exist"
            raise
        else:
            self.form[name] = field_type(label, description=info)
            new_field = self.form[name]
            new_field.position = len(self.form._fields) + 1
            new_field.data = default or ''
            if cmd_opt:
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
            if hasattr(field, 'cmd_opt'):
                cmd_parts += [field.cmd_opt, field.data]
            else:
                if field.name == 'file':
                    file = request.files[field.name]
                    file.save(os.path.join('.', file.filename))
                    cmd_parts += [file.filename]
                else:
                    cmd_parts += [field.data]

        cmd = sp.Popen(cmd_parts, stdout=sp.PIPE, stderr=sp.STDOUT).communicate()
        self.stdout = cmd[0].decode('utf8')


