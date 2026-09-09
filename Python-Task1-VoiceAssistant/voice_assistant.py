import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import smtplib
import os
import re
import threading
import subprocess
import requests

from email.message import EmailMessage
from urllib.parse import quote_plus
from nltk.tokenize import wordpunct_tokenize


# ============================================================
# TEXT TO SPEECH
# ============================================================

def speak(text):
    print(f"Assistant: {text}")

    try:
        engine = pyttsx3.init("sapi5")
        engine.setProperty("volume", 1.0)
        engine.setProperty("rate", 170)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

    except Exception as e:
        print("Voice Error:", e)


# ============================================================
# LISTEN TO USER
# ============================================================

def listen_command():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:

            print("\nListening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.8
            )

            audio = recognizer.listen(
                source,
                timeout=6,
                phrase_time_limit=10
            )

        command = recognizer.recognize_google(audio)

        print("You:", command)

        return command.lower().strip()

    except sr.WaitTimeoutError:
        speak("I did not hear anything. Please try again.")
        return ""

    except sr.UnknownValueError:
        speak("Sorry, I could not understand you. Please repeat.")
        return ""

    except sr.RequestError:
        speak(
            "Speech recognition service is currently unavailable."
        )
        return ""

    except Exception as e:
        print("Microphone Error:", e)
        speak("There was a problem accessing the microphone.")
        return ""


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(command):

    tokens = [
        word.lower()
        for word in wordpunct_tokenize(command)
    ]

    if any(
        word in tokens
        for word in ["hello", "hi", "hey"]
    ):
        return "greeting"

    if "time" in tokens:
        return "time"

    if (
        "date" in tokens
        or "day" in tokens
        or "today" in tokens
    ):
        return "date"

    if any(
        phrase in command
        for phrase in [
            "weather",
            "temperature"
        ]
    ):
        return "weather"

    if (
        "remind me" in command
        or "set reminder" in command
    ):
        return "reminder"

    if (
        "send email" in command
        or "send an email" in command
    ):
        return "email"

    if any(
        phrase in command
        for phrase in [
            "search for",
            "search",
            "google",
            "look up"
        ]
    ):
        return "search"

    if (
        command.startswith("who is")
        or command.startswith("what is")
        or command.startswith("who was")
        or command.startswith("tell me about")
    ):
        return "knowledge"

    if any(
        phrase in command
        for phrase in [
            "open youtube",
            "open google",
            "open github",
            "open notepad",
            "open calculator"
        ]
    ):
        return "custom"

    if any(
        word in tokens
        for word in [
            "exit",
            "stop",
            "bye",
            "goodbye"
        ]
    ):
        return "exit"

    return "unknown"


# ============================================================
# GREETING
# ============================================================

def greeting():

    hour = datetime.datetime.now().hour

    if hour < 12:
        greeting_text = "Good morning!"

    elif hour < 18:
        greeting_text = "Good afternoon!"

    else:
        greeting_text = "Good evening!"

    speak(
        f"{greeting_text} Hello! How can I help you?"
    )


# ============================================================
# CURRENT TIME
# ============================================================

def tell_time():

    current_time = datetime.datetime.now().strftime(
        "%I:%M %p"
    )

    speak(
        f"The current time is {current_time}"
    )


# ============================================================
# CURRENT DATE
# ============================================================

def tell_date():

    current_date = datetime.datetime.now().strftime(
        "%d %B %Y"
    )

    speak(
        f"Today's date is {current_date}"
    )


# ============================================================
# WEB SEARCH
# ============================================================

def search_web(command):

    topic = command

    remove_phrases = [
        "can you search for",
        "please search for",
        "search for",
        "search",
        "google",
        "look up"
    ]

    for phrase in remove_phrases:
        topic = topic.replace(phrase, "")

    topic = topic.strip()

    if not topic:
        speak("What would you like me to search for?")

        topic = listen_command()

    if topic:

        speak(
            f"Searching the web for {topic}"
        )

        url = (
            "https://www.google.com/search?q="
            + quote_plus(topic)
        )

        webbrowser.open(url)

    else:
        speak(
            "I could not get the search topic."
        )


# ============================================================
# LIVE WEATHER
# Uses Open-Meteo API - no API key required
# ============================================================

