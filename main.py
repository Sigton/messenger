import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

import datetime
import sqlite3
import json

from settings import *


class Messenger(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.db = None
        self.cursor = None

        self.active_server = None
        
        self.username = ""
        self.servers = []
        self.preference_file = None

        self.tk_setPalette(background=BACKGROUND_COLOUR)

        tk.Tk.wm_title(self, "Woodpecker Messenger")
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

    def connect_to_server(self, server_index):

        if self.db is not None:
            self.frames[MainPage].send_message(self.username + " has went offline.", False)

            self.cursor.execute('''DELETE FROM users WHERE nickname=?''', (self.username,))

            self.db.commit()
            self.db.close()

        self.db = sqlite3.connect(self.servers[server_index][1])
        self.cursor = self.db.cursor()
        self.active_server = server_index
        self.frames[MainPage].setup()

    def disconnect(self):

        if self.db is not None:
            self.frames[MainPage].send_message(self.username + " has went offline.", False)

            self.cursor.execute('''DELETE FROM users WHERE nickname=?''', (self.username,))

            self.db.commit()
            self.db.close()

        self.db = None
        self.cursor = None
        self.active_server = None
        self.frames[MainPage].setup()


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

            if self.controller.db is not None:

                self.controller.cursor.execute('''SELECT nickname FROM users''')
                users = [user[0] for user in self.controller.cursor.fetchall()]

                if name not in users:

                    self.controller.username = self.name_entry.get()
                    self.controller.show_frame(MainPage)

                else:
                    messagebox.showerror("Failed to Login", "That username is already taken!")
            else:
                self.controller.username = self.name_entry.get()
                self.controller.show_frame(MainPage)

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

        self.server_settings = None
        self.style_settings = None
        self.preference_settings = None

        self.can_send = True
        self.status = 0
        self.server_settings_open = False
        self.style_settings_open = False
        self.preference_settings_open = False

        tk.Label(self, text="Woodpecker Messenger",
                 font=HEADING_FONT).grid(row=0, column=0, columnspan=3,
                                         pady=10, padx=20, sticky="nw")
        tk.Label(self, text="Online Users:",
                 font=HEADING_FONT).grid(row=0, column=3,
                                         pady=10, sticky="nw")
        tk.Label(self, text="v0.8.0",
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

        self.menu_bar.add_command(label="Quit", command=self.logoff)
        self.menu_bar.add_command(label="Logout", command=None)
        self.menu_bar.add_command(label="Servers", command=self.open_server_settings)
        self.menu_bar.add_command(label="Styling", command=self.open_style_settings)
        self.menu_bar.add_command(label="Preferences", command=self.open_preference_settings)

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

        if self.controller.db is None:

            self.entry.delete("1.0", tk.END)

            if prefix:
                self.can_send = False
                self.controller.after(2000, self.allow_message)

            return

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

        self.refresh()

        self.entry.delete("1.0", tk.END)

        if prefix:
            self.can_send = False
            self.controller.after(2000, self.allow_message)

    def refresh(self):

        if self.controller.db is None:
            self.display.config(state="normal")

            self.display.delete('1.0', tk.END)
            self.display.insert(tk.END, "No Server Selected!")

            self.display.config(state="disabled")

            return

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

        if self.controller.db is None:
            return

        self.controller.cursor.execute('''SELECT nickname, status FROM users''')
        users = self.controller.cursor.fetchall()

        user_names = [user[0] for user in users]

        if self.controller.username not in user_names:
            self.controller.cursor.execute('''INSERT INTO users(nickname, status)
                                              VALUES(?,?)''', (self.controller.username, 1))

    def logoff(self):

        if self.controller.db is not None:
            self.send_message(self.controller.username + " has went offline.", False)

            self.controller.cursor.execute('''DELETE FROM users WHERE nickname=?''', (self.controller.username,))

            self.controller.db.commit()
            self.controller.db.close()

        self.controller.destroy()

    def auto_refresh(self):

        self.refresh()

        self.controller.after(UPDATE_FREQUENCY, self.auto_refresh)

    def allow_message(self):

        self.can_send = True
        self.error_message.config(text="")

    def set_status_away(self, event):

        if event.widget == self.controller and self.controller.db is not None:
            self.controller.cursor.execute('''UPDATE users SET status = 0 WHERE nickname = ?''',
                                           (self.controller.username,))
            self.controller.db.commit()

    def set_status_here(self, event):

        if event.widget == self.controller and self.controller.db is not None:
            self.controller.cursor.execute('''UPDATE users SET status = 1 WHERE nickname = ?''',
                                           (self.controller.username,))
            self.controller.db.commit()

    def open_server_settings(self):

        if not self.server_settings_open:
            self.server_settings_open = True
            self.server_settings = ServerSettings(self, self.controller)

    def open_style_settings(self):

        if not self.style_settings_open:
            self.style_settings_open = True
            self.style_settings = StyleSettings(self, self.controller)

    def open_preference_settings(self):

        if not self.preference_settings_open:
            self.preference_settings_open = True
            self.preference_settings = PreferenceSettings(self, self.controller)

    def load_preferences(self):
        try:
            with open(self.controller.preference_file, 'r') as infile:
                data = json.load(infile)

            self.controller.servers = data["servers"]
        except Exception:
            messagebox.showerror("Loading Failed", "Loading preferences failed, file is invalid.")

    def save_preferences(self):
        with open(self.controller.preference_file, 'w') as outfile:
            json.dump({"servers": self.controller.servers}, outfile)


class ServerSettings(tk.Toplevel):

    def __init__(self, parent, controller):

        tk.Toplevel.__init__(self)

        self.parent = parent
        self.controller = controller

        self.server_info = None
        self.server_info_open = False

        self.wm_title("Server Settings")
        self.wm_geometry("600x400")
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.resizable(False, False)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.add_button = tk.Button(self.container, text="Add Server", width=20, bg=BUTTON_COLOUR,
                                    activebackground=BUTTON_ACTIVE_COLOUR, font=MEDIUM_FONT,
                                    command=lambda:self.open_server_info(0))
        self.add_button.grid(row=0, column=0, padx=10, ipady=10)

        self.edit_button = tk.Button(self.container, text="Edit Server", width=20, bg=BUTTON_COLOUR,
                                     activebackground=BUTTON_ACTIVE_COLOUR, font=MEDIUM_FONT)
        self.edit_button.grid(row=1, column=0, padx=10, ipady=10)

        self.set_button = tk.Button(self.container, text="Join Server", width=20, bg=BUTTON_COLOUR,
                                    activebackground=BUTTON_ACTIVE_COLOUR, font=MEDIUM_FONT,
                                    command=self.set_active_server)
        self.set_button.grid(row=2, column=0, padx=10, ipady=10)

        self.remove_button = tk.Button(self.container, text="Remove Server", width=20, bg=BUTTON_COLOUR,
                                       activebackground=BUTTON_ACTIVE_COLOUR, font=MEDIUM_FONT,
                                       command=self.remove_server)
        self.remove_button.grid(row=3, column=0, padx=10, ipady=10)

        self.display = tk.Text(self.container, width=58, height=31,
                               bg=TEXTBOX_COLOUR, font=TEXTBOX_FONT, state="disabled")
        self.display.grid(row=0, column=1, rowspan=10, sticky="e")

        self.server_buttons = []
        if self.controller.db is None:
            self.active_server = None
        else:
            self.active_server = self.controller.active_server
        self.selected_server = None

        self.update_server_list()

    def update_server_list(self):

        self.display.config(state="normal")

        self.server_buttons = []
        self.display.delete("1.0", tk.END)

        n = 0
        for server in self.controller.servers:

            self.server_buttons += [tk.Button(self.display, text=server[0], width=49, bg=BUTTON_COLOUR,
                                              activebackground=BUTTON_ACTIVE_COLOUR, font=MEDIUM_FONT,
                                              command=lambda x=n: self.update_selected_button(x))]
            self.display.window_create(tk.END, window=self.server_buttons[-1])
            n += 1

        try:
            if self.active_server is not None:
                self.server_buttons[self.active_server].config(bg=SELECTED_BUTTON_COLOUR,
                                                               activebackground=SELECTED_BUTTON_ACTIVE_COLOUR)
        except IndexError:
            pass

        try:
            if self.selected_server is not None:
                self.server_buttons[self.selected_server].config(fg=SELECTED_TEXT_COLOUR)
        except IndexError:
            pass

        self.display.config(state="disabled")

    def close(self):

        self.parent.server_settings_open = False
        self.destroy()

    def update_selected_button(self, button_index):

        self.selected_server = button_index
        self.update_server_list()

    def set_active_server(self):

        if self.selected_server is None:
            return
        if not len(self.controller.servers):
            return

        if not self.active_server == self.selected_server:
            self.active_server = self.selected_server
            self.update_server_list()

            self.controller.connect_to_server(self.active_server)

        self.close()

    def remove_server(self):

        if self.selected_server is None:
            return
        if not len(self.controller.servers):
            return

        del self.server_buttons[self.selected_server]
        del self.controller.servers[self.selected_server]

        if self.selected_server == self.active_server:
            self.selected_server = None
            self.controller.disconnect()
            self.close()

        if len(self.controller.servers) == 0:
            self.selecetd_server = 0 
        else:
            while self.selected_server > len(self.controller.servers)-1:
                self.selected_server -= 1

        self.update_server_list()

    def open_server_info(self, method):

        if not self.server_info_open:
            self.server_info_open = True
            if not method:
                self.server_info = AddServer(self, self.controller)


class StyleSettings(tk.Toplevel):

    def __init__(self, parent, controller):

        tk.Toplevel.__init__(self)

        self.parent = parent
        self.controller = controller

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.resizable(False, False)

    def close(self):

        self.parent.style_settings_open = False
        self.destroy()


class PreferenceSettings(tk.Toplevel):

    def __init__(self, parent, controller):

        tk.Toplevel.__init__(self)

        self.parent = parent
        self.controller = controller

        self.wm_title("Preferences Settings")
        self.wm_geometry("200x150")
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.resizable(False, False)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_columnconfigure(2, weight=1)

        self.entry = tk.Entry(self.container, width=20, bg=TEXTBOX_COLOUR, font=TEXTBOX_FONT)
        self.entry.grid(row=0, column=0, columnspan=3, pady=20, padx=20, sticky="ew")

        self.browse_button = tk.Button(self.container, text="Browse", width=12,
                                       bg=BUTTON_COLOUR, activebackground=BUTTON_ACTIVE_COLOUR, font=MEDIUM_FONT,
                                       command=self.select_preference_file)
        self.browse_button.grid(row=1, column=0, pady=20, sticky='ew', ipady=5)

        self.load_button = tk.Button(self.container, text="Load", width=12,
                                     bg=BUTTON_COLOUR, activebackground=BUTTON_ACTIVE_COLOUR, font=MEDIUM_FONT,
                                     command=self.load_preferences)
        self.load_button.grid(row=1, column=1, pady=20, sticky='ew', ipady=5)

        self.save_button = tk.Button(self.container, text="Save", width=12,
                                     bg=BUTTON_COLOUR, activebackground=BUTTON_ACTIVE_COLOUR, font=MEDIUM_FONT,
                                     command=self.parent.save_preferences)
        self.save_button.grid(row=1, column=2, pady=20, sticky='ew', ipady=5)

        if self.controller.preference_file is not None:
            self.entry.insert(tk.END, self.controller.preference_file)

    def select_preference_file(self):

        self.controller.preference_file = filedialog.askopenfilename(title="Select Preference File",
                                                                     filetypes=(("json files", "*.json"),
                                                                                ("all files", "*.*")))
        if self.controller.preference_file is not "":
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, self.controller.preference_file)

    def close(self):

        self.parent.preference_settings_open = False
        self.destroy()

    def load_preferences(self):

        self.parent.load_preferences()
        self.close()


class ServerInfo(tk.Toplevel):

    def __init__(self, parent, controller):

        tk.Toplevel.__init__(self)

        self.parent = parent
        self.controller = controller

        self.wm_title("Server Info")
        self.wm_geometry("400x200")
        self.protocol("WM_DELETE_WINDOW", self.close)

        self.resizable(False, False)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)
        self.container.grid_rowconfigure(2, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)

        tk.Label(self.container, text="Server Name:", font=MEDIUM_FONT).grid(row=0, column=0, sticky="e")
        tk.Label(self.container, text="Server Address:", font=MEDIUM_FONT).grid(row=1, column=0, sticky="e")

        self.name_entry = tk.Entry(self.container, bg=TEXTBOX_COLOUR, font=TEXTBOX_FONT)
        self.name_entry.grid(row=0, column=1, sticky="w")

        self.address_entry = tk.Entry(self.container, bg=TEXTBOX_COLOUR, font=TEXTBOX_FONT)
        self.address_entry.grid(row=1, column=1, sticky="w")

        self.add_button = tk.Button(self.container,
                                    font=MEDIUM_FONT, bg=BUTTON_COLOUR, activebackground=BUTTON_ACTIVE_COLOUR)
        self.add_button.grid(row=2, column=0, ipady=10, sticky="ew")

        self.cancel_button = tk.Button(self.container, text="Cancel",
                                       font=MEDIUM_FONT, bg=BUTTON_COLOUR, activebackground=BUTTON_ACTIVE_COLOUR,
                                       command=self.close)
        self.cancel_button.grid(row=2, column=1, ipady=10, sticky="ew")
        
    def close(self):

        self.parent.server_info_open = False
        self.destroy()


class AddServer(ServerInfo):

    def __init__(self, parent, controller):

        ServerInfo.__init__(self, parent, controller)

        self.add_button.config(text="Add",
                               command=lambda: self.add_server(self.name_entry.get(), self.address_entry.get()))

    def add_server(self, name, address):

        self.controller.servers.append([name, address])
        self.parent.update_server_list()
        self.close()


class EditServer(ServerInfo):

    def __init__(self, parent, controller):

        ServerInfo.__init__(self, parent, controller)

        self.add_button.config(text="Edit")


app = Messenger()
app.mainloop()
