import socket
import threading
import json
import sqlite3
import hashlib
from datetime import datetime


HOST = "127.0.0.1"
PORT = 5555
DB_NAME = "chat_app.db"

clients = []
clients_lock = threading.Lock()


# ============================================================
# DATABASE
# ============================================================

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT NOT NULL,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (
            username,
            hash_password(password)
        ))

        conn.commit()
        conn.close()

        return True, "Registration successful."

    except sqlite3.IntegrityError:
        return False, "Username already exists."

    except sqlite3.Error as error:
        return False, f"Database error: {error}"


def validate_login(username, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM users
            WHERE username = ?
            AND password = ?
        """, (
            username,
            hash_password(password)
        ))

        user = cursor.fetchone()

        conn.close()

        return user is not None

    except sqlite3.Error:
        return False


def save_message(room, username, message, timestamp):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO messages
            (room, username, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            room,
            username,
            message,
            timestamp
        ))

        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        print("Message save error:", error)


def get_message_history(room):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT username, message, timestamp
            FROM messages
            WHERE room = ?
            ORDER BY id DESC
            LIMIT 50
        """, (room,))

        records = cursor.fetchall()

        conn.close()

        records.reverse()

        return records

    except sqlite3.Error:
        return []


# ============================================================
# CLIENT SESSION
# ============================================================

class ClientSession:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.username = None
        self.room = None
        self.authenticated = False


# ============================================================
# JSON SEND
# ============================================================

def send_json(connection, data):
    try:
        message = json.dumps(
            data
        ) + "\n"

        connection.sendall(
            message.encode("utf-8")
        )

        return True

    except (ConnectionResetError, BrokenPipeError, OSError):
        return False


# ============================================================
# BROADCAST
# ============================================================

def broadcast(room, data, exclude=None):
    disconnected = []

    with clients_lock:
        current_clients = list(clients)

    for client in current_clients:

        if (
            client.authenticated
            and client.room == room
            and client is not exclude
        ):
            success = send_json(
                client.connection,
                data
            )

            if not success:
                disconnected.append(client)

    for client in disconnected:
        remove_client(client)


# ============================================================
# REMOVE CLIENT
# ============================================================

def remove_client(client):
    was_connected = False

    with clients_lock:
        if client in clients:
            clients.remove(client)
            was_connected = True

    if (
        was_connected
        and client.authenticated
        and client.room
        and client.username
    ):
        broadcast(
            client.room,
            {
                "type": "system",
                "message": (
                    f"{client.username} disconnected."
                )
            },
            exclude=client
        )

    try:
        client.connection.close()
    except OSError:
        pass


# ============================================================
# JOIN ROOM
# ============================================================

def join_room(client, room):
    room = room.strip()

    if not room:
        send_json(
            client.connection,
            {
                "type": "error",
                "message": "Room name cannot be empty."
            }
        )
        return

    old_room = client.room

    if old_room:
        broadcast(
            old_room,
            {
                "type": "system",
                "message": (
                    f"{client.username} left the room."
                )
            },
            exclude=client
        )

    client.room = room

    history = get_message_history(
        room
    )

    history_data = []

    for username, message, timestamp in history:
        history_data.append({
            "username": username,
            "message": message,
            "timestamp": timestamp
        })

    send_json(
        client.connection,
        {
            "type": "joined",
            "room": room,
            "history": history_data
        }
    )

    broadcast(
        room,
        {
            "type": "system",
            "message": (
                f"{client.username} joined the room."
            )
        },
        exclude=client
    )


# ============================================================
# PROCESS CLIENT COMMAND
# ============================================================

def process_request(client, request):
    request_type = request.get(
        "type"
    )

    # --------------------------------------------------------
    # REGISTER
    # --------------------------------------------------------

    if request_type == "register":

        username = request.get(
            "username",
            ""
        ).strip()

        password = request.get(
            "password",
            ""
        )

        if len(username) < 3:
            send_json(
                client.connection,
                {
                    "type": "register_result",
                    "success": False,
                    "message": (
                        "Username must contain at least 3 characters."
                    )
                }
            )
            return

        if len(password) < 4:
            send_json(
                client.connection,
                {
                    "type": "register_result",
                    "success": False,
                    "message": (
                        "Password must contain at least 4 characters."
                    )
                }
            )
            return

        success, message = register_user(
            username,
            password
        )

        send_json(
            client.connection,
            {
                "type": "register_result",
                "success": success,
                "message": message
            }
        )

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    elif request_type == "login":

        username = request.get(
            "username",
            ""
        ).strip()

        password = request.get(
            "password",
            ""
        )

        if validate_login(
            username,
            password
        ):
            client.username = username
            client.authenticated = True

            send_json(
                client.connection,
                {
                    "type": "login_result",
                    "success": True,
                    "username": username,
                    "message": "Login successful."
                }
            )

        else:
            send_json(
                client.connection,
                {
                    "type": "login_result",
                    "success": False,
                    "message": (
                        "Invalid username or password."
                    )
                }
            )

    # --------------------------------------------------------
    # JOIN ROOM
    # --------------------------------------------------------

    elif request_type == "join":

        if not client.authenticated:
            return

        room = request.get(
            "room",
            ""
        )

        join_room(
            client,
            room
        )

    # --------------------------------------------------------
    # MESSAGE
    # --------------------------------------------------------

    elif request_type == "message":

        if (
            not client.authenticated
            or not client.room
        ):
            return

        message = request.get(
            "message",
            ""
        ).strip()

        if not message:
            return

        timestamp = datetime.now().strftime(
            "%H:%M:%S"
        )

        save_message(
            client.room,
            client.username,
            message,
            timestamp
        )

        broadcast(
            client.room,
            {
                "type": "message",
                "username": client.username,
                "message": message,
                "timestamp": timestamp
            }
        )

    # --------------------------------------------------------
    # DISCONNECT
    # --------------------------------------------------------

    elif request_type == "disconnect":

        raise ConnectionAbortedError


# ============================================================
# HANDLE CLIENT
# ============================================================

def handle_client(client):
    print(
        f"Client connected: {client.address}"
    )

    buffer = ""

    try:
        while True:

            data = client.connection.recv(
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
                    request = json.loads(
                        line
                    )

                    process_request(
                        client,
                        request
                    )

                except json.JSONDecodeError:
                    send_json(
                        client.connection,
                        {
                            "type": "error",
                            "message": (
                                "Invalid request received."
                            )
                        }
                    )

    except (
        ConnectionResetError,
        ConnectionAbortedError,
        OSError
    ):
        pass

    finally:
        print(
            f"Client disconnected: {client.address}"
        )

        remove_client(
            client
        )


# ============================================================
# START SERVER
# ============================================================

def start_server():
    create_database()

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        (HOST, PORT)
    )

    server_socket.listen()

    print("=" * 50)
    print("OIBSIP CHAT SERVER")
    print("=" * 50)
    print(f"Server running on {HOST}:{PORT}")
    print("Waiting for clients...")
    print("Press Ctrl + C to stop the server.")
    print("=" * 50)

    try:
        while True:

            connection, address = server_socket.accept()

            client = ClientSession(
                connection,
                address
            )

            with clients_lock:
                clients.append(
                    client
                )

            thread = threading.Thread(
                target=handle_client,
                args=(client,),
                daemon=True
            )

            thread.start()

    except KeyboardInterrupt:
        print("\nServer stopped.")

    finally:

        with clients_lock:
            current_clients = list(
                clients
            )

        for client in current_clients:
            remove_client(
                client
            )

        server_socket.close()


if __name__ == "__main__":
    start_server()