import tkinter as tk
from tkinter import messagebox
import string
import secrets
import pyperclip


# ============================================================
# CONSTANTS
# ============================================================

AMBIGUOUS_CHARACTERS = "0O1lI"

password_history = []


# ============================================================
# SECURE SHUFFLE
# Uses secrets instead of random
# ============================================================

def secure_shuffle(items):
    items = list(items)

    for i in range(len(items) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        items[i], items[j] = items[j], items[i]

    return "".join(items)


# ============================================================
# PASSWORD STRENGTH
# ============================================================

def get_password_strength(length, type_count):
    score = 0

    if length >= 8:
        score += 1

    if length >= 12:
        score += 1

    if length >= 16:
        score += 1

    if type_count >= 3:
        score += 1

    if type_count == 4:
        score += 1

    if score <= 2:
        return "Weak"

    elif score <= 4:
        return "Medium"

    return "Strong"


# ============================================================
# UPDATE STRENGTH DISPLAY
# ============================================================

def update_strength(password, type_count):
    if not password:
        strength_label.config(
            text="Strength: --",
            fg="black"
        )
        return

    strength = get_password_strength(
        len(password),
        type_count
    )

    if strength == "Weak":
        color = "red"

    elif strength == "Medium":
        color = "orange"

    else:
        color = "green"

    strength_label.config(
        text=f"Strength: {strength}",
        fg=color
    )


# ============================================================
# COPY PASSWORD
# ============================================================

def copy_password():
    password = password_var.get()

    if not password:
        messagebox.showwarning(
            "No Password",
            "Please generate a password first."
        )
        return

    try:
        pyperclip.copy(password)

        messagebox.showinfo(
            "Copied",
            "Password copied to clipboard."
        )

    except pyperclip.PyperclipException:
        messagebox.showerror(
            "Clipboard Error",
            "Unable to copy password to clipboard."
        )


# ============================================================
# UPDATE HISTORY
# ============================================================

def update_history(password):
    password_history.insert(
        0,
        password
    )

    # Only last 5 passwords in current session
    del password_history[5:]

    history_list.delete(
        0,
        tk.END
    )

    for index, item in enumerate(
        password_history,
        start=1
    ):
        history_list.insert(
            tk.END,
            f"{index}. {item}"
        )


# ============================================================
# GENERATE PASSWORD
# ============================================================

def generate_password():
    try:
        length = int(
            length_var.get()
        )

    except ValueError:
        messagebox.showerror(
            "Invalid Length",
            "Password length must be a number."
        )
        return

    # Minimum 8 characters
    if length < 8:
        messagebox.showerror(
            "Invalid Length",
            "Password must contain at least 8 characters."
        )
        return

    if length > 128:
        messagebox.showerror(
            "Invalid Length",
            "Password length cannot exceed 128 characters."
        )
        return

    selected_sets = []

    if uppercase_var.get():
        selected_sets.append(
            string.ascii_uppercase
        )

    if lowercase_var.get():
        selected_sets.append(
            string.ascii_lowercase
        )

    if numbers_var.get():
        selected_sets.append(
            string.digits
        )

    if symbols_var.get():
        selected_sets.append(
            string.punctuation
        )

    # Task requirement: at least 2 types
    if len(selected_sets) < 2:
        messagebox.showerror(
            "Character Types Required",
            "Please select at least 2 character types."
        )
        return

    # Remove ambiguous characters if selected
    if exclude_ambiguous_var.get():
        cleaned_sets = []

        for character_set in selected_sets:
            cleaned = "".join(
                char
                for char in character_set
                if char not in AMBIGUOUS_CHARACTERS
            )

            if cleaned:
                cleaned_sets.append(
                    cleaned
                )

        selected_sets = cleaned_sets

    if not selected_sets:
        messagebox.showerror(
            "Generation Error",
            "No valid characters are available."
        )
        return

    # Security rule:
    # Guarantee at least one character
    # from every selected type
    password_characters = []

    for character_set in selected_sets:
        password_characters.append(
            secrets.choice(character_set)
        )

    all_characters = "".join(
        selected_sets
    )

    remaining_length = (
        length - len(password_characters)
    )

    for _ in range(
        remaining_length
    ):
        password_characters.append(
            secrets.choice(all_characters)
        )

    # Secure shuffle
    password = secure_shuffle(
        password_characters
    )

    password_var.set(
        password
    )

    update_strength(
        password,
        len(selected_sets)
    )

    update_history(
        password
    )

    # Automatically copy generated password
    try:
        pyperclip.copy(
            password
        )

        clipboard_status_label.config(
            text="Copied automatically to clipboard",
            fg="green"
        )

    except pyperclip.PyperclipException:
        clipboard_status_label.config(
            text="Automatic clipboard copy failed",
            fg="red"
        )


# ============================================================
# CLEAR PASSWORD
# ============================================================

def clear_password():
    password_var.set("")

    strength_label.config(
        text="Strength: --",
        fg="black"
    )

    clipboard_status_label.config(
        text=""
    )


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "Random Password Generator"
)

root.geometry(
    "600x700"
)

root.resizable(
    False,
    False
)


