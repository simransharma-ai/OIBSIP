import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from io import BytesIO
import requests
import os
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

API_KEY = os.getenv("OPENWEATHER_API_KEY")

CURRENT_WEATHER_URL = (
    "https://api.openweathermap.org/data/2.5/weather"
)

FORECAST_URL = (
    "https://api.openweathermap.org/data/2.5/forecast"
)

ICON_URL = (
    "https://openweathermap.org/img/wn/{}@2x.png"
)

IP_LOCATION_URL = "https://ipinfo.io/json"


current_unit = "metric"
last_location = None


# ============================================================
# ERROR DISPLAY
# ============================================================

def show_error(message):
    error_label.config(
        text=message,
        fg="red"
    )


def clear_error():
    error_label.config(
        text=""
    )


# ============================================================
# BUILD SEARCH PARAMS
# Supports City Name or ZIP Code
# ============================================================

def build_location_params(location):
    location = location.strip()

    if location.isdigit():
        return {
            "zip": location,
            "appid": API_KEY,
            "units": current_unit
        }

    return {
        "q": location,
        "appid": API_KEY,
        "units": current_unit
    }


# ============================================================
# WEATHER ICON
# ============================================================

def display_weather_icon(icon_code):
    try:
        response = requests.get(
            ICON_URL.format(icon_code),
            timeout=10
        )

        response.raise_for_status()

        image_data = BytesIO(
            response.content
        )

        image = Image.open(
            image_data
        )

        image = image.resize(
            (90, 90)
        )

        photo = ImageTk.PhotoImage(
            image
        )

        weather_icon_label.config(
            image=photo
        )

        weather_icon_label.image = photo

    except Exception:
        weather_icon_label.config(
            image=""
        )


# ============================================================
# CURRENT WEATHER
# ============================================================

def fetch_current_weather(location):
    params = build_location_params(
        location
    )

    response = requests.get(
        CURRENT_WEATHER_URL,
        params=params,
        timeout=10
    )

    if response.status_code == 401:
        raise ValueError(
            "Invalid API key. Please check your OpenWeather API key."
        )

    if response.status_code == 404:
        raise ValueError(
            "City or ZIP code not found."
        )

    response.raise_for_status()

    return response.json()


# ============================================================
# FORECAST
# ============================================================

def fetch_forecast(location):
    params = build_location_params(
        location
    )

    response = requests.get(
        FORECAST_URL,
        params=params,
        timeout=10
    )

    if response.status_code == 401:
        raise ValueError(
            "Invalid API key."
        )

    if response.status_code == 404:
        raise ValueError(
            "Forecast location not found."
        )

    response.raise_for_status()

    return response.json()


# ============================================================
# GET WEATHER
# ============================================================

def get_weather():
    global last_location

    clear_error()

    location = city_entry.get().strip()

    if not location:
        show_error(
            "Please enter a city name or ZIP code."
        )
        return

    if not API_KEY:
        show_error(
            "OpenWeather API key is not configured."
        )
        return

    try:
        current_data = fetch_current_weather(
            location
        )

        forecast_data = fetch_forecast(
            location
        )

        last_location = location

        update_current_weather(
            current_data
        )

        update_hourly_forecast(
            forecast_data
        )

        update_daily_forecast(
            forecast_data
        )

    except requests.Timeout:
        show_error(
            "Network timeout. Please try again."
        )

    except requests.ConnectionError:
        show_error(
            "Unable to connect to the weather service."
        )

    except ValueError as error:
        show_error(
            str(error)
        )

    except requests.RequestException:
        show_error(
            "Weather service error. Please try again later."
        )

    except Exception as error:
        print(
            "Weather Error:",
            error
        )

        show_error(
            "Something went wrong while fetching weather."
        )


# ============================================================
# CURRENT WEATHER GUI
# ============================================================

