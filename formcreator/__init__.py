# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import subprocess as sp
from functools import partial
from operator import attrgetter
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

    def __init__(self, name, cmds, config='app.cfg', host='127.0.0.1', port='5000', script_url=SCRIPT_URL):
        self.name = name
        self.cmds = OrderedDict([(c.name, c) for c in cmds])
        self.app = Flask(__name__)
        self.config = os.path.abspath(config)
        # Not being used!
        self.app.config.from_pyfile(self.config)
        # Directories with contents displayed in the page
        self.dirs = []
        self.host = host
        self.port = port

        # Create the url_rules for the Forms
        for i, cmd in enumerate(self.cmds.values()):
            self.app.add_url_rule( SCRIPT_URL + (cmd.name if i > 0 else '')
                                 , cmd.name
                                 , partial(self.form, cmd.name)
                                 , methods=['GET', 'POST'])

        # Create the url_rules for serving Form's files directories
        for c in cmds:
            for d in c.dirs:
                self.app.add_url_rule( "{}{}/<path:filename>".format(SCRIPT_URL, d)
                                     , "{}-{}".format(cmd.name, d)
                                     , partial(self.serve_files, d)
                                     , methods=['GET'])
                self.dirs.append(DirContents(d))

    def run(self):
       self.app.run(debug=True, host=self.host)

    def serve_files(self, dir, filename):
        file_path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '{}')).format(dir)
        return send_from_directory(file_path, filename)

    def form(self, cmd_name):
        f = self.cmds[cmd_name]
        self.active = cmd_name
        f.stdout = ''

        if request.method == 'POST':
            f.process(request.form)
            if f.form.validate():
                f.run()

        return render_template( 'form.html'
                              , form=f.fields_list()
                              , desc=Markup(f.desc)
                              , dirs=self.dirs
                              , output_type=f.output_type
                              , output=f.stdout
                              , app=self)

class Form(object):

    def __init__(self, command, name='', desc='', output_type='pre', dirs=[]):
        self.form = wtforms.form.BaseForm(())
        self.command = command
        self.opts = []

        if callable(command):
            self.cmd_type = "function"
            self.run = self.run_function
        elif isinstance(command, basestring):
            self.cmd_type = "program"
            self.run = self.run_cmd

        if name != '':
            self.name = name
        elif self.cmd_type == 'function':
            self.name = command.__name__
        else:
            self.name = command

        self.desc = desc
        self.output_type = output_type
        self.dirs = dirs

    def fields_list(self):
        fl = []
        for o in self.opts:
            # Just wtform fields will have the field attribute
            if hasattr(o, "field"):
                fl += [o.field]
            else:
                fl += [o]
        return fl

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
                opt.field = new_field
                self.opts.append(opt)
            else:
                self.opts.append(opt)
        return self

    def process(self, form_data):
        self.form.process(form_data)

    def run_cmd(self):
        cmd_parts = [self.command]
        for opt in self.opts:
            if hasattr(opt, "field") and opt.field.data:
                cmd_parts += opt.cmd_data()
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
