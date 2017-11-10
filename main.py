import tkinter as tk
from tkinter import messagebox

import datetime
import sqlite3

from settings import *


class Messenger(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.db = sqlite3.connect(FILE_PATH)
        self.cursor = self.db.cursor()
        
        self.username = ""

        self.tk_setPalette(background=BACKGROUND_COLOUR)

        tk.Tk.wm_title(self, "Woodpecker")
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

        tk.Label(self, text="Login to Woodpecker", font=HEADING_FONT).grid(row=0, column=0, columnspan=2, pady=10)
        tk.Label(self, text="Enter your nickname:",
                 font=TEXTBOX_FONT).grid(row=1, column=0, sticky="w", padx=10,pady=30)

        self.name_entry = tk.Entry(self, bg=TEXTBOX_COLOUR, font=TEXTBOX_FONT)
        self.name_entry.grid(row=1, column=1)

        self.enter_button = tk.Button(self, text="Login", command=self.login, width=25,
                                      bg=BUTTON_COLOUR, font=MEDIUM_FONT, activebackground=BUTTON_ACTIVE_COLOUR)
        self.enter_button.grid(row=2, column=0, columnspan=2)

    def login(self):

        name = self.name_entry.get()

        if 2 < len(name) < 13:

            self.controller.cursor.execute('''SELECT nickname FROM users''')
            users = [user[0] for user in self.controller.cursor.fetchall()]

            if name not in users:

                self.controller.username = self.name_entry.get()
                self.controller.show_frame(MainPage)

            else:
                messagebox.showerror("Failed to Login", "That username is already taken!")

        else:
            messagebox.showerror("Failed to Login", "Username has to be between 3 and 12 characters.")

    def setup(self):

        self.controller.geometry('300x180')
        self.controller.bind("<Return>", lambda e: self.login)


class MainPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.parent = parent
        self.controller = controller

        self.can_send = True
        self.status = 0

        tk.Label(self, text="Woodpecker",
                 font=HEADING_FONT).grid(row=0, column=0, columnspan=3,
                                         pady=10, padx=20, sticky="nw")
        tk.Label(self, text="Online Users:",
                 font=HEADING_FONT).grid(row=0, column=3,
                                         pady=10, sticky="nw")
        tk.Label(self, text="By Jamie, v0.6.0",
                 font=MEDIUM_FONT, fg=DARK_TEXT_COLOUR).grid(row=6, column=0, sticky="nw", pady=10, padx=20)

        self.error_message = tk.Label(self, text="",
                                      font=MEDIUM_FONT, fg=ERROR_COLOUR)
        self.error_message.grid(row=3, column=0, sticky="w", padx=20)

        self.entry = tk.Text(self, width=50, height=2, bg=DARK_BACKGROUND_COLOUR, font=TEXTBOX_FONT)
        self.entry.grid(row=1, column=0, columnspan=2, rowspan=2, sticky="w", padx=10, ipady=30)

        self.send_button = tk.Button(self, text="Send",
                                     command=lambda: self.send_message(self.entry.get("1.0", tk.END)),
                                     width=10, bg=BUTTON_COLOUR, font=MEDIUM_FONT,
                                     activebackground=BUTTON_ACTIVE_COLOUR)
        self.send_button.grid(row=1, column=2, sticky="w", ipady=10, padx=5)

        self.refresh_button = tk.Button(self, text="Refresh", command=self.refresh,
                                        width=10, bg=BUTTON_COLOUR, font=MEDIUM_FONT,
                                        activebackground=BUTTON_ACTIVE_COLOUR)
        self.refresh_button.grid(row=2, column=2, sticky="w", ipady=10, padx=5)

        self.display = tk.Text(self, state="disabled", width=100, height=25, bg=TEXTBOX_COLOUR, font=TEXTBOX_FONT)
        self.display.grid(row=5, column=0, columnspan=4, sticky="nsew")

        self.online_users = tk.Text(self, state="disabled", height=12, bg=TEXTBOX_COLOUR, font=TEXTBOX_FONT)
        self.online_users.grid(row=1, column=3, rowspan=4)

        self.menu_bar = tk.Menu(self.controller)

        self.file_menu = tk.Menu(self.menu_bar)
        self.file_menu.add_command(label="Settings", command=None)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Logout", command=None)
        self.file_menu.add_command(label="Quit", command=self.logoff)
        self.menu_bar.add_cascade(label="WP", menu=self.file_menu)

        self.servers_menu = tk.Menu(self.menu_bar)
        self.servers_menu.add_command(label="Add Server", command=None)
        self.servers_menu.add_command(label="Set Server", command=None)
        self.servers_menu.add_command(label="Manage Servers", command=None)
        self.servers_menu.add_command(label="Create Server", command=None)
        self.menu_bar.add_cascade(label="Servers", menu=self.servers_menu)

    def setup(self):

        self.controller.geometry('800x600')
        self.controller.bind("<Return>", lambda e: self.send_message(self.entry.get("1.0", tk.END)))
        self.controller.bind("<FocusIn>", self.set_status_here)
        self.controller.bind("<FocusOut>", self.set_status_away)

        self.set_online()
        self.controller.protocol("WM_DELETE_WINDOW", self.logoff)

        self.controller.config(menu=self.menu_bar)

        self.send_message(self.controller.username + " is now online.", False)

        self.auto_refresh()

    def send_message(self, message, prefix=True):

        if message.strip("\n") == "" or not self.can_send:
            return

        if len(message) > MESSAGE_LENGTH_THRESHOLD:
            self.error_message.config(
                text="Message is too long! Max of {} characters.".format(MESSAGE_LENGTH_THRESHOLD)
            )
            self.entry.delete("1.0", tk.END)

            self.can_send = False
            self.controller.after(2000, self.allow_message)

            return

        message = message.replace("\n", " ")

        time = datetime.datetime.now().time()
        hours, minutes, seconds = str(time.hour), str(time.minute), str(time.second)
        if len(hours) == 1:
            hours = "0" + hours
        if len(minutes) == 1:
            minutes = "0" + minutes
        if len(seconds) == 1:
            seconds = "0" + seconds

        self.controller.cursor.execute('''INSERT INTO messages(time, name, message, prefix)
                                                  VALUES(?,?,?,?)''',
                                       ("<{}:{}:{}>".format(hours, minutes, seconds),
                                        self.controller.username, message, prefix))
        self.controller.db.commit()

        self.entry.delete("1.0", tk.END)

        self.refresh()

        self.can_send = False
        self.controller.after(2000, self.allow_message)

    def refresh(self):

        self.controller.cursor.execute('''SELECT time, name, message, prefix FROM messages''')
        messages = self.controller.cursor.fetchall()[-20:]

        self.display.config(state="normal")
        self.display.delete('1.0', tk.END)

        for message in messages:
            self.display.insert(tk.END,
                                "{} {}: {}\n".format(message[0], message[1], message[2]) if message[3]
                                else "{} {}\n".format(message[0], message[2]))

        self.display.config(state="disabled")

        self.online_users.config(state="normal")
        self.online_users.delete('1.0', tk.END)

        self.controller.cursor.execute('''SELECT nickname, status FROM users''')
        users = self.controller.cursor.fetchall()

        user_names = [user[0] for user in users]

        n = 0
        for user in user_names:
            self.online_users.insert(tk.END, "{} {}\n".format(user, "(Away)" if not users[n][1] else ""))
            n += 1

        self.online_users.config(state="disabled")

    def set_online(self):

        self.controller.cursor.execute('''SELECT nickname, status FROM users''')
        users = self.controller.cursor.fetchall()

        user_names = [user[0] for user in users]

        if self.controller.username not in user_names:
            self.controller.cursor.execute('''INSERT INTO users(nickname, status)
                                              VALUES(?,?)''', (self.controller.username, 1))

    def logoff(self):
            
        self.send_message(self.controller.username + " has went offline.", False)

        self.controller.cursor.execute('''DELETE FROM users WHERE nickname=?''', (self.controller.username,))

        self.controller.db.commit()

        self.controller.destroy()
        self.controller.db.close()

    def auto_refresh(self):

        self.refresh()

        self.controller.after(UPDATE_FREQUENCY, self.auto_refresh)

    def allow_message(self):

        self.can_send = True
        self.error_message.config(text="")

    def set_status_away(self, event):

        if event.widget == self.controller:
            self.controller.cursor.execute('''UPDATE users SET status = 0 WHERE nickname = ?''',
                                           (self.controller.username,))
            self.controller.db.commit()

    def set_status_here(self, event):

        if event.widget == self.controller:
            self.controller.cursor.execute('''UPDATE users SET status = 1 WHERE nickname = ?''',
                                           (self.controller.username,))
            self.controller.db.commit()


app = Messenger()
app.mainloop()
