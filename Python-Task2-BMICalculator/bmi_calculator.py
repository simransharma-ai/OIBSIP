import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt


DB_NAME = "bmi_history.db"


# ============================================================
# DATABASE
# ============================================================

def create_database():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Unable to create database.\n{error}"
        )


# ============================================================
# BMI CATEGORY
# ============================================================

def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight", "blue"

    elif bmi < 25:
        return "Normal", "green"

    elif bmi < 30:
        return "Overweight", "orange"

    else:
        return "Obese", "red"


# ============================================================
# CALCULATE BMI
# ============================================================

def calculate_bmi():
    name = name_entry.get().strip()
    weight_text = weight_entry.get().strip()
    height_text = height_entry.get().strip()

    if not name:
        messagebox.showwarning(
            "Input Required",
            "Please enter your name."
        )
        return

    if not weight_text or not height_text:
        messagebox.showwarning(
            "Input Required",
            "Please enter both weight and height."
        )
        return

    try:
        weight = float(weight_text)
        height_cm = float(height_text)

        if weight <= 0 or height_cm <= 0:
            raise ValueError

        if weight > 500:
            messagebox.showwarning(
                "Invalid Weight",
                "Please enter a realistic weight."
            )
            return

        if height_cm > 300:
            messagebox.showwarning(
                "Invalid Height",
                "Please enter height in centimeters."
            )
            return

        height_m = height_cm / 100

        bmi = weight / (height_m ** 2)

        category, color = get_bmi_category(bmi)

        result_label.config(
            text=f"BMI: {bmi:.2f}"
        )

        category_label.config(
            text=f"Category: {category}",
            fg=color
        )

        # Store current result for Save button
        current_result["name"] = name
        current_result["weight"] = weight
        current_result["height"] = height_cm
        current_result["bmi"] = bmi
        current_result["category"] = category

        save_button.config(
            state="normal"
        )

    except ValueError:
        messagebox.showerror(
            "Invalid Input",
            "Weight and height must be valid positive numbers."
        )


# ============================================================
# SAVE RESULT
# ============================================================

def save_result():
    if not current_result:
        messagebox.showwarning(
            "No Result",
            "Please calculate BMI first."
        )
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        recorded_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            INSERT INTO bmi_records
            (name, weight, height, bmi, category, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            current_result["name"],
            current_result["weight"],
            current_result["height"],
            current_result["bmi"],
            current_result["category"],
            recorded_at
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Saved",
            "BMI record saved successfully."
        )

        save_button.config(
            state="disabled"
        )

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Unable to save BMI record.\n{error}"
        )


# ============================================================
# VIEW HISTORY
# ============================================================

def show_history():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id,
                name,
                weight,
                height,
                bmi,
                category,
                recorded_at
            FROM bmi_records
            ORDER BY id DESC
        """)

        records = cursor.fetchall()

        conn.close()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Unable to load history.\n{error}"
        )
        return

    history_window = tk.Toplevel(root)

    history_window.title(
        "BMI History"
    )

    history_window.geometry(
        "900x450"
    )

    title = tk.Label(
        history_window,
        text="BMI History",
        font=("Arial", 18, "bold")
    )

    title.pack(
        pady=10
    )

    frame = tk.Frame(
        history_window
    )

    frame.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    columns = (
        "ID",
        "Name",
        "Weight",
        "Height",
        "BMI",
        "Category",
        "Date"
    )

    tree = ttk.Treeview(
        frame,
        columns=columns,
        show="headings"
    )

    tree.heading(
        "ID",
        text="ID"
    )

    tree.heading(
        "Name",
        text="Name"
    )

    tree.heading(
        "Weight",
        text="Weight (kg)"
    )

    tree.heading(
        "Height",
        text="Height (cm)"
    )

    tree.heading(
        "BMI",
        text="BMI"
    )

    tree.heading(
        "Category",
        text="Category"
    )

    tree.heading(
        "Date",
        text="Date & Time"
    )

    tree.column(
        "ID",
        width=50
    )

    tree.column(
        "Name",
        width=120
    )

    tree.column(
        "Weight",
        width=90
    )

    tree.column(
        "Height",
        width=90
    )

    tree.column(
        "BMI",
        width=80
    )

    tree.column(
        "Category",
        width=100
    )

    tree.column(
        "Date",
        width=170
    )

    for record in records:
        formatted_record = (
            record[0],
            record[1],
            record[2],
            record[3],
            f"{record[4]:.2f}",
            record[5],
            record[6]
        )

        tree.insert(
            "",
            "end",
            values=formatted_record
        )

    scrollbar = ttk.Scrollbar(
        frame,
        orient="vertical",
        command=tree.yview
    )

    tree.configure(
        yscrollcommand=scrollbar.set
    )

    tree.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )


# ============================================================
# BMI TREND GRAPH
# ============================================================

def show_graph():
    name = name_entry.get().strip()

    if not name:
        messagebox.showwarning(
            "Name Required",
            "Enter the user's name to view BMI trend."
        )
        return

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT bmi, recorded_at
            FROM bmi_records
            WHERE LOWER(name) = LOWER(?)
            ORDER BY id ASC
        """, (name,))

        records = cursor.fetchall()

        conn.close()

    except sqlite3.Error as error:
        messagebox.showerror(
            "Database Error",
            f"Unable to load graph data.\n{error}"
        )
        return

    if not records:
        messagebox.showinfo(
            "No History",
            f"No BMI history found for {name}."
        )
        return

    bmi_values = [
        record[0]
        for record in records
    ]

    dates = [
        datetime.strptime(
            record[1],
            "%Y-%m-%d %H:%M:%S"
        ).strftime("%d-%m %H:%M")
        for record in records
    ]

    plt.figure(
        figsize=(9, 5)
    )

    plt.plot(
        dates,
        bmi_values,
        marker="o"
    )

    plt.title(
        f"BMI Trend - {name}"
    )

    plt.xlabel(
        "Date"
    )

    plt.ylabel(
        "BMI"
    )

    plt.xticks(
        rotation=45
    )

    plt.grid(
        True
    )

    plt.tight_layout()

    plt.show()


