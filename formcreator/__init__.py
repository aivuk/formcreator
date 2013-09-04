# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import subprocess as sp
from functools import partial
import os

from flask import Flask, request, render_template, send_from_directory, Markup
import wtforms
from ordereddict import OrderedDict
from markdown import markdown

from fields import *
from blocks import *

SCRIPT_URL = '/'
SCRIPT_PATH = '.'

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

class Form(object):

    def __init__(self, command, name='', desc='', output_type='pre', dirs=[]):
        self.form = wtforms.form.BaseForm(())
        self.command = command
        self.opts = []
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
            if hasattr(opt, 'field'):
                self.form[opt.name] = opt.field
                new_field = self.form[opt.name]
                new_field.position = field_position
                new_field.data = opt.default or ''
                if hasattr(opt, "cmd_opt"):
                    new_field.cmd_opt = opt.cmd_opt
                self.opts.append(new_field)
            else:
                self.opts.append(opt)
        return self

    def list_form(self):
        fs = list(self.form)
        fs.sort(key = lambda x: x.position)
        return self.opts

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
