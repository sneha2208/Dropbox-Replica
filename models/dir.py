from google.appengine.ext import ndb
class Directory(ndb.Model):
    dirName = ndb.StringProperty()
    dirPath = ndb.StringProperty()
    parentDirectory = ndb.KeyProperty()
    subDir = ndb.KeyProperty(repeated=True)
    files = ndb.KeyProperty(repeated=True)