# ============================================================
# TITLE
# ============================================================

title_label = tk.Label(
    root,
    text="Random Password Generator",
    font=("Arial", 22, "bold")
)

title_label.pack(
    pady=(20, 5)
)


subtitle_label = tk.Label(
    root,
    text="Generate strong and secure passwords",
    font=("Arial", 11)
)

subtitle_label.pack(
    pady=(0, 20)
)


# ============================================================
# PASSWORD LENGTH
# ============================================================

length_frame = tk.Frame(
    root
)

length_frame.pack(
    pady=10
)


length_label = tk.Label(
    length_frame,
    text="Password Length:",
    font=("Arial", 12)
)

length_label.pack(
    side="left",
    padx=5
)


length_var = tk.IntVar(
    value=12
)


length_spinbox = tk.Spinbox(
    length_frame,
    from_=8,
    to=128,
    textvariable=length_var,
    width=8,
    font=("Arial", 12)
)

length_spinbox.pack(
    side="left",
    padx=5
)


# ============================================================
# CHARACTER TYPES
# ============================================================

character_frame = tk.LabelFrame(
    root,
    text="Character Types",
    font=("Arial", 12, "bold"),
    padx=20,
    pady=10
)

character_frame.pack(
    fill="x",
    padx=60,
    pady=15
)


uppercase_var = tk.BooleanVar(
    value=True
)

lowercase_var = tk.BooleanVar(
    value=True
)

numbers_var = tk.BooleanVar(
    value=True
)

symbols_var = tk.BooleanVar(
    value=True
)


uppercase_checkbox = tk.Checkbutton(
    character_frame,
    text="Uppercase Letters (A-Z)",
    variable=uppercase_var,
    font=("Arial", 11)
)

uppercase_checkbox.pack(
    anchor="w"
)


lowercase_checkbox = tk.Checkbutton(
    character_frame,
    text="Lowercase Letters (a-z)",
    variable=lowercase_var,
    font=("Arial", 11)
)

lowercase_checkbox.pack(
    anchor="w"
)


numbers_checkbox = tk.Checkbutton(
    character_frame,
    text="Numbers (0-9)",
    variable=numbers_var,
    font=("Arial", 11)
)

numbers_checkbox.pack(
    anchor="w"
)


symbols_checkbox = tk.Checkbutton(
    character_frame,
    text="Symbols (!@#$...)",
    variable=symbols_var,
    font=("Arial", 11)
)

symbols_checkbox.pack(
    anchor="w"
)


# ============================================================
# EXCLUDE AMBIGUOUS CHARACTERS
# ============================================================

exclude_ambiguous_var = tk.BooleanVar(
    value=False
)


exclude_checkbox = tk.Checkbutton(
    root,
    text="Exclude ambiguous characters (0, O, 1, l, I)",
    variable=exclude_ambiguous_var,
    font=("Arial", 11)
)

exclude_checkbox.pack(
    pady=5
)


# ============================================================
# GENERATE BUTTON
# ============================================================

generate_button = tk.Button(
    root,
    text="Generate Password",
    font=("Arial", 12, "bold"),
    width=22,
    command=generate_password
)

generate_button.pack(
    pady=15
)


# ============================================================
# PASSWORD RESULT
# ============================================================

password_var = tk.StringVar()


password_entry = tk.Entry(
    root,
    textvariable=password_var,
    font=("Consolas", 14),
    width=38,
    justify="center",
    state="readonly"
)

password_entry.pack(
    pady=10
)


# ============================================================
# STRENGTH
# ============================================================

strength_label = tk.Label(
    root,
    text="Strength: --",
    font=("Arial", 13, "bold")
)

strength_label.pack(
    pady=5
)


clipboard_status_label = tk.Label(
    root,
    text="",
    font=("Arial", 9)
)

clipboard_status_label.pack(
    pady=3
)


# ============================================================
# COPY / CLEAR BUTTONS
# ============================================================

button_frame = tk.Frame(
    root
)

button_frame.pack(
    pady=10
)


copy_button = tk.Button(
    button_frame,
    text="Copy to Clipboard",
    width=18,
    command=copy_password
)

copy_button.pack(
    side="left",
    padx=5
)


clear_button = tk.Button(
    button_frame,
    text="Clear",
    width=12,
    command=clear_password
)

clear_button.pack(
    side="left",
    padx=5
)


# ============================================================
# PASSWORD HISTORY
# ============================================================

history_frame = tk.LabelFrame(
    root,
    text="Last 5 Generated Passwords (Current Session Only)",
    font=("Arial", 11, "bold"),
    padx=10,
    pady=10
)

history_frame.pack(
    fill="both",
    padx=45,
    pady=15
)


history_list = tk.Listbox(
    history_frame,
    width=55,
    height=5,
    font=("Consolas", 10)
)

history_list.pack()


privacy_label = tk.Label(
    root,
    text=(
        "Password history is not saved to a file or database "
        "for security."
    ),
    font=("Arial", 9),
    wraplength=500
)

privacy_label.pack(
    pady=10
)


# ============================================================
# START APPLICATION
# ============================================================

root.mainloop()