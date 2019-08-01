from google.appengine.ext import ndb
class MyUser(ndb.Model):
    rootDir = ndb.KeyProperty()   #Root directory will be stored here
    currDir = ndb.KeyProperty()   # Current Dir of the user 
