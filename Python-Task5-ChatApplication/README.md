# Chat Application

## Overview

This project is a real-time Python Chat Application developed as part of the OASIS INFOBYTE Python Programming Internship.

The application uses socket programming to allow multiple users to communicate in real time. It includes authentication, multiple chat rooms, message history, timestamps, emoji support, notifications, and graceful disconnect handling.

## Features

### Beginner Features

- Server listens for incoming client connections
- Client connects to the server
- Real-time bidirectional messaging
- Multiple clients supported
- Messages displayed with timestamps
- Graceful client disconnect handling
- Runs locally using localhost

### Advanced Features

- Tkinter GUI chat application
- User registration and login
- Multiple chat rooms
- General and Python rooms
- Custom room creation
- SQLite message history
- Previous messages loaded when joining a room
- In-app notification for new messages
- Emoji support
- Join, leave, and disconnect notifications

## Technologies Used

- Python
- Socket Programming
- Threading
- Tkinter
- SQLite
- JSON
- Hashlib

## How to Run

### Step 1 - Start Server

```bash
python server.py