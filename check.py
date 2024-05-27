from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QDialog, QApplication, QPushButton
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QMovie
import sys
import time
import speech_recognition as sr
from openai import OpenAI
# from elevenlabs import play
from test_tts import tts_run


class Audio(QThread):
    def __init__(self, audio_text):
        super().__init__()
        self.audio_text = audio_text

    def run(self):
        tts_run(self.audio_text, "[happy]")


class ChatGPTThread(QThread):
    def __init__(self, chatgpt, prompt):
        super().__init__()
        self.chatgpt = chatgpt
        self.prompt = prompt
        self.response = ""
        self.tmp = []
        self.tmp2 = ""

    def run(self):
        response = self.chatgpt.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                    "content": "I am an intelligent assistant. And my mission is to provide helpful information. Your answer will have an emotion displayed at the end, like this example [happy]. You will have 4 emotion is happy, sad, scared, angry. Please place the end sentence dot before the emotion like: hello. [happy]"},
                {"role": "user", "content": self.prompt}
            ]
        )
        self.response = str(response.choices[0].message.content)
        return self.response


class myThread(QThread):
    # Define a custom signal to emit the GIF filename
    gifFilename = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.chatgpt_thread = ChatGPTThread
        self.recognizer = sr.Recognizer()
        self.chatgpt = OpenAI(api_key="sk-J3vEsFqZXfrV6UtUPCVTYYgfTzUdAr7lrqmhAxO3xDkGOLyL",
                              base_url="https://api.chatanywhere.tech/v1")
        self.audio_thread = Audio
        self.dict = {
            "[happy]": "face/happy.gif",
            "[sad]": "face/sad.gif",
            "[angry]": "face/angry.gif",
            "[scared]": "face/scared.gif"
        }
        # self.happy_gif = QMovie('face/happy.gif')  # Pre-load the happy GIF
        # Pre-load the goodbye GIF (assuming you have one)
        # self.goodbye_gif = QMovie('face/goodbye.gif')

    def run(self):
        result = self.chatgpt_thread(
            prompt="Make a polite and short greeting", chatgpt=self.chatgpt).run()
        tmp = result.split()
        tmp2 = tmp[-1]
        result2 = result.replace(tmp2, "")
        self.audio_thread(result2).run()
        print("Bot:", result2)
        while True:
            try:
                with sr.Microphone() as source2:
                    self.gifFilename.emit('face/hearing.gif')
                    self.recognizer.adjust_for_ambient_noise(
                        source2, duration=0.2)
                    audio2 = self.recognizer.listen(source2)
                    MyText = self.recognizer.recognize_google(audio2).lower()
                    print("User:", MyText)

                    if "bye" not in MyText:
                        result = self.chatgpt_thread(
                            prompt=MyText, chatgpt=self.chatgpt).run()
                        tmp = result.split()
                        tmp2 = tmp[-1]
                        result2 = result.replace(tmp2, "")
                        self.gifFilename.emit(self.dict[tmp2])
                        self.audio_thread(result2).run()
                        print("Bot:", result2)
                        # Emit signal for happy GIF
                    else:
                        result = self.chatgpt_thread(
                            prompt="Make an awesome goodbye", chatgpt=self.chatgpt).run()
                        tmp = result.split()
                        tmp2 = tmp[-1]
                        result2 = result.replace(tmp2, "")
                        self.gifFilename.emit(self.dict[tmp2])
                        self.audio_thread(result2).run()
                        print("Bot:", result2)
                        # Emit signal for goodbye GIF
                        sys.exit()
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))
            except sr.UnknownValueError:
                self.audio_thread(audio_text="Say it again please!").run()
                print("Bot: Say it again please!")


class Main(QWidget):

    def __init__(self):
        super().__init__()

        print('Thread is to be called here...')
        self.load()
        print('Thread has been called...')
        sys.exit()

    def load(self):
        # setup dialog
        dialog = QDialog(self)
        vbox = QVBoxLayout()
        self.lbl = QLabel(self)

        # Set the initial GIF (can be happy or another default)
        self.movie = QMovie('face/happy.gif')  # Create a movie object
        self.lbl.setMovie(self.movie)
        self.movie.start()  # Start the initial GIF playback

        vbox.addWidget(self.lbl)
        dialog.setLayout(vbox)
        dialog.setFixedSize(1535, 800)

        # Setup thread
        thread = myThread()

        # Connect the thread's signal to update the GIF in the GUI
        thread.gifFilename.connect(self.update_gif)

        thread.start()
        dialog.exec()

    def update_gif(self, filename):
        # Function to update the GIF based on the received filename
        self.movie.stop()  # Stop the current GIF playback
        # Create a new movie object with the received filename
        self.movie = QMovie(filename)
        self.lbl.setMovie(self.movie)
        self.movie.start()  # Start the new GIF playback


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    app.exec()
