import time
from collections import defaultdict
from uuid import UUID

import openai
from controller.internal.logging.view_logger import ViewLogger
from controller.managers.process_memory_manager import Process
from controller.internal.screenshot_management.vision import Vision
from controller.internal.screenshot_management.window_capture import WindowCapture

INPUT_KWARGS = {
    'send_to_process': False,
    'focus': True,
    'sleep_between_presses': 0.1,
    'sleep_between_keys': 0.13
}


class MessageReplier:

    def __init__(self, app_id: UUID, message_path_to_be_clicked, remove_chat_to_be_clicked,
                 process: Process, logger: ViewLogger):
        self.app_id = app_id
        self.logger = logger
        self.process = process
        self.win_cap = None
        self.message_path_to_be_clicked = message_path_to_be_clicked
        self.remove_chat_to_be_clicked = remove_chat_to_be_clicked
        self.player_chat_history = defaultdict(list)

    def reply(self, message_from_user):
        self.logger.update_logs(f"Got a(n) message: {message_from_user}!")
        colon_index = message_from_user.find(":")
        # Extract the substring after the colon
        result_string = message_from_user[colon_index + 1:]
        if colon_index != -1:
            user_id = message_from_user[:colon_index]
        else:
            # Nie znaleziono dwukropka, zachowaj oryginalny ciąg znaków
            user_id = message_from_user
        self.player_chat_history[user_id].append(result_string)
        if len(self.player_chat_history[user_id]) > 8:
            return
        self.process.send_input('Esc', **INPUT_KWARGS)
        result = self.click(self.message_path_to_be_clicked)
        if result:
            reply_message = self.determine_reply(user_id)
            self.player_chat_history[user_id].append(reply_message)
            self.process.send_input(*reply_message, '\n', 'Esc', **INPUT_KWARGS)
            self.logger.update_logs(f"Send a(n) message: {reply_message}!")

    def click(self,
              inventory_path):  # todo sprawdzanie czy jest wiadomosc, bo jak nie to wchodzi w self.process.send_input i dziwne rzeczy robi
        self.win_cap = WindowCapture(self.process.hwnd)
        screenshot = self.win_cap.get_screenshot()
        points = Vision(self.win_cap.get_screen_position).find2(screenshot, inventory_path, 0.8)
        counter = 0
        while len(points) < 1 and counter < 10:
            self.win_cap = WindowCapture(self.process.hwnd)
            screenshot = self.win_cap.get_screenshot()
            points = Vision(self.win_cap.get_screen_position).find2(screenshot, inventory_path, 0.8)
            counter = counter + 1
            time.sleep(0.1)
        if len(points) < 1:
            return False
        if points:
            self.process.send_mouse_click(True, points[0][0], points[0][1], hwnd=self.process.hwnd)
        return True

    def determine_reply(self, user_id):
        openai.api_key = "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"
        messages = self.prepare_messages(user_id) if len(
            self.player_chat_history[user_id]) < 6 else self.end_conversation_messages()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message.content.strip().lower().replace(",", "").replace(".", "")

    def prepare_messages(self, user_id):
        prompt = "Jesteś graczem gry Metin2, do którego pisze inny gracz. Nie używaj słowa metin2. Odpisuj krótko, maksymalnie 10 słów. Potocznym językiem." \
                 "Nie korzystaj ze znaków interpunkcyjnych ani wykrzynkików. Jeśli będziesz miał problem ze zrozumieniem wiadomości odpisz - :)."
        messages = [{"role": "system", "content": prompt}]
        for i in range(len(self.player_chat_history[user_id])):
            if i % 2 == 0:
                messages.append({"role": "user", "content": self.player_chat_history[user_id][i]})
            else:
                messages.append({"role": "assistant", "content": self.player_chat_history[user_id][i]})
        return messages

    def end_conversation_messages(self):
        prompt = "Napisz - miło się rozmawiało ale musze dalej łowić ryby więc nie mam czasu. W innych słowach, używając maksymalnie 5 słów. Używaj języka nastolatków."
        messages = [{"role": "system", "content": prompt}]
        return messages

    def single_double_click_operation(self, point):
        self.process.send_mouse_click(True, point[0], point[1], hwnd=self.process.hwnd, button='right')
        self.logger.update_logs("Double Clicked an message...")
