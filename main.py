import tkinter as tk

import json
import datetime

from settings import *


class Messenger(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.username = ""

        self.tk_setPalette(background=BACKGROUND_COLOUR)

        tk.Tk.wm_title(self, "Messenger")
        self.geometry('800x600')
        self.resizable(False, False)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for f in (MainPage, LoginPage):

            frame = f(self.container, self)

            self.frames[f] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()
        frame.setup()


class LoginPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller

        tk.Label(self, text="Login to GHS Messenger", font=HEADING_FONT).grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(self, text="Enter your nickname:",
                 font=TEXTBOX_FONT).grid(row=1, column=0, sticky="w", padx=10, pady=30)

        self.name_entry = tk.Entry(self, bg=BACKGROUND_COLOUR, font=TEXTBOX_FONT)
        self.name_entry.grid(row=1, column=1)

        self.enter_button = tk.Button(self, text="Login", command=self.login, width=25,
                                      bg=BUTTON_COLOUR, font=BUTTON_FONT, activebackground=BUTTON_ACTIVE_COLOUR)
        self.enter_button.grid(row=2, column=0, columnspan=2)

    def login(self):

        self.controller.username = self.name_entry.get()
        self.controller.frames[MainPage].auto_refresh()
        self.controller.show_frame(MainPage)

    def setup(self):

        self.controller.geometry('300x180')


class MainPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller

        self.can_send = True

        self.controller.bind("<Return>", lambda e: self.send_message(self.entry.get("1.0", tk.END)))

        with open(FILE_PATH, 'r') as infile:
            self.data = json.load(infile)

        tk.Label(self, text="GHS Messenger", font=HEADING_FONT).grid(row=0, column=0, columnspan=3,
                                                                     pady=10, padx=20, sticky="nw")

        self.entry = tk.Text(self, width=50, height=2, bg=TEXTBOX_COLOUR, font=TEXTBOX_FONT)
        self.entry.grid(row=1, column=0, columnspan=2, rowspan=2, sticky="w", padx=10, ipady=30)

        self.send_button = tk.Button(self, text="Send",
                                     command=lambda: self.send_message(self.entry.get("1.0", tk.END)),
                                     width=10, bg=BUTTON_COLOUR, font=BUTTON_FONT,
                                     activebackground=BUTTON_ACTIVE_COLOUR)
        self.send_button.grid(row=1, column=2, sticky="w", ipady=10, padx=5)

        self.refresh_button = tk.Button(self, text="Refresh", command=self.refresh,
                                        width=10, bg=BUTTON_COLOUR, font=BUTTON_FONT,
                                        activebackground=BUTTON_ACTIVE_COLOUR)
        self.refresh_button.grid(row=2, column=2, sticky="w", ipady=10, padx=5)

        self.display = tk.Text(self, state="disabled", width=100, height=25, bg=TEXTBOX_COLOUR, font=TEXTBOX_FONT)
        self.display.grid(row=5, column=0, columnspan=4, sticky="nsew")

        self.online_users = tk.Text(self, state="disabled", height=12, bg=TEXTBOX_COLOUR, font=TEXTBOX_FONT)
        self.online_users.grid(row=0, column=3, rowspan=5)

    def setup(self):

        self.controller.geometry('800x600')

    def send_message(self, message):

        if message.strip("\n") == "" or not self.can_send:
            self.entry.delete("1.0", tk.END)
            return

        time = datetime.datetime.now().time()

        self.data["messages"].append("<{}:{}:{}> {}: {}".format(time.hour, time.minute, time.second,
                                                                self.controller.username, message.strip("\n")))

        if len(self.data["messages"]) > MESSAGE_THRESHOLD:
            self.data["messages"] = self.data["messages"][-MESSAGE_THRESHOLD:]

        with open(FILE_PATH, 'w') as outfile:
            json.dump(self.data, outfile)

        self.entry.delete("1.0", tk.END)

        self.refresh()

        self.can_send = False
        self.controller.after(2000, self.allow_message)

    def refresh(self):

        with open(FILE_PATH, 'r') as infile:
            data = json.load(infile)

        self.display.config(state="normal")
        self.display.delete('1.0', tk.END)

        for message in data["messages"]:
            self.display.insert(tk.END, message + "\n")

        self.display.config(state="disabled")

    def auto_refresh(self):

        self.refresh()

        self.controller.after(5000, self.auto_refresh)

    def allow_message(self):

        self.can_send = True


app = Messenger()
app.mainloop()
