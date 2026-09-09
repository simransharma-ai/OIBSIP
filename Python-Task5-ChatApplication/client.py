import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox, simpledialog


HOST = "127.0.0.1"
PORT = 5555

client_socket = None
connected = False
current_username = ""
current_room = ""


# ============================================================
# SEND JSON
# ============================================================

def send_json(data):
    global connected

    if not connected:
        return False

    try:
        message = json.dumps(
            data
        ) + "\n"

        client_socket.sendall(
            message.encode("utf-8")
        )

        return True

    except OSError:
        connected = False

        root.after(
            0,
            show_disconnected
        )

        return False


# ============================================================
# CONNECT SERVER
# ============================================================

def connect_to_server():
    global client_socket
    global connected

    try:
        client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client_socket.connect(
            (HOST, PORT)
        )

        connected = True

        thread = threading.Thread(
            target=receive_messages,
            daemon=True
        )

        thread.start()

        status_label.config(
            text="Connected to server",
            fg="green"
        )

        return True

    except ConnectionRefusedError:

        messagebox.showerror(
            "Connection Error",
            "Unable to connect to server.\n"
            "Please start server.py first."
        )

        return False

    except OSError as error:

        messagebox.showerror(
            "Connection Error",
            str(error)
        )

        return False


# ============================================================
# REGISTER
# ============================================================

def register():
    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning(
            "Required",
            "Please enter username and password."
        )
        return

    send_json({
        "type": "register",
        "username": username,
        "password": password
    })


# ============================================================
# LOGIN
# ============================================================

def login():
    username = username_entry.get().strip()
    password = password_entry.get()

    if not username or not password:

        messagebox.showwarning(
            "Required",
            "Please enter username and password."
        )

        return

    send_json({
        "type": "login",
        "username": username,
        "password": password
    })


# ============================================================
# SHOW CHAT UI
# ============================================================

def show_chat_screen(username):
    global current_username

    current_username = username

    login_frame.pack_forget()

    chat_frame.pack(
        fill="both",
        expand=True
    )

    user_label.config(
        text=f"Logged in as: {username}"
    )

    join_room(
        "General"
    )


# ============================================================
# JOIN ROOM
# ============================================================

def join_room(room=None):
    if room is None:

        room = room_entry.get().strip()

    if not room:
        messagebox.showwarning(
            "Room Required",
            "Please enter a room name."
        )
        return

    send_json({
        "type": "join",
        "room": room
    })


# ============================================================
# SEND MESSAGE
# ============================================================

def send_message(event=None):
    message = message_entry.get().strip()

    if not message:
        return

    if not current_room:

        messagebox.showwarning(
            "Room Required",
            "Please join a chat room first."
        )

        return

    send_json({
        "type": "message",
        "message": message
    })

    message_entry.delete(
        0,
        tk.END
    )


# ============================================================
# ADD EMOJI
# ============================================================

def add_emoji(emoji):
    current_text = message_entry.get()

    message_entry.delete(
        0,
        tk.END
    )

    message_entry.insert(
        0,
        current_text + emoji
    )

    message_entry.focus()


# ============================================================
# CHAT DISPLAY
# ============================================================

def clear_chat():
    chat_text.config(
        state="normal"
    )

    chat_text.delete(
        "1.0",
        tk.END
    )

    chat_text.config(
        state="disabled"
    )


def append_chat(text):
    chat_text.config(
        state="normal"
    )

    chat_text.insert(
        tk.END,
        text + "\n"
    )

    chat_text.see(
        tk.END
    )

    chat_text.config(
        state="disabled"
    )


# ============================================================
# DESKTOP / IN-APP NOTIFICATION
# ============================================================

def notify_new_message(username):
    if username == current_username:
        return

    try:
        if root.focus_get() is None:
            root.bell()

            root.title(
                "● New Message - Chat Application"
            )

            root.after(
                3000,
                lambda: root.title(
                    "OIBSIP Chat Application"
                )
            )

    except tk.TclError:
        pass


