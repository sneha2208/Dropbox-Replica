from google.appengine.ext import ndb
class File(ndb.Model):
    fileName = ndb.StringProperty()
    data = ndb.BlobKeyProperty() #Data will be stored here
