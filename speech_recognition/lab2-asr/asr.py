from PyQt5 import QtWidgets, QtGui, QtCore, uic

from asrInterface import Ui_MainWindow
import sys

import speech_recognition as sr

import subprocess
import threading


class myWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(myWindow, self).__init__()
        self.myCommand = " "
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

    def start_speech_recognition(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            while True:
                try:
                    audio = r.listen(source, phrase_time_limit=10)
                    command = r.recognize_google(
                        audio, language='en')  # 识别语音指令为英语
                    print("Command:", command)
                    self.process_command(command)
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    print("Error:", e)
                    break

    def process_command(self, command):
        if "play music" in command.lower():
            # 执行打开音乐播放软件的操作
            print("Open music player")

            # 替换为你自己的音乐播放软件路径
            subprocess.Popen(
                ["/System/Applications/Music.app/Contents/MacOS/Music"])
        elif "open notebook" in command.lower():
            # 执行打开记事本的操作
            print("Open notebook")

            # 替换为你自己的记事本软件路径
            subprocess.Popen(
                ["/System/Applications/TextEdit.app/Contents/MacOS/TextEdit"])

app = QtWidgets.QApplication([])
application = myWindow()
application.show()

# 启动语音识别线程
speech_thread = threading.Thread(target=application.start_speech_recognition)
speech_thread.start()

sys.exit(app.exec_())
