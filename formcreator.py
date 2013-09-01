# -*- coding: utf-8 -*-

from __future__ import unicode_literals
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
        self.active = cmd_name
        f.stdout = ''

        if request.method == 'POST':
            f.process(request.form)
            if f.form.validate():
                f.run()

        return render_template('form.html', form=f.list_form(), output=f.stdout, app=self)

def makeOpt(field_type, process_formdata=None):
    class Opt(object):

        def __init__(self, name, label='', description='', default='', cmd_opt=None, **kwargs):
            self.name = name
            self.default = default
            self.field = field_type(label=label, description=description, **kwargs)
            if cmd_opt:
                self.cmd_opt = cmd_opt
            if process_formdata:
                self.field.process_formdata = process_formdata

    return Opt

class Upload(wtforms.FileField):
    def __init__(self, *args, **kwargs):
        self.upload_directory = kwargs['upload_directory'] if kwargs.has_key('upload_directory') else '/tmp'
        if not os.path.isdir(self.upload_directory):
            os.mkdir(self.upload_directory)
        kwargs.pop('upload_directory')
        super(Upload, self).__init__(*args, **kwargs)

    def process_formdata(self, data):
        uploaded_file = request.files[self.name]
        if uploaded_file.filename:
            file_path = os.path.join(self.upload_directory, uploaded_file.filename)
            uploaded_file.save(file_path)
            self.data = file_path
        else:
            self.data = ''

Text = makeOpt(wtforms.TextField)
File = makeOpt(Upload)
Integer = makeOpt(wtforms.IntegerField)
Float = makeOpt(wtforms.FloatField)
Decimal = makeOpt(wtforms.DecimalField)

class wCmd(object):

    def __init__(self, command, name='', desc=''):
        self.form = wtforms.form.BaseForm(())
        self.command = command
        if str(type(command)) == "<type 'function'>":
            self.cmd_type = "function"
        else:
            self.cmd_type = "program"
        self.name = name
        self.desc = desc

    def __add__(self, opt):
        if opt.name in self.form:
            print ("Field name already exist")
            raise
        else:
            self.form[opt.name] = opt.field
            new_field = self.form[opt.name]
            new_field.position = len(self.form._fields) + 1
            new_field.data = opt.default or ''
            if hasattr(opt, "cmd_opt"):
                new_field.cmd_opt = opt.cmd_opt
        return self

    def list_form(self):
        fs = list(self.form)
        fs.sort(key = lambda x: x.position)
        return fs

    def process(self, form_data):
        self.form.process(form_data)

    def run_cmd(self):
        cmd_parts = [self.command]
        for field in self.form:
            if hasattr(field, 'cmd_opt'):
                cmd_parts += [field.cmd_opt, field.data]
            else:
                cmd_parts += [field.data]
        cmd = sp.Popen(cmd_parts, stdout=sp.PIPE, stderr=sp.STDOUT).communicate()
        self.stdout = cmd[0].decode('utf8')

    def run_function(self):
        args = []
        kwargs = {}

        for field in self.form:
            if hasattr(field, 'cmd_opt'):
                kwargs[field.cmd_opt] = field.data
            else:
                args.append(field.data)

        self.stdout = self.command(*args, **kwargs)

    def run(self):
        if self.cmd_type == 'function':
            self.run_function()
        else:
            self.run_cmd()