def weather_code_description(code):

    weather_codes = {
        0: "clear sky",
        1: "mainly clear",
        2: "partly cloudy",
        3: "overcast",
        45: "foggy",
        48: "foggy",
        51: "light drizzle",
        53: "moderate drizzle",
        55: "heavy drizzle",
        61: "light rain",
        63: "moderate rain",
        65: "heavy rain",
        71: "light snow",
        73: "moderate snow",
        75: "heavy snow",
        80: "rain showers",
        81: "rain showers",
        82: "heavy rain showers",
        95: "thunderstorm",
        96: "thunderstorm with hail",
        99: "heavy thunderstorm with hail"
    }

    return weather_codes.get(
        code,
        "unknown weather conditions"
    )


def get_weather(command):

    city = command

    city = city.replace(
        "what is the weather in",
        ""
    )

    city = city.replace(
        "what's the weather in",
        ""
    )

    city = city.replace(
        "weather in",
        ""
    )

    city = city.replace(
        "temperature in",
        ""
    )

    city = city.replace(
        "weather",
        ""
    )

    city = city.strip()

    if not city:
        speak("Please tell me the city name.")

        city = listen_command()

    if not city:
        return

    try:

        speak(
            f"Checking the weather in {city}"
        )

        geo_url = (
            "https://geocoding-api.open-meteo.com/"
            "v1/search"
        )

        geo_response = requests.get(
            geo_url,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        results = geo_data.get("results")

        if not results:
            speak(
                f"Sorry, I could not find {city}."
            )
            return

        location = results[0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        location_name = location.get(
            "name",
            city
        )

        weather_url = (
            "https://api.open-meteo.com/v1/forecast"
        )

        weather_response = requests.get(
            weather_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "weather_code,"
                    "wind_speed_10m"
                )
            },
            timeout=10
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = weather_data["current"]

        temperature = current["temperature_2m"]

        weather_code = current["weather_code"]

        wind_speed = current["wind_speed_10m"]

        condition = weather_code_description(
            weather_code
        )

        speak(
            f"The current weather in "
            f"{location_name} is {condition}. "
            f"The temperature is "
            f"{temperature} degrees Celsius "
            f"and the wind speed is "
            f"{wind_speed} kilometers per hour."
        )

    except requests.RequestException:
        speak(
            "Sorry, I could not connect "
            "to the weather service."
        )

    except Exception as e:
        print("Weather Error:", e)

        speak(
            "Sorry, I could not get "
            "the weather information."
        )


# ============================================================
# REMINDER
# Example:
# Remind me in 1 minute to drink water
# ============================================================

def reminder_alert(message):

    print("\nREMINDER:", message)

    speak(
        f"Reminder. {message}"
    )


def set_reminder(command):

    pattern = (
        r"remind me in\s+(\d+)\s*"
        r"(second|seconds|minute|minutes|hour|hours)"
        r"\s+to\s+(.+)"
    )

    match = re.search(
        pattern,
        command
    )

    if not match:

        speak(
            "Please say the reminder like, "
            "remind me in 1 minute to drink water."
        )

        return

    amount = int(match.group(1))

    unit = match.group(2)

    message = match.group(3)

    if "second" in unit:
        seconds = amount

    elif "minute" in unit:
        seconds = amount * 60

    else:
        seconds = amount * 3600

    timer = threading.Timer(
        seconds,
        reminder_alert,
        args=[message]
    )

    timer.daemon = True

    timer.start()

    speak(
        f"Reminder set for {amount} "
        f"{unit} to {message}."
    )


# ============================================================
# EMAIL
#
# Set environment variables before using:
#
# EMAIL_ADDRESS
# EMAIL_APP_PASSWORD
#
# Gmail users should use an App Password.
# ============================================================

def send_email():

    sender_email = os.getenv(
        "EMAIL_ADDRESS"
    )

    app_password = os.getenv(
        "EMAIL_APP_PASSWORD"
    )

    if not sender_email or not app_password:

        speak(
            "Email is not configured yet. "
            "Please configure the email address "
            "and app password first."
        )

        return

    speak(
        "Please say the receiver email address."
    )

    receiver_email = input(
        "Receiver Email: "
    ).strip()

    if not receiver_email:
        speak(
            "Receiver email cannot be empty."
        )
        return

    speak(
        "What is the subject?"
    )

    subject = listen_command()

    if not subject:
        subject = input(
            "Subject: "
        ).strip()

    speak(
        "What message would you like to send?"
    )

    body = listen_command()

    if not body:
        body = input(
            "Message: "
        ).strip()

    try:

        message = EmailMessage()

        message["From"] = sender_email

        message["To"] = receiver_email

        message["Subject"] = subject

        message.set_content(body)

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            smtp.login(
                sender_email,
                app_password
            )

            smtp.send_message(
                message
            )

        speak(
            "Email sent successfully."
        )

    except Exception as e:

        print("Email Error:", e)

        speak(
            "Sorry, I could not send the email."
        )


# ============================================================
# GENERAL KNOWLEDGE
# Uses Wikipedia REST API
# ============================================================

def general_knowledge(command):

    topic = command

    remove_phrases = [
        "tell me about",
        "who is",
        "who was",
        "what is"
    ]

    for phrase in remove_phrases:
        topic = topic.replace(
            phrase,
            ""
        )

    topic = topic.strip()

    if not topic:
        speak(
            "Please tell me what "
            "you want to know about."
        )
        return

    try:

        url = (
            "https://en.wikipedia.org/api/rest_v1/"
            "page/summary/"
            + quote_plus(topic)
        )

        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent":
                "OIBSIP-VoiceAssistant/1.0"
            }
        )

        if response.status_code != 200:

            speak(
                "I could not find reliable "
                "information about that topic."
            )
            return

        data = response.json()

        summary = data.get(
            "extract"
        )

        if not summary:

            speak(
                "I could not find information "
                "about that topic."
            )
            return

        # Keep spoken response short
        sentences = summary.split(".")

        short_summary = ".".join(
            sentences[:2]
        ).strip()

        if short_summary:
            short_summary += "."

        speak(short_summary)

    except requests.RequestException:

        speak(
            "I could not connect to "
            "the knowledge service."
        )

    except Exception as e:

        print(
            "Knowledge Error:",
            e
        )

        speak(
            "Sorry, I could not answer "
            "that question."
        )