# ============================================================
# CLEAR
# ============================================================

def clear_fields():
    name_entry.delete(
        0,
        tk.END
    )

    weight_entry.delete(
        0,
        tk.END
    )

    height_entry.delete(
        0,
        tk.END
    )

    result_label.config(
        text="BMI: --"
    )

    category_label.config(
        text="Category: --",
        fg="black"
    )

    current_result.clear()

    save_button.config(
        state="disabled"
    )


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "BMI Calculator"
)

root.geometry(
    "520x600"
)

root.resizable(
    False,
    False
)


title_label = tk.Label(
    root,
    text="BMI Calculator",
    font=("Arial", 24, "bold")
)

title_label.pack(
    pady=20
)


subtitle_label = tk.Label(
    root,
    text="Calculate and Track Your Body Mass Index",
    font=("Arial", 11)
)

subtitle_label.pack(
    pady=(0, 20)
)


# NAME

name_label = tk.Label(
    root,
    text="Name:",
    font=("Arial", 12)
)

name_label.pack(
    pady=(10, 5)
)


name_entry = tk.Entry(
    root,
    font=("Arial", 12),
    width=30
)

name_entry.pack()


# WEIGHT

weight_label = tk.Label(
    root,
    text="Weight (kg):",
    font=("Arial", 12)
)

weight_label.pack(
    pady=(15, 5)
)


weight_entry = tk.Entry(
    root,
    font=("Arial", 12),
    width=30
)

weight_entry.pack()


# HEIGHT

height_label = tk.Label(
    root,
    text="Height (cm):",
    font=("Arial", 12)
)

height_label.pack(
    pady=(15, 5)
)


height_entry = tk.Entry(
    root,
    font=("Arial", 12),
    width=30
)

height_entry.pack()


# CALCULATE BUTTON

calculate_button = tk.Button(
    root,
    text="Calculate BMI",
    font=("Arial", 12, "bold"),
    width=20,
    command=calculate_bmi
)

calculate_button.pack(
    pady=20
)


# RESULT

result_label = tk.Label(
    root,
    text="BMI: --",
    font=("Arial", 18, "bold")
)

result_label.pack(
    pady=5
)


category_label = tk.Label(
    root,
    text="Category: --",
    font=("Arial", 15, "bold")
)

category_label.pack(
    pady=5
)


# SAVE BUTTON

save_button = tk.Button(
    root,
    text="Save Result",
    font=("Arial", 11),
    width=20,
    state="disabled",
    command=save_result
)

save_button.pack(
    pady=10
)


# HISTORY BUTTON

history_button = tk.Button(
    root,
    text="View History",
    font=("Arial", 11),
    width=20,
    command=show_history
)

history_button.pack(
    pady=5
)


# GRAPH BUTTON

graph_button = tk.Button(
    root,
    text="View BMI Trend",
    font=("Arial", 11),
    width=20,
    command=show_graph
)

graph_button.pack(
    pady=5
)


# CLEAR BUTTON

clear_button = tk.Button(
    root,
    text="Clear",
    font=("Arial", 11),
    width=20,
    command=clear_fields
)

clear_button.pack(
    pady=5
)


# Current calculated result
current_result = {}


# Create database when program starts
create_database()


# Start GUI
root.mainloop()