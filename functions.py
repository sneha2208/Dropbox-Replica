
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.ext import blobstore
from models.myuser import MyUser
from models.dir import Directory
from models.files import File
import re


def getNamesfromDir(value):
    names = list()
    for x in value:
        names.append(x.get().dirName)
    return names

def getNamesfromFile(value):
    names = list()
    for x in value:
        names.append(x.get().fileName)
    return names

def isRootDirectory(myuser):
    currentDir = myuser.currDir.get()
    if currentDir.parentDirectory == None:
        return True
    else:
        return False

#If dir already exists
def exists(i, lists):
    return i not in lists
