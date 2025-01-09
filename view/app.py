import os
import tkinter
from tkinter import filedialog
from typing import List

import customtkinter
from PIL import Image

from controller.internal.logging.view_logger import ViewLogger
from controller.managers.settings_manager import Settings

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

# IMAGE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_images") # when its run in pycharm as proj
IMAGE_PATH = os.path.join("", "images/gui") #when its run as exe


class App(customtkinter.CTk):

    def __init__(self, view_logger: ViewLogger, processes: List[str], settings: Settings,
                 pause_or_resume: callable,
                 cancel_animation: callable,
                 drop_items: callable,
                 marble_click: callable,
                 sell_items: callable,
                 message_reply: callable,
                 close_window: callable,
                 load_settings: callable,
                 load_from_file: callable):
        super().__init__()
        self.view_logger = view_logger
        self.protocol("WM_DELETE_WINDOW", self.on_close_window)
        self.settings = settings
        self.processes = processes
        self.pause_or_resume = pause_or_resume
        self.cancel_animation = cancel_animation
        self.drop_items = drop_items
        self.marble_click = marble_click
        self.sell_items = sell_items
        self.message_reply = message_reply
        self.close_window = close_window
        self.load_settings = load_settings
        self.load_from_file = load_from_file
        # configure window

        self.title("Fishing bot")
        # self.resizable(False, False)
        self.geometry(f"{800}x{320}")

        self.grid_rowconfigure(3, weight=1)

        self.switch = customtkinter.CTkSwitch(master=self, text=f"",
                                              font=customtkinter.CTkFont('Bahnschrift SemiLight', size=18,
                                                                         weight="bold"), width=220, switch_height=25,
                                              switch_width=50,
                                              command=self.run_pause_callback)
        self.switch.grid(row=0, column=0, padx=10, pady=(10, 10))
        self.switch.configure()  # state=tkinter.DISABLED

        self.bg_image = customtkinter.CTkImage(Image.open(os.path.join(IMAGE_PATH, "run_or_pause.png")),
                                               size=(200, 40))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image, text="",
                                                     font=customtkinter.CTkFont(size=25, weight="bold"),
                                                     text_color="white")
        self.bg_image_label.grid(row=0, column=0, padx=(130, 20))

        # create tabview
        self.tabview = customtkinter.CTkTabview(self, segmented_button_selected_color="#528fbb",
                                                segmented_button_selected_hover_color="#528fbb")
        self.tabview.grid(row=2, column=0, padx=(20, 20), pady=(0, 0), sticky="nsew")
        self.tabview.add("Configuration")
        self.tabview.add("Logs")
        self.tabview.tab("Configuration").grid_columnconfigure(2, weight=1)
        self.tabview.tab("Configuration").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Logs").grid_columnconfigure(0, weight=1)

        self.main_config_frame = customtkinter.CTkFrame(self.tabview.tab("Configuration"), fg_color="transparent")
        self.main_config_frame.grid(row=0, column=0, padx=(0, 20), sticky="nsew")
        self.main_config_frame.grid_columnconfigure(4, weight=1)
        self.main_config_frame.grid_rowconfigure(4, weight=1)

        self.bg_image = customtkinter.CTkImage(Image.open(os.path.join(IMAGE_PATH, "image1.png")),
                                               size=(150, 120))
        self.bg_image_label = customtkinter.CTkLabel(self.main_config_frame, image=self.bg_image, text="",
                                                     font=customtkinter.CTkFont(size=25, weight="bold"),
                                                     text_color="white")
        self.bg_image_label.grid(row=0, column=0)

        # self.select_process_label = customtkinter.CTkLabel(self.main_config_frame, text="Metin2 process:",
        #                                                    font=customtkinter.CTkFont(size=15, weight="bold"))
        # self.select_process_label.grid(row=0, column=0, padx=20, pady=(30, 0))

        self.scaling_option_menu = customtkinter.CTkOptionMenu(self.main_config_frame, width=200,
                                                               values=self.processes, dynamic_resizing=False,
                                                               fg_color="#528fbb", button_color="#46c59b")
        self.scaling_option_menu.grid(row=1, column=0, padx=20, pady=(20, 10))

        self.fishing_address_frame = customtkinter.CTkFrame(self.tabview.tab("Configuration"), height=150,
                                                            fg_color="transparent")
        self.fishing_address_frame.grid(row=0, column=1, padx=(0, 20), sticky="nsew")
        self.fishing_address_frame.grid_columnconfigure(0, weight=1)
        self.fishing_address_frame.grid_rowconfigure(6, weight=1)
        self.fishing_offset_label = customtkinter.CTkLabel(self.fishing_address_frame, text="",
                                                           font=customtkinter.CTkFont(size=15, weight="bold"))

        self.fishing_offset_label.grid(row=0, column=0, padx=20, pady=(10, 0))

        self.message_reply_switch = customtkinter.CTkSwitch(self.fishing_address_frame, width=170, text=f"",
                                                            font=customtkinter.CTkFont('Bahnschrift SemiLight',
                                                                                       size=14),
                                                            command=self.message_reply_callback)
        self.message_reply_switch.grid(row=2, column=0, padx=(10, 15), pady=(5, 10))

        self.bg_image = customtkinter.CTkImage(Image.open(os.path.join(IMAGE_PATH, "auto_reply.png")),
                                               size=(120, 20))
        self.bg_image_label = customtkinter.CTkLabel(self.fishing_address_frame, image=self.bg_image, text="",
                                                     font=customtkinter.CTkFont(size=25, weight="bold"),
                                                     text_color="white")
        self.bg_image_label.grid(row=2, column=0, padx=(30, 0), pady=(0, 0))

        self.fishing_marble_click_switch = customtkinter.CTkSwitch(self.fishing_address_frame, width=170, text=f"",
                                                                   font=customtkinter.CTkFont('Bahnschrift SemiLight',
                                                                                              size=14),
                                                                   command=self.marble_click_callback)
        self.fishing_marble_click_switch.grid(row=3, column=0, padx=(10, 15), pady=(10, 10))

        self.bg_image = customtkinter.CTkImage(Image.open(os.path.join(IMAGE_PATH, "marble_click.png")),
                                               size=(120, 20))
        self.bg_image_label = customtkinter.CTkLabel(self.fishing_address_frame, image=self.bg_image, text="",
                                                     font=customtkinter.CTkFont(size=25, weight="bold"),
                                                     text_color="white")
        self.bg_image_label.grid(row=3, column=0, padx=(30, 0), pady=(0, 0))

        self.bg_image = customtkinter.CTkImage(Image.open(os.path.join(IMAGE_PATH, "keys_with_bait.png")),
                                               size=(170, 20))
        self.bg_image_label = customtkinter.CTkLabel(self.fishing_address_frame, image=self.bg_image, text="",
                                                     font=customtkinter.CTkFont(size=25, weight="bold"),
                                                     text_color="white")
        self.bg_image_label.grid(row=4, column=0, padx=(0, 0), pady=(0, 0))

        self.bait_keys_entry = customtkinter.CTkEntry(self.fishing_address_frame, border_width=1, width=160,
                                                      placeholder_text="Keys with fish bait", height=25,
                                                      font=customtkinter.CTkFont('Arial', size=16))
        self.bait_keys_entry.grid(row=5, column=0, padx=(10, 20), pady=(0, 0))

        self.chat_next_address_frame = customtkinter.CTkFrame(self.tabview.tab("Configuration"), height=150,
                                                              fg_color="transparent")
        self.chat_next_address_frame.grid(row=0, column=2, padx=(0, 20), sticky="nsew")
        self.chat_next_address_frame.grid_columnconfigure(6, weight=1)
        self.chat_next_address_frame.grid_rowconfigure(6, weight=1)
        self.chat_next_offset_label = customtkinter.CTkLabel(self.chat_next_address_frame, text="",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.chat_next_offset_label.grid(row=0, column=0, padx=20, pady=(10, 0))

        self.cancel_animation_switch = customtkinter.CTkSwitch(self.chat_next_address_frame, text=f"", width=240,
                                                               font=customtkinter.CTkFont('Bahnschrift SemiLight',
                                                                                          size=14),
                                                               command=self.cancel_animations_callback)
        self.cancel_animation_switch.grid(row=1, column=0, padx=(10, 0), pady=(10, 10))
        self.bg_image = customtkinter.CTkImage(Image.open(os.path.join(IMAGE_PATH, "cancel_animations.png")),
                                               size=(150, 22))
        self.bg_image_label = customtkinter.CTkLabel(self.chat_next_address_frame, image=self.bg_image, text="",
                                                     font=customtkinter.CTkFont(size=25, weight="bold"),
                                                     text_color="white")
        self.bg_image_label.grid(row=1, column=0, padx=(10, 0), pady=(0, 0))
        self.drop_items_switch = customtkinter.CTkSwitch(self.chat_next_address_frame, text=f"", width=240,
                                                         font=customtkinter.CTkFont('Bahnschrift SemiLight', size=14),
                                                         command=self.drop_items_callback)
        self.drop_items_switch.grid(row=2, column=0, padx=(10, 0), pady=(10, 10))
        self.bg_image = customtkinter.CTkImage(Image.open(os.path.join(IMAGE_PATH, "drop_items.png")),
                                               size=(100, 22))
        self.bg_image_label = customtkinter.CTkLabel(self.chat_next_address_frame, image=self.bg_image, text="",
                                                     font=customtkinter.CTkFont(size=25, weight="bold"),
                                                     text_color="white")
        self.bg_image_label.grid(row=2, column=0, padx=(10, 0), pady=(0, 0))
        self.sell_items_switch = customtkinter.CTkSwitch(self.chat_next_address_frame, text=f"", width=240,
                                                         font=customtkinter.CTkFont('Bahnschrift SemiLight', size=14),
                                                         command=self.sell_items_callback)
        self.sell_items_switch.grid(row=3, column=0, padx=(10, 0), pady=(10, 10))
        self.bg_image = customtkinter.CTkImage(Image.open(os.path.join(IMAGE_PATH, "sell_items.png")),
                                               size=(100, 22))
        self.bg_image_label = customtkinter.CTkLabel(self.chat_next_address_frame, image=self.bg_image, text="",
                                                     font=customtkinter.CTkFont(size=25, weight="bold"),
                                                     text_color="white")
        self.bg_image_label.grid(row=3, column=0, padx=(10, 0), pady=(0, 0))
        self.logs_box = customtkinter.CTkTextbox(self.tabview.tab("Logs"), width=745, height=200)
        self.logs_box.grid(row=0, column=1, padx=(0, 0), sticky="nsew")
        self.logs_box.configure(state='disabled')

    def open_file_explorer(self):
        file_path = filedialog.askopenfilename()
        self.load_from_file(file_path)

    def on_load_settings(self):
        self.load_settings()

    def on_close_window(self):
        self.close_window()
        self.destroy()

    def run_pause_callback(self):
        self.pause_or_resume()

    def cancel_animations_callback(self):
        self.cancel_animation()

    def drop_items_callback(self):
        self.drop_items()
        print(IMAGE_PATH)

    def sell_items_callback(self):
        self.sell_items()

    def marble_click_callback(self):
        self.marble_click()

    def message_reply_callback(self):
        self.message_reply()
