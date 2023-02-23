import customtkinter

from controller.managers.settings_loader import Settings

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    def __init__(self, settings: Settings):
        super().__init__()

        self.settings = settings
        # configure window

        self.title("Fishing bot")
        # self.resizable(False, False)
        self.geometry(f"{720}x{400}")

        self.grid_rowconfigure(3, weight=1)

        self.switch = customtkinter.CTkSwitch(master=self, text=f"Run or pause the bot",
                                         font=customtkinter.CTkFont(size=15, weight="bold"),
                                         command=self.run_pause_callback)
        self.switch.grid(row=1, column=0, padx=10, pady=(10, 10))

        # create tabview
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=2, column=0, padx=(20, 20), pady=(0, 0), sticky="nsew")
        self.tabview.add("Configuration")
        self.tabview.add("Options")
        self.tabview.tab("Configuration").grid_columnconfigure(2, weight=1)
        self.tabview.tab("Configuration").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Options").grid_columnconfigure(0, weight=1)

        self.select_process_frame = customtkinter.CTkFrame(self.tabview.tab("Configuration"), height=150,
                                                           fg_color="transparent")
        self.select_process_frame.grid(row=0, column=0, padx=(0, 20), sticky="nsew")
        self.select_process_frame.grid_columnconfigure(4, weight=1)
        self.select_process_frame.grid_rowconfigure(4, weight=1)

        self.select_process_label = customtkinter.CTkLabel(self.select_process_frame, text="Metin2 process:",
                                                           font=customtkinter.CTkFont(size=15, weight="bold"))
        self.select_process_label.grid(row=0, column=0, padx=20, pady=(10, 0))
        self.scaling_option_menu = customtkinter.CTkOptionMenu(self.select_process_frame, width=200,
                                                               values=["metin2client.exe | 1352",
                                                                       "svchost.exe | 15524",
                                                                       "metin2client.exe | 15724",
                                                                       "python.exe | 19552"])
        self.scaling_option_menu.grid(row=1, column=0, padx=20, pady=(0, 10))

        self.main_button_1 = customtkinter.CTkButton(master=self.tabview.tab("Configuration"), border_width=0,
                                                     text_color=("gray10", "#DCE4EE"), text="Load from file")
        self.main_button_1.grid(row=1, column=0, padx=(20, 20), pady=(20, 20))

        self.fishing_address_frame = customtkinter.CTkFrame(self.tabview.tab("Configuration"), height=150,
                                                            fg_color="transparent")
        self.fishing_address_frame.grid(row=0, column=1, padx=(0, 20), sticky="nsew")
        self.fishing_address_frame.grid_columnconfigure(0, weight=1)
        self.fishing_address_frame.grid_rowconfigure(6, weight=1)
        self.fishing_offset_label = customtkinter.CTkLabel(self.fishing_address_frame, text="Fishing",
                                                           font=customtkinter.CTkFont(size=15, weight="bold"))

        self.fishing_offset_label.grid(row=0, column=0, padx=20, pady=(10, 0))

        self.fishing_base_entry = customtkinter.CTkEntry(self.fishing_address_frame, border_width=1,
                                                         placeholder_text="Thrown pole Address", height=10)
        self.fishing_base_entry.grid(row=1, column=0, padx=20, pady=(0, 10))
        self.fish_caught_base_entry = customtkinter.CTkEntry(self.fishing_address_frame, border_width=1,
                                                             placeholder_text="Fish caught Address", height=10)
        self.fish_caught_base_entry.grid(row=2, column=0, padx=20, pady=(0, 10))
        self.fishing_pole_thrown_entry = customtkinter.CTkEntry(self.fishing_address_frame, border_width=1,
                                                                placeholder_text="Pole is thrown offsets", height=15)
        self.fishing_pole_thrown_entry.grid(row=3, column=0, padx=20, pady=(0, 10))

        self.fishing_offset1_entry = customtkinter.CTkEntry(self.fishing_address_frame, border_width=1,
                                                            placeholder_text="Fish caught offsets", height=15)
        self.fishing_offset1_entry.grid(row=4, column=0, padx=20, pady=(0, 10))

        self.chat_next_address_frame = customtkinter.CTkFrame(self.tabview.tab("Configuration"), height=150,
                                                              fg_color="transparent")
        self.chat_next_address_frame.grid(row=0, column=2, padx=(0, 20), sticky="nsew")
        self.chat_next_address_frame.grid_columnconfigure(6, weight=1)
        self.chat_next_address_frame.grid_rowconfigure(6, weight=1)
        self.chat_next_offset_label = customtkinter.CTkLabel(self.chat_next_address_frame, text="Message",
                                                             font=customtkinter.CTkFont(size=15, weight="bold"))
        self.chat_next_offset_label.grid(row=0, column=0, padx=20, pady=(10, 0))
        self.chat_next_base_entry = customtkinter.CTkEntry(self.chat_next_address_frame, border_width=1,
                                                           placeholder_text="Base Address", height=15)
        self.chat_next_base_entry.grid(row=1, column=0, padx=20, pady=(0, 10))
        self.chat_next_content_entry = customtkinter.CTkEntry(self.chat_next_address_frame, border_width=1,
                                                              placeholder_text="Message offsets", height=15)
        self.chat_next_content_entry.grid(row=2, column=0, padx=20, pady=(0, 10))
        self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("Options"), text="CTkLabel on Tab 2")
        self.label_tab_2.grid(row=0, column=0, padx=20, pady=(0, 10))

    def run_pause_callback(self):
        self.switch.toggle()

