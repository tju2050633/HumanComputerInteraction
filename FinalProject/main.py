from gpt import chat
import threading
import pyaudio
import wave
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTextEdit, QCheckBox, QInputDialog
from aip import AipSpeech
from qt_material import apply_stylesheet
import imaplib
import sys
import time
import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import decode_header
from email.header import Header
import re
import playsound
from pydub import AudioSegment
from pydub.playback import play

APP_ID = '34736598'
API_KEY = 'bg5lT5hq6U7jCPNQzBtIy3V3'
SECRET_KEY = 'Sau2E3pOUuIMPTpetpn6hWBuKoeyZL14'

EMAIL_NAME = None
EMAIL_PASSWORD = None

emailRecipient = None
gpt3Reply = None
lastEmailContent = None

client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.filename = "./user_speech.wav"
        self.client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
        self.dev_pid = 1537  # 默认普通话
        self.recording = False
        self.sampleRate = 16000
        self.audioType = 'wav'

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(450, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        # 图片
        image_path = "./images/waiting.gif"
        movie = QtGui.QMovie(image_path)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setFixedSize(288, 310)
        self.label.setMovie(movie)
        self.verticalLayout.addWidget(self.label)
        movie.start()
        scaled_size = QtCore.QSize(288, 310)
        movie.setScaledSize(scaled_size)
        self.current_movie = movie  # 当前显示的 QMovie 对象

        self.horizontalLayout0 = QtWidgets.QHBoxLayout()
        self.horizontalLayout0.setObjectName("horizontalLayout0")
        self.horizontalLayout0.addWidget(self.label)
        self.verticalLayout.addLayout(self.horizontalLayout0)

        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout.addWidget(self.lineEdit)

        self.startRecordingButton = QtWidgets.QPushButton(
            "开始录制", self.centralwidget)
        self.startRecordingButton.setObjectName("startRecordingButton")
        # self.verticalLayout.addWidget(self.startRecordingButton)

        self.stopRecordingButton = QtWidgets.QPushButton(
            "结束录制", self.centralwidget)
        self.stopRecordingButton.setObjectName("stopRecordingButton")
        # self.verticalLayout.addWidget(self.stopRecordingButton)

        # 组合录制按钮
        self.horizontalLayout1 = QtWidgets.QHBoxLayout()
        self.horizontalLayout1.setObjectName("horizontalLayout1")
        self.horizontalLayout1.addWidget(self.startRecordingButton)
        self.horizontalLayout1.addWidget(self.stopRecordingButton)
        self.verticalLayout.addLayout(self.horizontalLayout1)

        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        # self.verticalLayout.addWidget(self.pushButton)

        self.sendEmailButton = QtWidgets.QPushButton(
            "发送邮件", self.centralwidget)
        self.sendEmailButton.setObjectName("sendEmailButton")
        # self.verticalLayout.addWidget(self.sendEmailButton)

        # 组合send和发送邮件按钮
        self.horizontalLayout2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout2.setObjectName("horizontalLayout2")
        self.horizontalLayout2.addWidget(self.pushButton)
        self.horizontalLayout2.addWidget(self.sendEmailButton)
        self.verticalLayout.addLayout(self.horizontalLayout2)

        self.checkBox = QCheckBox("持续接收邮件", self.centralwidget)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)

        self.checkText = QCheckBox("是否回复图片", self.centralwidget)
        self.checkText.setObjectName("checkText")
        self.verticalLayout.addWidget(self.checkText)

        self.checkVoice = QCheckBox("是否用语音回答", self.centralwidget)
        self.checkVoice.setObjectName("checkVoice")
        self.verticalLayout.addWidget(self.checkVoice)

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # connect buttons to their respective functions
        self.startRecordingButton.clicked.connect(self.start_recording)
        self.stopRecordingButton.clicked.connect(self.stop_recording)
        self.pushButton.clicked.connect(self.processInput)
        self.sendEmailButton.clicked.connect(self.send_email)

        # Initialize the AipSpeech object
        self.aipSpeech = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

        # Create a thread to check for new emails
        self.check_email_thread = threading.Thread(target=self.check_new_email)
        # self.check_email_thread.start()

        self.checkBox.stateChanged.connect(self.toggle_email_credentials)

    def toggle_email_credentials(self, state):
        global EMAIL_NAME, EMAIL_PASSWORD
        if state == QtCore.Qt.Checked:
            if EMAIL_NAME is None or EMAIL_PASSWORD is None:
                # Prompt the user to enter email credentials
                email_dialog = QtWidgets.QDialog()
                email_dialog.setWindowTitle("Email Credentials")

                form_layout = QtWidgets.QFormLayout(email_dialog)
                email_name_input = QtWidgets.QLineEdit()
                email_password_input = QtWidgets.QLineEdit()
                email_password_input.setEchoMode(QtWidgets.QLineEdit.Password)
                form_layout.addRow("Email Name:", email_name_input)
                form_layout.addRow("Email Password:", email_password_input)

                button_box = QtWidgets.QDialogButtonBox(
                    QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
                button_box.accepted.connect(email_dialog.accept)
                button_box.rejected.connect(email_dialog.reject)
                form_layout.addRow(button_box)

                if email_dialog.exec_() == QtWidgets.QDialog.Accepted:
                    EMAIL_NAME = email_name_input.text()
                    EMAIL_PASSWORD = email_password_input.text()

                if EMAIL_NAME is None or EMAIL_PASSWORD is None:
                    # User canceled the input or did not provide both credentials
                    self.checkBox.setChecked(False)

            self.check_email_thread.start()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(
            "MainWindow", "SpeakAI: a smart assistant program"))
        self.pushButton.setText(_translate("MainWindow", "Send"))

    def processInput(self):
        userInput = self.lineEdit.text()
        self.textBrowser.append("You: " + userInput)
        self.lineEdit.clear()

        # Create a thread to send the user input to GPT-3 API
        # to avoid blocking the GUI thread
        thread = threading.Thread(target=self.chatThread, args=(userInput,))
        thread.start()

    def start_recording(self):
        self.update_gif("./images/listening.gif")

        if self.recording:
            self.textBrowser.append("正在录制中...")
            return

        self.textBrowser.append("开始录制语音...")
        self.recording = True

        # Create a thread to start recording
        thread = threading.Thread(target=self.record)
        thread.start()

    def stop_recording(self):
        self.update_gif("./images/waiting.gif")

        if not self.recording:
            self.textBrowser.append("没有在录制中...")
            return

        self.textBrowser.append("结束录制语音...")
        self.recording = False

    def record(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000

        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        frames = []

        while self.recording:
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Convert recorded audio to text using AipSpeech
        result = self.recognition(self.aipSpeech, b''.join(frames))
        if result['err_no'] == 0:
            userInput = result['result'][0]
            self.lineEdit.setText(userInput)
            self.textBrowser.append("Voice Input: " + userInput)
        else:
            self.textBrowser.append(
                'Recognition Error, Error number is ' + str(result['err_no']))

    def recognition(self, aipSpeech, audio_data):
        result = aipSpeech.asr(audio_data, 'pcm', 16000, {
            'dev_pid': self.dev_pid,
        })

        return result

    def chatThread(self, userInput):
        # Here, replace with the actual code to send userInput to GPT-3 API
        # and get the response. Now it is just an echo.
        chatMode = not (self.checkText.isChecked())
        enableVoice = self.checkVoice.isChecked()
        gpt3Response = chat(userInput, chatMode)

        # Play the response audio
        thread = threading.Thread(
            target=self.playAudio, args=(gpt3Response, enableVoice))
        thread.start()

        # Display the response in the text browser
        self.textBrowser.append("GPT-3: " + gpt3Response)

        # 设置全局变量存储GPT的回复
        global gpt3Reply
        gpt3Reply = gpt3Response

    def playAudio(self, gpt3Response, enableVoice):
        if enableVoice:
            result = client.synthesis(gpt3Response, 'zh', 1, {  # zh代表中文
                'vol': 5,
                'per': 4,  # 0为女声，1为男声，3为情感合成-度逍遥，4为情感合成-度丫丫
                'spd': 6,  # 语速，取值0-9，默认为5中语速
                'pit': 5,  # 音调，取值0-9，默认为5中语调
                'aue': 3,  # 下载的文件格式支持pcm、wav、mp3，不传则返回pcm
            })
            if not isinstance(result, dict):
                
                output_voice_file_name = './output_voice.mp3'
                with open(output_voice_file_name, 'wb') as f:
                    print("正在保存音频文件")
                    f.write(result)

                    # 播放语音
                    self.update_gif("./images/speaking.gif")
                    if sys.platform.startswith('darwin'):
                        playsound.playsound(output_voice_file_name)
                    elif sys.platform.startswith('win32'):
                        audio = AudioSegment.from_file(
                            output_voice_file_name, format='mp3')
                        play(audio)
                    else:
                        pass
            else:
                print("语音合成失败")

    def check_new_email(self):
        # 连接到邮箱服务器
        try:
            mail = imaplib.IMAP4_SSL("imap.qq.com")
            print("已连接到邮箱服务器")
        except:
            print("无法连接到邮箱服务器")
            exit(1)

        # 登录邮箱账户
        try:
            mail.login(EMAIL_NAME, EMAIL_PASSWORD)
            print("已登录到邮箱账户")
        except:
            print("无法登录到邮箱账户")
            exit(1)

        # 选择收件箱文件夹
        mail.select("INBOX")

        while True:
            # 搜索所有邮件
            status, response = mail.search(None, "ALL")
            emails = response[0].split()

            if emails:
                email_id = emails[-1]
                status, email_data = mail.fetch(email_id, "(RFC822)")

                # 解析邮件内容
                for response_part in email_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg["subject"]
                        subject = decode_header(subject)[0][0]
                        subject = subject.decode("utf-8")  # 转换为字符串
                        body = ""

                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                if content_type == "text/plain":
                                    body = part.get_payload(
                                        decode=True).decode()
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode()

                        # 全局变量存储收件人和邮件内容
                        global emailRecipient, lastEmailContent
                        # 提取邮件地址
                        recipient_match = re.search(r"<([^>]+)>", msg["From"])
                        if recipient_match:
                            recipient_email = recipient_match.group(1)
                        else:
                            recipient_email = msg["From"]

                        # 将邮件内容填写到输入框
                        if self.checkBox.isChecked() and body != lastEmailContent:
                            text_to_fill = "[回复当前邮件]:"+f"Subject: {subject}\n\n{body}"
                            QtCore.QMetaObject.invokeMethod(self.lineEdit, "setText", QtCore.Qt.QueuedConnection,
                                                            QtCore.Q_ARG(str, text_to_fill))

                            emailRecipient = recipient_email
                            lastEmailContent = body
            else:
                print("未找到邮件")

            time.sleep(5)  # 每隔5秒检查一次收件箱

    def send_email(self):
        global emailRecipient, gpt3Reply
        if emailRecipient and gpt3Reply:
            # 用于发送邮件的邮箱。修改成自己的邮箱
            sender_email_address = EMAIL_NAME
            # 用于发送邮件的邮箱的密码。修改成自己的邮箱的密码
            sender_email_password = EMAIL_PASSWORD
            # 用于发送邮件的邮箱的smtp服务器，也可以直接是IP地址
            # 修改成自己邮箱的sntp服务器地址；qq邮箱不需要修改此值
            smtp_server_host = "smtp.qq.com"
            # 修改成自己邮箱的sntp服务器监听的端口；qq邮箱不需要修改此值
            smtp_server_port = 465
            # 要发往的邮箱
            receiver_email = emailRecipient
            # 要发送的邮件主题
            message_subject = "GPT-3 reply"
            # 要发送的邮件内容
            message_context = gpt3Reply

            # 邮件对象，用于构建邮件
            # 如果要发送html，请将plain改为html
            message = MIMEText(message_context, 'plain', 'utf-8')
            # 设置发件人（声称的）
            # message["From"] = Header(sender_email_address, "utf-8")
            message["From"] = sender_email_address
            
            # 设置收件人（声称的）
            message["To"] = Header(receiver_email, "utf-8")
            # 设置邮件主题
            message["Subject"] = Header(message_subject,"utf-8")

            # 连接smtp服务器。如果没有使用SSL，将SMTP_SSL()改成SMTP()即可其他都不需要做改动
            email_client = smtplib.SMTP_SSL(smtp_server_host, smtp_server_port)
            try:
                # 验证邮箱及密码是否正确
                email_client.login(sender_email_address, sender_email_password)
                print("smtp----login success, now will send an email to {receiver_email}")
            except:
                print("smtp----sorry, username or password not correct or another problem occur")
            else:
                # 发送邮件
                email_client.sendmail(sender_email_address, receiver_email, message.as_string())
                print(f"smtp----send email to {receiver_email} finish")
                emailRecipient = None
                gpt3Reply = None

            finally:
                # 关闭连接
                email_client.close()
                
        else:
            self.textBrowser.append("没有可发送的邮件或回复内容")

    def update_gif(self, new_image_path):
        print("更新gif图片" + new_image_path)
        # 更新gif图片
        new_movie = QtGui.QMovie(new_image_path)
        scaled_size = QtCore.QSize(288, 310)
        new_movie.setScaledSize(scaled_size)
        self.label.setMovie(new_movie)
        self.current_movie.stop()  # 停止当前显示的 QMovie
        self.current_movie = new_movie  # 更新当前显示的 QMovie 对象
        new_movie.start()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # apply material design style
    apply_stylesheet(app, theme='dark_blue.xml')

    MainWindow.show()
    sys.exit(app.exec_())