# ============================================================
# SERVER MESSAGE PROCESSING
# ============================================================

def process_server_message(data):
    global current_room

    message_type = data.get(
        "type"
    )

    # --------------------------------------------------------
    # REGISTER RESULT
    # --------------------------------------------------------

    if message_type == "register_result":

        if data.get("success"):

            messagebox.showinfo(
                "Registration",
                data.get(
                    "message"
                )
            )

        else:

            messagebox.showerror(
                "Registration",
                data.get(
                    "message"
                )
            )

    # --------------------------------------------------------
    # LOGIN RESULT
    # --------------------------------------------------------

    elif message_type == "login_result":

        if data.get("success"):

            show_chat_screen(
                data.get(
                    "username"
                )
            )

        else:

            messagebox.showerror(
                "Login Failed",
                data.get(
                    "message"
                )
            )

    # --------------------------------------------------------
    # JOIN ROOM
    # --------------------------------------------------------

    elif message_type == "joined":

        current_room = data.get(
            "room",
            ""
        )

        room_label.config(
            text=f"Room: {current_room}"
        )

        room_entry.delete(
            0,
            tk.END
        )

        clear_chat()

        append_chat(
            f"--- Joined {current_room} ---"
        )

        history = data.get(
            "history",
            []
        )

        if history:

            append_chat(
                "--- Previous Messages ---"
            )

            for item in history:

                append_chat(
                    f"[{item['timestamp']}] "
                    f"{item['username']}: "
                    f"{item['message']}"
                )

            append_chat(
                "--- End History ---"
            )

    # --------------------------------------------------------
    # NORMAL MESSAGE
    # --------------------------------------------------------

    elif message_type == "message":

        username = data.get(
            "username",
            ""
        )

        message = data.get(
            "message",
            ""
        )

        timestamp = data.get(
            "timestamp",
            ""
        )

        append_chat(
            f"[{timestamp}] "
            f"{username}: {message}"
        )

        notify_new_message(
            username
        )

    # --------------------------------------------------------
    # SYSTEM MESSAGE
    # --------------------------------------------------------

    elif message_type == "system":

        append_chat(
            f"[SYSTEM] {data.get('message', '')}"
        )

    # --------------------------------------------------------
    # ERROR
    # --------------------------------------------------------

    elif message_type == "error":

        messagebox.showerror(
            "Server Error",
            data.get(
                "message",
                "Unknown error"
            )
        )


# ============================================================
# RECEIVE THREAD
# ============================================================

def receive_messages():
    global connected

    buffer = ""

    try:
        while connected:

            data = client_socket.recv(
                4096
            )

            if not data:
                break

            buffer += data.decode(
                "utf-8"
            )

            while "\n" in buffer:

                line, buffer = buffer.split(
                    "\n",
                    1
                )

                if not line.strip():
                    continue

                try:
                    message = json.loads(
                        line
                    )

                    root.after(
                        0,
                        process_server_message,
                        message
                    )

                except json.JSONDecodeError:
                    pass

    except OSError:
        pass

    finally:
        connected = False

        root.after(
            0,
            show_disconnected
        )


# ============================================================
# DISCONNECTED
# ============================================================

def show_disconnected():
    status_label.config(
        text="Disconnected from server",
        fg="red"
    )


# ============================================================
# CLOSE APPLICATION
# ============================================================

def close_application():
    global connected

    if connected:

        send_json({
            "type": "disconnect"
        })

    connected = False

    try:
        client_socket.close()

    except (AttributeError, OSError):
        pass

    root.destroy()


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "OIBSIP Chat Application"
)

root.geometry(
    "750x650"
)

root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# ============================================================
# STATUS
# ============================================================

status_label = tk.Label(
    root,
    text="Connecting...",
    font=("Arial", 9)
)

status_label.pack(
    pady=5
)


# ============================================================
# LOGIN FRAME
# ============================================================

