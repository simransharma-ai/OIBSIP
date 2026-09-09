# Random Password Generator

## Overview

This project is a Python-based Random Password Generator developed as part of the OASIS INFOBYTE Python Programming Internship.

The application generates secure random passwords based on user-selected criteria. It includes a graphical interface, clipboard integration, password strength indication, ambiguous character exclusion, and session-only password history.

## Features

### Beginner Features

- User-defined password length
- Minimum length of 8 characters
- Uppercase letters
- Lowercase letters
- Numbers
- Symbols
- At least 2 character types required
- Input validation
- Generate multiple passwords without restarting the application

### Advanced Features

- Tkinter GUI
- Secure password generation using the `secrets` module
- Password strength indicator
- Guarantees at least one character from each selected type
- Automatic clipboard copy
- Manual Copy to Clipboard button
- Option to exclude ambiguous characters such as:
  - 0
  - O
  - 1
  - l
  - I
- Displays the last 5 generated passwords
- Password history is stored only for the current session and is not saved to a file

## Technologies Used

- Python
- Tkinter
- secrets
- string
- pyperclip

## Installation

Install the required package:

```bash
pip install -r requirements.txt