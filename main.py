import tkinter as tk
import json

from settings import *


class Messenger(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.username = ""

        tk.Tk.wm_title(self, "Messenger")
        self.geometry('800x600')

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


class LoginPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller

        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        self.enter_button = tk.Button(self, text="Login", command=self.login)
        self.enter_button.pack()

    def login(self):

        self.controller.username = self.name_entry.get()
        self.controller.frames[MainPage].auto_refresh()
        self.controller.show_frame(MainPage)


class MainPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller

        self.controller.bind("<Return>", lambda e: self.send_message(self.entry.get()))

        with open(FILE_PATH, 'r') as infile:
            self.data = json.load(infile)

        self.entry = tk.Entry(self)
        self.entry.pack()
        self.send_button = tk.Button(self, text="Send", command=lambda: self.send_message(self.entry.get()))
        self.send_button.pack()
        self.refresh_button = tk.Button(self, text="Refresh", command=self.refresh)
        self.refresh_button.pack()
        self.display = tk.Text(self)
        self.display.pack()

    def send_message(self, message):

        if message == "":
            return

        self.data["messages"].append("{}: {}".format(self.controller.username, message))

        if len(self.data["messages"]) > MESSAGE_THRESHOLD:
            self.data["messages"] = self.data["messages"][-MESSAGE_THRESHOLD:]

        with open(FILE_PATH, 'w') as outfile:
            json.dump(self.data, outfile)

        self.entry.delete(0, tk.END)

        self.refresh()

    def refresh(self):

        with open(FILE_PATH, 'r') as infile:
            data = json.load(infile)

        self.display.delete('1.0', tk.END)

        for message in data["messages"]:
            self.display.insert(tk.END, message + "\n")

    def auto_refresh(self):

        self.refresh()

        self.controller.after(5000, self.auto_refresh)


app = Messenger()
app.mainloop()