# ============================================================
# CUSTOM COMMANDS
# ============================================================

def custom_commands(command):

    if "open youtube" in command:

        speak("Opening YouTube.")

        webbrowser.open(
            "https://www.youtube.com"
        )

    elif "open google" in command:

        speak("Opening Google.")

        webbrowser.open(
            "https://www.google.com"
        )

    elif "open github" in command:

        speak("Opening GitHub.")

        webbrowser.open(
            "https://github.com"
        )

    elif "open notepad" in command:

        speak("Opening Notepad.")

        try:
            subprocess.Popen(
                ["notepad.exe"]
            )
        except Exception:
            speak(
                "Unable to open Notepad."
            )

    elif "open calculator" in command:

        speak("Opening Calculator.")

        try:
            subprocess.Popen(
                ["calc.exe"]
            )
        except Exception:
            speak(
                "Unable to open Calculator."
            )


# ============================================================
# PROCESS COMMAND
# ============================================================

def process_command(command):

    intent = detect_intent(
        command
    )

    if intent == "greeting":

        greeting()

    elif intent == "time":

        tell_time()

    elif intent == "date":

        tell_date()

    elif intent == "search":

        search_web(command)

    elif intent == "weather":

        get_weather(command)

    elif intent == "reminder":

        set_reminder(command)

    elif intent == "email":

        send_email()

    elif intent == "knowledge":

        general_knowledge(command)

    elif intent == "custom":

        custom_commands(command)

    elif intent == "exit":

        speak(
            "Goodbye! Have a nice day."
        )

        return False

    else:

        speak(
            "Sorry, I did not understand "
            "that command. Please try again."
        )

    return True


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    speak(
        "Voice Assistant started."
    )

    speak(
        "You can ask me for the time, date, "
        "weather, web search, general knowledge, "
        "reminders, email, or custom commands."
    )

    while True:

        command = listen_command()

        if command:

            should_continue = process_command(
                command
            )

            if not should_continue:
                break


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":
    main()