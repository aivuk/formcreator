# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import subprocess as sp
from functools import partial
import hashlib
import os

from flask import Flask, request, render_template, send_from_directory, Markup, flash, redirect
from flask_login import LoginManager, login_required, login_user, logout_user
import wtforms
from collections import OrderedDict
from markdown import markdown

from .fields import *
from .blocks import *
from .models import db, User

SCRIPT_URL = '/'
SCRIPT_PATH = '.'

class DefaultConfig(object):
    SECRET_KEY = 'Isthisthereallife?Isthisjustfantasy?Caughtinalandslide'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/formcreator.db'

class MainApp(object):

    def __init__(self, name, cmds, config='app.cfg', host='127.0.0.1', port=5000, script_url=SCRIPT_URL, not_public=False):
        self.name = name
        self.cmds = OrderedDict([(c.name, c) for c in cmds])
        self.app = Flask(__name__)
        self.config = os.path.abspath(config)
        self.app.config.from_object('formcreator.DefaultConfig')
        self.app.config.from_pyfile(self.config, silent=True)
        # Directories with contents displayed in the page
        self.dirs = []
        self.host = host
        self.port = port

        if not_public:
            self.init_user_mgmt()

            # Create hte LoginManager
            self.login_manager = LoginManager()
            self.login_manager.init_app(self.app)
            self.login_manager.login_view = "login"
            self.login_manager.user_loader(self.load_user)

        # Create the url_rules for the Forms
        for i, cmd in enumerate(self.cmds.values()):
            if not_public:
                url_function = partial(login_required(self.form), cmd.name)
            else:
                url_function = partial(self.form, cmd.name)

            self.app.add_url_rule( SCRIPT_URL + (cmd.name if i > 0 else '')
                                 , cmd.name
                                 , url_function
                                 , methods=['GET', 'POST'])

        # Create the url_rules for serving Form's files directories
        for c in cmds:
            for d in c.dirs:
                self.app.add_url_rule( "{}{}/<path:filename>".format(SCRIPT_URL, d)
                                     , "{}-{}".format(cmd.name, d)
                                     , partial(self.serve_files, d)
                                     , methods=['GET'])
                self.dirs.append(DirContents(d))

        if not_public:
            self.app.add_url_rule("/login", "login", self.login, methods=['POST', 'GET'])
            self.app.add_url_rule("/logout", "logout", self.logout, methods=['POST', 'GET'])

    def init_user_mgmt(self):
        """This initializes the default user management method.

        To implement your own user management, you need to do the following:

        1. Implement a flask-compatible User class:
            - see https://flask-login.readthedocs.io/en/latest/#your-user-class
        2. Override the following MainApp methods:
          1. init_user_mgmt()  -- This hook is invoked whenever not_public == True
          2. load_user()       -- Must return a User instance based on id (per Flask)
          3. do_user_login()   -- Must return a User instance based on login/password

        """
        self.not_public = True
        # Create de database
        self.db = db
        self.app.test_request_context().push()
        self.db.init_app(self.app)
        self.db.create_all()
        # Create admin user if doesn't exist
        admin_user = User.query.get(1)
        if not admin_user:
            admin_user = User("admin", "admin", is_admin=True)
            self.db.session.add(admin_user)
            self.db.session.commit()

    def logout(self):
        logout_user()
        return redirect("/")

    def do_user_login(self, login, password):
        """This is the default user login implementation. Override if doing your own."""
        password = hashlib.sha256(password.encode('utf8')).hexdigest()
        u = User.query.filter(User.username == login,
                              User.password == password).one()
        return u

    def login(self):

        login_form = wtforms.form.BaseForm(())
        login_form['username'] = wtforms.TextField("Username")
        login_form['password'] = wtforms.PasswordField("Password")
        login_form['username'].data = ''

        if request.method == 'POST':
            login_form.process(request.form)
            if login_form.validate():
                # login and validate the user...
                login = login_form['username'].data
                password = login_form['password'].data
                try:
                    u = self.do_user_login(login, password)
                    login_user(u)
                    flash("Logged in successfully.")
                    return redirect(request.args.get("next") or "/")
                except:
                    flash("Username or password incorrect, try again.")

            return redirect("/login")

        return render_template("login.html", form=login_form, app=self)

    def load_user(self, userid):
        user = User.query.get(userid)
        return user

    def run(self, *args, **kwargs):
       self.app.run(debug=True, *args, **kwargs)

    def serve_files(self, dir, filename):
        file_path = os.path.abspath(os.path.join(os.getcwd(), '{}')).format(dir)
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
                              , inline=f.inline
                              , app=self)

class Form(object):

    def __init__(self, command, name='', desc='', output_type='pre', dirs=[], inline=False):
        self.form = wtforms.form.BaseForm(())
        self.command = command
        self.opts = []
        self.inline = inline

        if callable(command):
            self.cmd_type = "function"
            self.run = self.run_function
        elif type(command) is str:
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
            raise RuntimeError("Field name already exist")
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
        try:
            cmd = sp.Popen(cmd_parts, stdout=sp.PIPE, stderr=sp.STDOUT).communicate()
        except OSError:
            self.stdout = "Command '{}' not found".format(cmd_parts[0])
            return
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