login_frame = tk.Frame(
    root
)

login_frame.pack(
    expand=True
)


title_label = tk.Label(
    login_frame,
    text="Chat Application",
    font=("Arial", 25, "bold")
)

title_label.pack(
    pady=15
)


subtitle_label = tk.Label(
    login_frame,
    text="Login or create an account",
    font=("Arial", 11)
)

subtitle_label.pack(
    pady=5
)


tk.Label(
    login_frame,
    text="Username:",
    font=("Arial", 11)
).pack(
    pady=(20, 5)
)


username_entry = tk.Entry(
    login_frame,
    width=30,
    font=("Arial", 12)
)

username_entry.pack()


tk.Label(
    login_frame,
    text="Password:",
    font=("Arial", 11)
).pack(
    pady=(15, 5)
)


password_entry = tk.Entry(
    login_frame,
    width=30,
    font=("Arial", 12),
    show="*"
)

password_entry.pack()


login_button = tk.Button(
    login_frame,
    text="Login",
    width=15,
    command=login
)

login_button.pack(
    pady=(20, 5)
)


register_button = tk.Button(
    login_frame,
    text="Register",
    width=15,
    command=register
)

register_button.pack(
    pady=5
)


# ============================================================
# CHAT FRAME
# ============================================================

chat_frame = tk.Frame(
    root
)


top_frame = tk.Frame(
    chat_frame
)

top_frame.pack(
    fill="x",
    padx=10,
    pady=5
)


user_label = tk.Label(
    top_frame,
    text="",
    font=("Arial", 10, "bold")
)

user_label.pack(
    side="left"
)


room_label = tk.Label(
    top_frame,
    text="Room: --",
    font=("Arial", 10, "bold")
)

room_label.pack(
    side="right"
)


# ============================================================
# ROOM CONTROLS
# ============================================================

room_frame = tk.Frame(
    chat_frame
)

room_frame.pack(
    fill="x",
    padx=10,
    pady=5
)


room_entry = tk.Entry(
    room_frame,
    width=25
)

room_entry.pack(
    side="left",
    padx=5
)


join_button = tk.Button(
    room_frame,
    text="Join / Create Room",
    command=join_room
)

join_button.pack(
    side="left",
    padx=5
)


general_button = tk.Button(
    room_frame,
    text="General",
    command=lambda: join_room(
        "General"
    )
)

general_button.pack(
    side="left",
    padx=5
)


python_button = tk.Button(
    room_frame,
    text="Python",
    command=lambda: join_room(
        "Python"
    )
)

python_button.pack(
    side="left",
    padx=5
)


# ============================================================
# CHAT AREA
# ============================================================

chat_text = tk.Text(
    chat_frame,
    state="disabled",
    wrap="word",
    font=("Consolas", 11)
)

chat_text.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


# ============================================================
# EMOJI BAR
# ============================================================

emoji_frame = tk.Frame(
    chat_frame
)

emoji_frame.pack(
    fill="x",
    padx=10
)


emojis = [
    "😀",
    "😂",
    "❤️",
    "👍",
    "🎉"
]


for emoji in emojis:

    button = tk.Button(
        emoji_frame,
        text=emoji,
        width=3,
        command=lambda value=emoji:
            add_emoji(value)
    )

    button.pack(
        side="left",
        padx=2
    )


# ============================================================
# MESSAGE BOX
# ============================================================

message_frame = tk.Frame(
    chat_frame
)

message_frame.pack(
    fill="x",
    padx=10,
    pady=10
)


message_entry = tk.Entry(
    message_frame,
    font=("Arial", 11)
)

message_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(0, 5)
)


message_entry.bind(
    "<Return>",
    send_message
)


send_button = tk.Button(
    message_frame,
    text="Send",
    width=10,
    command=send_message
)

send_button.pack(
    side="right"
)


# ============================================================
# CONNECT
# ============================================================

root.after(
    300,
    connect_to_server
)


root.mainloop()