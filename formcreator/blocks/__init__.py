import os
from flask import render_template
from markdown import markdown

__all__ = ["DirContents", "Doc"]

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

class Doc(object):

    def __init__(self, text):
        self.text = text

    def __html__(self):
        return markdown(self.text)
