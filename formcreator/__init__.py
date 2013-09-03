# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, escape, g, send_from_directory, Markup
import wtforms
from functools import partial
from ordereddict import OrderedDict
from markdown import markdown
import subprocess as sp
import os

SCRIPT_URL = '/'
SCRIPT_PATH = '.'

class DirContents(object):
    def __init__(self, dir, name=''):
        self.dir = dir
        if name != '':
            self.name = name
        else:
            self.name = dir

    def get_contents(self):
        return os.listdir(self.dir)

    def html(self):
        return render_template('dir_contents.html', dir=self)

class MainApp(object):

    def __init__(self, name, cmds, config='app.cfg', host='127.0.0.1', port='5000'):
        self.name = name
        self.cmds = OrderedDict([(c.name, c) for c in cmds])
        self.app = Flask(__name__)
        self.config = os.path.abspath(config)
        self.app.config.from_pyfile(self.config)
        self.dirs = []
        self.host = host
        self.port = port

        for i, cmd in enumerate(self.cmds.values()):
            self.app.add_url_rule(SCRIPT_URL + (cmd.name if i > 0 else ''), cmd.name, partial(self.form, cmd.name), methods=['GET', 'POST'])

        for c in cmds:
            for d in c.dirs:
                self.app.add_url_rule("{}{}/<path:filename>".format(SCRIPT_URL, d), "{}-{}".format(cmd.name, d), partial(self.serve_files, d), methods=['GET'])
                self.dirs.append(DirContents(d))

    def run(self):
       self.app.run(debug=True, host=self.host)

    def serve_files(self, dir, filename):
        return send_from_directory(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '{}')).format(dir), filename)

    def form(self, cmd_name):
        f = self.cmds[cmd_name]
        self.active = cmd_name
        f.stdout = ''

        if request.method == 'POST':
            f.process(request.form)
            if f.form.validate():
                f.run()

        return render_template('form.html', form=f.list_form(), desc=Markup(f.desc), dirs=self.dirs, output_type=f.output_type, output=f.stdout, app=self)

def makeOpt(field_type, process_formdata=None):
    class Opt(object):

        def __init__(self, label='', description='', name='', default='', cmd_opt=None, **kwargs):
            self.name = name
            self.default = default
            self.field = field_type(label=label, description=description, **kwargs)
            if cmd_opt:
                self.cmd_opt = cmd_opt
            if process_formdata:
                self.field.process_formdata = process_formdata

    return Opt


class SelectFileField(wtforms.HiddenField):
    def __init__(self, *args, **kwargs):
        self.files_directory = kwargs['files_directory']
        self.files = os.listdir(self.files_directory)
        kwargs.pop('files_directory')
        super(SelectFileField, self).__init__(*args, **kwargs)

    def process_formdata(self, data):
        if data[0] != '':
            file_path = os.path.join(self.files_directory, data[0])
            self.data = file_path
        else:
            self.data = ''

    def __call__(self):
        self.files = os.listdir(self.files_directory)
        return render_template('select_files.html', files_directory=self.files_directory, field=self, files=enumerate(self.files))

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

Boolean = makeOpt(wtforms.BooleanField)
SelectFile = makeOpt(SelectFileField)
Text = makeOpt(wtforms.TextField)
File = makeOpt(Upload)
Integer = makeOpt(wtforms.IntegerField)
Float = makeOpt(wtforms.FloatField)
Decimal = makeOpt(wtforms.DecimalField)

class Form(object):

    def __init__(self, command, name='', desc='', output_type='pre', dirs=[]):
        self.form = wtforms.form.BaseForm(())
        self.command = command
        if str(type(command)) == "<type 'function'>":
            self.cmd_type = "function"
        else:
            self.cmd_type = "program"
        if name != '':
            self.name = name
        elif self.cmd_type == 'function':
            self.name = command.__name__
        else:
            self.name = command

        self.desc = desc
        self.output_type = output_type
        self.dirs = dirs

    def __add__(self, opt):
        field_position = len(self.form._fields) + 1
        opt.name = 'arg-{}'.format(field_position)
        if opt.name in self.form:
            print ("Field name already exist")
            raise
        else:
            self.form[opt.name] = opt.field
            new_field = self.form[opt.name]
            new_field.position = field_position
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
                if field.data and str(type(field.data)) == "<type 'str'>":
                    cmd_parts += [field.cmd_opt, field.data]
                elif field.data:
                    cmd_parts += [field.cmd_opt]
            else:
                if field.data:
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
