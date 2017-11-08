import tkinter as tk
import json

from settings import *

name = input("Enter your username: ")

with open("//H023FILESRV01/OldPupilSHare/messages.json", 'r') as infile:
    data = json.load(infile)


def send_message(message):

    global data, name

    data["messages"].append("{}: {}".format(name, message))

    with open("//H023FILESRV01/OldPupilSHare/messages.json", 'w') as outfile:
        json.dump(data, outfile)

    refresh()


def refresh():

    global data, display

    with open("//H023FILESRV01/OldPupilSHare/messages.json", 'r') as infile:
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
