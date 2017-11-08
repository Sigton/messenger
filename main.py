import tkinter as tk
import json

from settings import *

name = input("Enter your username: ")


class Messenger(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Messenger")
        self.geometry('800x600')

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for f in (MainPage,):

            frame = f(self.container, self)

            self.frames[f] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class MainPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller

        with open(FILE_PATH, 'r') as infile:
            self.data = json.load(infile)

        entry = tk.Entry(self)
        entry.pack()
        send_button = tk.Button(self, text="Send", command=lambda: self.send_message(entry.get()))
        send_button.pack()
        refresh_button = tk.Button(self, text="Refresh", command=self.refresh)
        refresh_button.pack()
        display = tk.Text(self)
        display.pack()

    def send_message(self, message):

        self.data["messages"].append("{}: {}".format(name, message))

        with open(FILE_PATH, 'w') as outfile:
            json.dump(self.data, outfile)

        self.refresh()

    def refresh(self):

        with open(FILE_PATH, 'r') as infile:
            data = json.load(infile)

        self.display.delete('1.0', tk.END)

        for message in data["messages"]:
            self.display.insert(tk.END, message + "\n")
