import webapp2
import jinja2
import os
import logging
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from google.appengine.api import users
from models.myuser import MyUser
from models.dir import Directory
from models.files import File
import functions
import re

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class FileUpload(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        uploads = self.get_uploads()
        for file in uploads:
            filename = blobstore.BlobInfo(file.key()).filename

            user = users.get_current_user()
            my_user_key = ndb.Key(MyUser, user.user_id())
            my_user = my_user_key.get()

            currDirObj = my_user.currDir.get()
            path = ''
            if functions.isRootDirectory(my_user):
                path = currDirObj.dirPath + filename
            else:
                path = currDirObj.dirPath + '/' + filename

            file_id = my_user.key.id() + path
            file_key = ndb.Key(File, file_id)
            logging.info(file_id)
            if functions.exists(file_key, currDirObj.files):
                file_object = File(id=file_id)
                file_object.fileName = filename
                file_object.data = file.key()
                file_object.put()

                currDirObj.files.append(file_key)
                currDirObj.put()

            else:
                # Delete uploaded file from the blobstore
                blobstore.delete(file.key())
                logging.debug("File with the same name already exists!")

        self.redirect('/')

class FileRead(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        filename = self.request.get('file_name')
        user = users.get_current_user()
        my_user_key = ndb.Key(MyUser, user.user_id())
        my_user = my_user_key.get()
        parDirObj =  my_user.currDir.get()
        path = ''
        if functions.isRootDirectory(my_user):
            path = parDirObj.dirPath + filename
        else:
            path = parDirObj.dirPath + '/' + filename
        file_id = my_user.key.id() + path
        file_key = ndb.Key(File, file_id)
        file_object = file_key.get()
        self.send_blob(file_object.data,save_as=file_object.fileName)
