import openai
import requests
from PIL import Image
from io import BytesIO
import os
import playsound

openai.api_key = "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"

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
]

def chat(prompt, chat=True):
    # 退出
    if prompt == "q":
        return

    # 对话模式
    if chat:
        # 将用户输入添加到对话列表
        messages.append({"role": "user", "content": prompt})

        # 调用 OpenAI API获取回复
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,  # 生成的最大文本长度
            temperature=0.9,  # 控制生成文本的随机性。较高的值会产生更多随机的输出。
            presence_penalty=0.8,  # 控制生成文本的多样性。较高的值会产生更多不同的输出。
            n=1,  # 生成的候选项数量
        )

        # 从 API 响应中获取生成的文本
        generated_text = response['choices'][0]['message']['content']

        # 将生成的文本添加到对话列表
        messages.append({"role": "assistant", "content": generated_text})

        # 打印生成的文本
        return generated_text
    else:
        # 调用 OpenAI API生成图片
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )

        # 从 API 响应中获取生成的图片的 URL
        image_url = response['data'][0]['url']

        # 显示生成的图片
        image_data = requests.get(image_url).content
        image = Image.open(BytesIO(image_data))
        image.show()

        return "The image has been generated."
