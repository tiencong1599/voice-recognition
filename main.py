from re import split
import tornado.httpserver, tornado.ioloop, tornado.options, tornado.web, os.path, random, string
from datetime import datetime
import os, io, sys
from google.cloud import speech
import tornado.httpclient
import tornado.gen
import urllib
import json
import env
from pydub import AudioSegment

sys.path.append("../env-exe/")

credential_path = "key.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

#Actually we didn't need this class
class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/uploads", UploadHandler)
            
            
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
        #upload Audio
        ori_fname = uploadAudio(self.request)
        # convert any type of audio to wav type
        wav_audio = cvtAudio(ori_fname)
        os.remove("uploads/"+ori_fname)
        #streaming audio
        responses = streamAudio(wav_audio)
        for result in responses.results:
            self.write("""
            <div>
                <p>%s</p>
            </div>
            """ % (result.alternatives[0].transcript))
            
        
def uploadAudio(request):
    file1 = request.files['file'][0]
    original_fname = file1['filename']
    # filename, file_extension = os.path.splitext(original_fname)
    # new_fname = "audio-"+str(datetime.today().strftime('%d-%b-%Y'))+file_extension
    # os.rename(original_fname, new_fname)
    output_file = open("uploads/" + original_fname, 'wb')
    output_file.write(file1['body'])
    return original_fname

def cvtAudio(fname):
    ori_fname, ext = os.path.splitext(fname)
    sound = AudioSegment.from_file(os.path.join("uploads/", fname),format=ext.strip("."))
    output = "uploads/" + ori_fname +".wav"
    sound.export(output, format="wav")
    return output


def streamAudio(audioUrl):
    client = speech.SpeechClient()

    # Full path of the audio file, Replace with your file name
    file_name = audioUrl

    #Loads the audio file into memory
    with io.open(file_name, "rb") as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        audio_channel_count=2,
        sample_rate_hertz=48000,
        language_code="vi-VN",
    )

    # Sends the request to google to transcribe the audio
    response =  client.recognize(request={"config": config, "audio": audio})
    
    return response
    
        
        



if __name__ == "__main__":
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()