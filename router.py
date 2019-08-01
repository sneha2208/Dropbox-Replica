import webapp2
from webapp2 import Route


app = webapp2.WSGIApplication([
    Route('/', handler = 'main.MainPage'),
    Route('/upload', handler = 'fileHandler.FileUpload'),
    Route('/download', handler = 'fileHandler.FileRead'),
],debug=True)
