import os
import wtforms
from flask import render_template, request

__all__ = ["SelectFile", "Boolean", "Text", "TextArea", "File", "Integer", "Float", "Decimal"]

def makeOpt(field_type):
    class Opt(object):

        def __init__(self, label='', description='', name='', default='', cmd_opt=None, **kwargs):
            self.name = name
            self.default = default
            self.field = field_type(label=label, description=description, **kwargs)
            if cmd_opt:
                self.cmd_opt = cmd_opt

        def cmd_data(self):
            if hasattr(self.field, "cmd_data"):
                return self.field.cmd_data()
            else:
                if hasattr(self, 'cmd_opt'):
                    return [self.cmd_opt, str(self.field.data)]
                else:
                    return [str(self.field.data)]

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

class BooleanField(wtforms.BooleanField):
    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)

    def cmd_data(self):
        if self.data:
            return [self.cmd_opt]

Boolean = makeOpt(BooleanField)
SelectFile = makeOpt(SelectFileField)
Text = makeOpt(wtforms.TextField)
TextArea =  makeOpt(wtforms.TextAreaField)
File = makeOpt(Upload)
Integer = makeOpt(wtforms.IntegerField)
Float = makeOpt(wtforms.FloatField)
Decimal = makeOpt(wtforms.DecimalField)
