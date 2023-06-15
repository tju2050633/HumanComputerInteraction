# SpeechRecognition
### **File Structure**

```
.
├── README.md
├── __pycache__
├── images
├── report
│   ├── Presentation.pptx
│   └── report.md
├── output_voice.mp3
├── user_speech.wav
├── requirements.txt
├── gpt.py
└── main.py
```



### **Usage**



**Installation**

```shell
pip install requirements.txt
```



**Fill API Keys**



Required API Keys:

- Baidu AI Product API Keys
  - APP_ID
  - API_KEY
  - SECRET_KEY

- OpenAI API Key



Visit https://ai.baidu.com . Login Baidu account, create product and get the three keys in the pruduct page. Each account can get access for 180 days freely.

Visit https://platform.openai.com . Login OpenAI account, get your API key in the profile page.



**Run**

```shell
python main.py
```



**Use**

- Enter your question in the dialog box, and click the send button to chat with AI.
- Or you can click the start recording button and speak to input your voice. Click the stop button, and the voice will be transcribed into text and placed in the input box. You can modify it and send it.
- You can enable the voice output for AI responses by clicking on the toggle button for voice answers.
- You can ask AI for image response by clicking on the toggle button for image answers, and describe your requirements by sending message.
- You can ask this application to receive emails continuously and ask AI to reply it automatically.
