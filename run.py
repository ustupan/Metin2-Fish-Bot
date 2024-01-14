import logging
import sys

import openai
from controller.app_controller import AppController


def main():
    logging.basicConfig(format='[%(asctime)s.%(msecs)03d] %(message)s', datefmt='%d-%m-%Y %H:%M:%S',
                        level=logging.INFO, stream=sys.stdout)


def chat():
    openai.api_key = "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"
    prompt = "Wyobraź sobie, że jesteś graczem Metin2 łowiącym ryby od 5 godzin w oddalonym miejscu. Pisze do ciebie administrator gry w celu sprawdzenia twojej obecności"
    question = "Dobry, obecny?"
    response_prompt = f"{prompt} Odpisuj krótko od dwóch do pięciu słów, nie używaj słowa Metin2, nie zadawaj pytań. Pamietaj ze nie jestes sztuszczą inteligencją tylko graczem. Pisz potocznym językiem"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": response_prompt}, {"role": "user", "content": question}]
    )
    print(response.choices[0].message.content.strip().lower().replace(",", ""))


if __name__ == "__main__":
    AppController().start()
    # chat()



