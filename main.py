import webapp2
import jinja2
import os
import logging
from google.appengine.ext import blobstore
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

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'

        user = users.get_current_user()
        if user == None:
            logging.info("user")
            logging.info(user)
            rendered_template = {
            'url' : users.create_login_url(self.request.uri)
            }
            template = JINJA_ENVIRONMENT.get_template('templates/login.html')
            self.response.write(template.render(rendered_template))
            return
        else:
            myuser_key = ndb.Key(MyUser, user.user_id())
            myuser = myuser_key.get()
            logging.info("my user")
            logging.info(myuser)

            if myuser == None:
                myuser = MyUser(id=user.user_id())
                #Adding the root directory
                directory_id = myuser.key.id() + '/'
                directory = Directory(id=directory_id)

                directory.parentDirectory = None
                directory.dirName = 'root'
                directory.dirPath = '/'
                directory.put()

                myuser.rootDir = directory.key
                myuser.put()
                myuser.currDir = ndb.Key(Directory, myuser.key.id() + '/')
                myuser.put()

                logging.info("Details")
                logging.info(myuser)
                logging.info(myuser.currDir)
                logging.info(myuser.rootDir)
                logging.info("My user after ")
                logging.info(myuser.currDir.get())

            #Navigating the directory

            directory_name = self.request.get('directory_name')
            if directory_name != '':
                # myuser_key = ndb.Key('MyUser', user.user_id())
                # myuser = myuser_key.get()
                parent_dir_obj = myuser.currDir.get()
                directory_id =''
                if functions.isRootDirectory(myuser):
                    directory_id = myuser.key.id() + parent_dir_obj.dirPath + directory_name
                else:
                    directory_id = myuser.key.id() + parent_dir_obj.dirPath + '/' + directory_name
                directory_key = ndb.Key(Directory, directory_id)
                myuser.currDir = directory_key
                myuser.put()
                self.redirect('/')

            #Getting current paths files and directories
            currPathDir = myuser.currDir.get()
            logging.info("curr path")
            logging.info(currPathDir)
            dirCurrPath = currPathDir.subDir
            filesCurrPath = currPathDir.files

            #Sorting of dirs and files
            dirCurrPath = sorted(dirCurrPath, key=lambda element: element.get().dirName.lower())
            filesCurrPath = sorted(filesCurrPath, key=lambda element: element.get().fileName.lower())

            #  file and dir names extract

            dirCurrPath = functions.getNamesfromDir(dirCurrPath)
            filesCurrPath = functions.getNamesfromFile(filesCurrPath)

            logging.info("sub dir")
            logging.info(dirCurrPath)

            total_no_of_files = len(currPathDir.files)
            total_directories = len(currPathDir.subDir)

            # Each File size
            file_size = list()
            for f in currPathDir.files:
                file_size.append(blobstore.BlobInfo(f.get().data).size)

            # Type of the Files
            file_type = list()
            for f in currPathDir.files:
                file_type.append(blobstore.BlobInfo(f.get().data).content_type)

            # Creation date of the file
            fileCreationDate = list()
            for f in currPathDir.files:
                fileCreationDate.append(blobstore.BlobInfo(f.get().data).creation.strftime("%d %B %Y, %I:%M%p"))

            # Total size of the files in a Directory
            totalCount = 0;
            for f in currPathDir.files:
                totalCount += blobstore.BlobInfo(f.get().data).size

            logging.info('filesCurrPath')
            logging.info(len(filesCurrPath))
            rendered_template = {
                'url': users.create_logout_url(self.request.uri),
                'user': users.get_current_user(),
                'directories': dirCurrPath,
                'files': filesCurrPath,
                'current_path': currPathDir.dirPath,
                'is_not_in_root': not functions.isRootDirectory(myuser),
                'total_no_of_files' : total_no_of_files,
                'total_directories' : total_directories,
                'file_size' : file_size,
                'file_type' : file_type,
                'length' : len(filesCurrPath),
                'fileCreationDate' :fileCreationDate,
                'totalCount' : totalCount,
                'upload_url': blobstore.create_upload_url('/upload')
            }

            template = JINJA_ENVIRONMENT.get_template('templates/main.html')
            self.response.write(template.render(rendered_template))


    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        button = self.request.get('button')
        if button == 'Add':
            directory_name = self.request.get('value')
            directory_name = re.sub(r'[/;]', '', directory_name).lstrip()
            if not (directory_name is None or directory_name == ''):
                user = users.get_current_user()
                my_user_key = ndb.Key(MyUser, user.user_id())
                my_user = my_user_key.get()
                logging.info("my user key in post method")
                logging.info(my_user)
                parent_dir_obj = my_user.currDir.get()

                path = ''
                if functions.isRootDirectory(my_user):
                    path = parent_dir_obj.dirPath + directory_name
                else:
                    path = parent_dir_obj.dirPath + '/' + directory_name

                directory_id = my_user.key.id() + path
                directory = Directory(id=directory_id)
                logging.info("dir ID")
                logging.info(directory_id)
                logging.info(parent_dir_obj.subDir)
                # If directory already exists
                if functions.exists(directory.key, parent_dir_obj.subDir):
                    parent_dir_obj.subDir.append(directory.key)
                    parent_dir_obj.put()
                    logging.info("parent_dir_obj")
                    logging.info(parent_dir_obj)
                    # Saving all params of dir to db
                    directory.parentDirectory = my_user.currDir
                    directory.dirName = directory_name
                    directory.dirPath = path
                    directory.put()
                self.redirect('/')

        elif button == 'Delete':
            name = self.request.get('name')
            type = self.request.get('fType')

            if type == 'file':
                user = users.get_current_user()
                my_user_key = ndb.Key(MyUser, user.user_id())
                my_user = my_user_key.get()
                parent_dir_obj = my_user.currDir.get()
                path = ''
                if functions.isRootDirectory(my_user):
                    path = parent_dir_obj.dirPath + name
                else:
                    path = parent_dir_obj.dirPath + '/' + name
                file_id = my_user.key.id() + path
                file_key = ndb.Key(File, file_id)
                parent_dir_obj.files.remove(file_key)
                parent_dir_obj.put()
                blobObject = file_key.get().data
                blobstore.delete(blobObject)
                file_key.delete()



            elif type == 'directory':
                user = users.get_current_user()
                my_user_key = ndb.Key(MyUser, user.user_id())
                my_user = my_user_key.get()

                parent_dir_obj = my_user.currDir.get()

                path = ''
                if functions.isRootDirectory(my_user):
                    path = parent_dir_obj.dirPath + name
                else:
                    path = parent_dir_obj.dirPath + '/' + name

                directory_id = my_user.key.id() + path
                directory_key = ndb.Key(Directory, directory_id)
                directory_object = directory_key.get()

                if not directory_object.files and not directory_object.subDir:
                    #Delete all the references
                    parent_dir_obj.subDir.remove(directory_key)
                    parent_dir_obj.put()

                    # Delete directory from datastore
                    directory_key.delete()


            self.redirect('/')

        elif button == 'Up':
            user = users.get_current_user()
            my_user_key = ndb.Key(MyUser, user.user_id())
            my_user = my_user_key.get()
            if not functions.isRootDirectory(my_user):
                parent_dir_obj = my_user.currDir.get().parentDirectory
                my_user.currDir = parent_dir_obj
                my_user.put()
            self.redirect('/')

        elif button == 'Home':
            user = users.get_current_user()
            my_user_key = ndb.Key(MyUser, user.user_id())
            my_user = my_user_key.get()
            my_user.currDir = ndb.Key(Directory, my_user.key.id() + '/')
            my_user.put()
            self.redirect('/')
