import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from datetime import datetime
import os

#Actually we didn't need this class
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/upload", UploadHandler)
        ]
        settings = {
'template_path': 'static/templates',
'static_path': 'static',
"xsrf_cookies": False
}
        tornado.web.Application.__init__(self, handlers, **settings)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class UploadHandler(tornado.web.RequestHandler):
    def post(self):
        import time
        file1 = self.request.files['file'][0]
        original_fname = file1['filename']
        # filename, file_extension = os.path.splitext(original_fname)
        # new_fname = "audio-"+str(datetime.today().strftime('%d-%b-%Y'))+file_extension
        # os.rename(original_fname, new_fname)
        output_file = open("uploads/" + original_fname, 'wb')
        output_file.write(file1['body'])
        
        self.finish("file " + original_fname + " is uploaded")
        #self.redirect("/stream/[0-9Xx\-]+)")






if __name__ == "__main__":
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()