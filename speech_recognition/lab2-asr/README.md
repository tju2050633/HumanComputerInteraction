# 用户交互技术作业二：语音识别应用程序

## 功能介绍

实现了应用程序界面上的2个语音识别功能：
- 用户通过声音输入“play music”，应用程序打开音乐播放器
- 用户通过声音输入“open notepad”，应用程序打开文本编辑器

## 依赖项

本项目依赖以下python包：
- PyQT5
- speech_recognition

安装方法：

首先确保已经安装了python和pip，然后执行以下命令：
`pip install PyQT5`
`pip install speech_recognition`

## 修改软件路径

找到asr.py文件中myWindow类的process_command方法，根据注释提示修改路径，使得应用程序可以找到本地对应的应用程序。

## 运行

`cd '/path/to/project'`
`python asr.py`