def update_current_weather(data):
    city_name = data.get(
        "name",
        "Unknown"
    )

    country = data.get(
        "sys",
        {}
    ).get(
        "country",
        ""
    )

    temperature = data[
        "main"
    ][
        "temp"
    ]

    humidity = data[
        "main"
    ][
        "humidity"
    ]

    weather = data[
        "weather"
    ][0]

    description = weather[
        "description"
    ].title()

    icon_code = weather[
        "icon"
    ]

    wind_speed = data[
        "wind"
    ][
        "speed"
    ]

    location_label.config(
        text=f"{city_name}, {country}"
    )

    if current_unit == "metric":

        temperature_label.config(
            text=f"{temperature:.1f} °C"
        )

        fahrenheit = (
            temperature * 9 / 5
        ) + 32

        secondary_temperature_label.config(
            text=f"{fahrenheit:.1f} °F"
        )

        wind_label.config(
            text=f"Wind: {wind_speed:.1f} m/s"
        )

    else:

        temperature_label.config(
            text=f"{temperature:.1f} °F"
        )

        celsius = (
            temperature - 32
        ) * 5 / 9

        secondary_temperature_label.config(
            text=f"{celsius:.1f} °C"
        )

        wind_label.config(
            text=f"Wind: {wind_speed:.1f} mph"
        )

    condition_label.config(
        text=description
    )

    humidity_label.config(
        text=f"Humidity: {humidity}%"
    )

    display_weather_icon(
        icon_code
    )


# ============================================================
# NEXT 6 HOURS
# OpenWeather forecast gives 3-hour intervals
# ============================================================

def update_hourly_forecast(data):
    for widget in hourly_frame.winfo_children():
        widget.destroy()

    tk.Label(
        hourly_frame,
        text="Next 6 Hours",
        font=("Arial", 13, "bold")
    ).pack(
        pady=5
    )

    forecast_list = data.get(
        "list",
        []
    )[:2]

    if not forecast_list:
        return

    container = tk.Frame(
        hourly_frame
    )

    container.pack()

    for item in forecast_list:

        time_text = datetime.fromtimestamp(
            item["dt"]
        ).strftime(
            "%I:%M %p"
        )

        temp = item[
            "main"
        ][
            "temp"
        ]

        description = item[
            "weather"
        ][0][
            "description"
        ].title()

        if current_unit == "metric":
            temp_text = f"{temp:.1f} °C"

        else:
            temp_text = f"{temp:.1f} °F"

        card = tk.Frame(
            container,
            bd=1,
            relief="solid",
            padx=15,
            pady=8
        )

        card.pack(
            side="left",
            padx=8
        )

        tk.Label(
            card,
            text=time_text,
            font=("Arial", 10, "bold")
        ).pack()

        tk.Label(
            card,
            text=temp_text,
            font=("Arial", 11)
        ).pack()

        tk.Label(
            card,
            text=description,
            wraplength=130
        ).pack()


# ============================================================
# NEXT 5 DAYS
# ============================================================

def update_daily_forecast(data):
    for widget in daily_frame.winfo_children():
        widget.destroy()

    tk.Label(
        daily_frame,
        text="5-Day Forecast",
        font=("Arial", 13, "bold")
    ).pack(
        pady=5
    )

    forecast_list = data.get(
        "list",
        []
    )

    daily_records = {}

    for item in forecast_list:

        date_text = datetime.fromtimestamp(
            item["dt"]
        ).strftime(
            "%Y-%m-%d"
        )

        hour = datetime.fromtimestamp(
            item["dt"]
        ).hour

        if date_text not in daily_records:

            daily_records[
                date_text
            ] = item

        if 11 <= hour <= 14:

            daily_records[
                date_text
            ] = item

    selected_days = list(
        daily_records.values()
    )[:5]

    container = tk.Frame(
        daily_frame
    )

    container.pack()

    for item in selected_days:

        day = datetime.fromtimestamp(
            item["dt"]
        ).strftime(
            "%a"
        )

        temp = item[
            "main"
        ][
            "temp"
        ]

        description = item[
            "weather"
        ][0][
            "description"
        ].title()

        if current_unit == "metric":
            temp_text = f"{temp:.0f}°C"

        else:
            temp_text = f"{temp:.0f}°F"

        card = tk.Frame(
            container,
            bd=1,
            relief="solid",
            padx=12,
            pady=8
        )

        card.pack(
            side="left",
            padx=4
        )

        tk.Label(
            card,
            text=day,
            font=("Arial", 10, "bold")
        ).pack()

        tk.Label(
            card,
            text=temp_text
        ).pack()

        tk.Label(
            card,
            text=description,
            wraplength=90,
            font=("Arial", 8)
        ).pack()


# ============================================================
# UNIT TOGGLE
# ============================================================

def toggle_unit():
    global current_unit

    if current_unit == "metric":

        current_unit = "imperial"

        unit_button.config(
            text="Switch to Celsius"
        )

    else:

        current_unit = "metric"

        unit_button.config(
            text="Switch to Fahrenheit"
        )

    if last_location:

        city_entry.delete(
            0,
            tk.END
        )

        city_entry.insert(
            0,
            last_location
        )

        get_weather()


