import tkinter as tk
import json

from settings import *

'''
name = input("Enter your username: ")

with open(FILE_PATH, 'r') as infile:
    data = json.load(infile)
'''


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

def send_message(message):

    global data, name

    data["messages"].append("{}: {}".format(name, message))

    with open(FILE_PATH, 'w') as outfile:
        json.dump(data, outfile)

    refresh()


def refresh():

    global data, display

    with open(FILE_PATH, 'r') as infile:
        data = json.load(infile)

    display.delete('1.0', tk.END)

    for message in data["messages"]:
        display.insert(tk.END, message + "\n")


root = tk.Tk()
entry = tk.Entry(root)
entry.pack()
send_button = tk.Button(root, text="Send", command=lambda: send_message(entry.get()))
send_button.pack()
refresh_button = tk.Button(root, text="Refresh", command=refresh)
refresh_button.pack()
display = tk.Text(root)
display.pack()

root.mainloop()