# ============================================================
# AUTOMATIC LOCATION
# Bonus Feature
# ============================================================

def detect_location():
    clear_error()

    try:
        response = requests.get(
            IP_LOCATION_URL,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        city = data.get(
            "city"
        )

        if not city:
            show_error(
                "Unable to detect your city."
            )
            return

        city_entry.delete(
            0,
            tk.END
        )

        city_entry.insert(
            0,
            city
        )

        get_weather()

    except requests.Timeout:
        show_error(
            "Location detection timed out."
        )

    except requests.RequestException:
        show_error(
            "Unable to detect location."
        )


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "Basic Weather App"
)

root.geometry(
    "850x780"
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
    text="Weather App",
    font=("Arial", 25, "bold")
)

title_label.pack(
    pady=(20, 5)
)


subtitle_label = tk.Label(
    root,
    text="Real-Time Weather & Forecast",
    font=("Arial", 11)
)

subtitle_label.pack(
    pady=(0, 15)
)


# ============================================================
# SEARCH
# ============================================================

search_frame = tk.Frame(
    root
)

search_frame.pack(
    pady=10
)


city_entry = tk.Entry(
    search_frame,
    width=30,
    font=("Arial", 13)
)

city_entry.pack(
    side="left",
    padx=5
)

city_entry.insert(
    0,
    "Delhi"
)


weather_button = tk.Button(
    search_frame,
    text="Get Weather",
    font=("Arial", 11, "bold"),
    command=get_weather
)

weather_button.pack(
    side="left",
    padx=5
)


location_button = tk.Button(
    search_frame,
    text="Use My Location",
    font=("Arial", 10),
    command=detect_location
)

location_button.pack(
    side="left",
    padx=5
)


# ============================================================
# ERROR
# ============================================================

error_label = tk.Label(
    root,
    text="",
    font=("Arial", 10)
)

error_label.pack(
    pady=5
)


# ============================================================
# CURRENT WEATHER
# ============================================================

current_frame = tk.LabelFrame(
    root,
    text="Current Weather",
    padx=20,
    pady=15
)

current_frame.pack(
    fill="x",
    padx=60,
    pady=10
)


location_label = tk.Label(
    current_frame,
    text="Search for a city",
    font=("Arial", 18, "bold")
)

location_label.pack()


weather_icon_label = tk.Label(
    current_frame
)

weather_icon_label.pack()


temperature_label = tk.Label(
    current_frame,
    text="-- °C",
    font=("Arial", 28, "bold")
)

temperature_label.pack()


secondary_temperature_label = tk.Label(
    current_frame,
    text="-- °F",
    font=("Arial", 12)
)

secondary_temperature_label.pack()


condition_label = tk.Label(
    current_frame,
    text="--",
    font=("Arial", 14)
)

condition_label.pack(
    pady=5
)


info_frame = tk.Frame(
    current_frame
)

info_frame.pack(
    pady=5
)


humidity_label = tk.Label(
    info_frame,
    text="Humidity: --",
    font=("Arial", 11)
)

humidity_label.pack(
    side="left",
    padx=20
)


wind_label = tk.Label(
    info_frame,
    text="Wind: --",
    font=("Arial", 11)
)

wind_label.pack(
    side="left",
    padx=20
)


# ============================================================
# UNIT BUTTON
# ============================================================

unit_button = tk.Button(
    root,
    text="Switch to Fahrenheit",
    command=toggle_unit
)

unit_button.pack(
    pady=5
)


# ============================================================
# HOURLY FORECAST
# ============================================================

hourly_frame = tk.LabelFrame(
    root,
    text="",
    padx=10,
    pady=10
)

hourly_frame.pack(
    fill="x",
    padx=60,
    pady=10
)


tk.Label(
    hourly_frame,
    text="Next 6 Hours",
    font=("Arial", 13, "bold")
).pack()


# ============================================================
# DAILY FORECAST
# ============================================================

daily_frame = tk.LabelFrame(
    root,
    text="",
    padx=10,
    pady=10
)

daily_frame.pack(
    fill="x",
    padx=30,
    pady=10
)


tk.Label(
    daily_frame,
    text="5-Day Forecast",
    font=("Arial", 13, "bold")
).pack()


# ============================================================
# START
# ============================================================

root.mainloop()