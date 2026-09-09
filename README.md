# OIBSIP - Python Programming Internship

## OASIS INFOBYTE Internship Projects

This repository contains all projects completed as part of the **OASIS INFOBYTE Python Programming Internship**.

The projects demonstrate Python programming, GUI development, database integration, API handling, secure password generation, voice processing, socket programming, and real-time communication.

---

## Tasks Completed

### Task 1 - Voice Assistant

A Python-based Voice Assistant that accepts voice commands and responds using text-to-speech.

#### Features

- Voice input using SpeechRecognition
- Text-to-speech using pyttsx3
- Greeting commands
- Current date and time
- Web search
- Live weather information
- General knowledge queries
- Reminder functionality
- Email sending support
- Custom commands
- Error handling for unrecognized speech

#### Folder

```text
Python-Task1-VoiceAssistant
````

#### Run

```bash
cd Python-Task1-VoiceAssistant
pip install -r requirements.txt
python voice_assistant.py
```

---

### Task 2 - BMI Calculator

A GUI-based BMI Calculator that calculates and stores Body Mass Index records.

#### Features

* Weight and height input
* BMI calculation
* BMI category classification
* Underweight
* Normal
* Overweight
* Obese
* Input validation
* Tkinter GUI
* SQLite database
* BMI history
* BMI trend graph
* Color-coded results
* Database error handling

#### Folder

```text
Python-Task2-BMICalculator
```

#### Run

```bash
cd Python-Task2-BMICalculator
pip install -r requirements.txt
python bmi_calculator.py
```

---

### Task 3 - Random Password Generator

A secure Python password generator with GUI and advanced password controls.

#### Features

* Custom password length
* Minimum password length validation
* Uppercase letters
* Lowercase letters
* Numbers
* Symbols
* At least two character types required
* Secure password generation using the `secrets` module
* Password strength indicator
* Automatic clipboard copy
* Manual Copy to Clipboard button
* Exclude ambiguous characters
* Last 5 generated passwords in the current session
* Password history is not saved to a file or database

#### Folder

```text
Python-Task3-RandomPasswordGenerator
```

#### Run

```bash
cd Python-Task3-RandomPasswordGenerator
pip install -r requirements.txt
python password_generator.py
```

---

### Task 4 - Basic Weather App

A Python GUI Weather App that fetches real-time weather data using the OpenWeather API.

#### Features

* Search weather by city name
* Search weather by ZIP code
* Current temperature
* Celsius and Fahrenheit support
* Humidity
* Weather condition
* Wind speed
* Weather icon
* Next 6 hours forecast
* 5-day forecast
* Celsius/Fahrenheit toggle
* Automatic location detection
* Empty input validation
* Invalid city handling
* Invalid API key handling
* Network error handling

#### Folder

```text
Python-Task4-BasicWeatherApp
```

#### API Configuration

Set your OpenWeather API key before running:

```powershell
$env:OPENWEATHER_API_KEY="YOUR_API_KEY"
```

Do not upload your API key to GitHub.

#### Run

```bash
cd Python-Task4-BasicWeatherApp
pip install -r requirements.txt
python weather_app.py
```

---

### Task 5 - Chat Application

A real-time client-server Chat Application developed using Python socket programming.

#### Features

* Server listens for incoming clients
* Client-server communication
* Real-time two-way messaging
* Multiple client support
* User registration and login
* Multiple chat rooms
* Message timestamps
* SQLite message history
* Previous messages loaded when joining a room
* Emoji support
* New message notification
* Join, leave and disconnect notifications
* Graceful disconnect handling
* Runs on localhost

#### Folder

```text
Python-Task5-ChatApplication
```

#### Run

First open the Task 5 folder:

```bash
cd Python-Task5-ChatApplication
```

Start the server:

```bash
python server.py
```

Open a second terminal and run:

```bash
python client.py
```

Open another terminal for a second user:

```bash
python client.py
```

Register/login with different usernames and join the same room to test real-time messaging.

---

## Technologies Used

* Python
* Tkinter
* SQLite
* Socket Programming
* Threading
* SpeechRecognition
* pyttsx3
* PyAudio
* Requests
* NLTK
* Matplotlib
* Pillow
* OpenWeather API
* Wikipedia REST API
* SMTP
* JSON
* Hashlib
* Secrets
* Pyperclip

---

## Repository Structure

```text
OIBSIP/
│
├── Python-Task1-VoiceAssistant/
│   ├── voice_assistant.py
│   ├── requirements.txt
│   ├── README.md
│   └── screenshots/
│
├── Python-Task2-BMICalculator/
│   ├── bmi_calculator.py
│   ├── requirements.txt
│   ├── README.md
│   └── screenshots/
│
├── Python-Task3-RandomPasswordGenerator/
│   ├── password_generator.py
│   ├── requirements.txt
│   ├── README.md
│   └── screenshots/
│
├── Python-Task4-BasicWeatherApp/
│   ├── weather_app.py
│   ├── requirements.txt
│   ├── README.md
│   └── screenshots/
│
├── Python-Task5-ChatApplication/
│   ├── server.py
│   ├── client.py
│   ├── requirements.txt
│   ├── README.md
│   └── screenshots/
│
└── README.md
```

---

## How to Run the Repository

Clone the repository:

```bash
git clone https://github.com/simransharma-ai/OIBSIP.git
```

Open the repository:

```bash
cd OIBSIP
```

Open the required task folder.

Example:

```bash
cd Python-Task1-VoiceAssistant
```

Install required dependencies:

```bash
pip install -r requirements.txt
```

Run the project using the command mentioned in the respective task section above.

---

## Security and Privacy Notes

* API keys and passwords are not stored directly in the source code.
* Environment variables are used for sensitive credentials.
* The Voice Assistant may use external speech-recognition and API services.
* Task 3 password history is stored only during the current session.
* Task 4 OpenWeather API key should never be committed to GitHub.
* Task 5 chat messages are **not end-to-end encrypted**.
* Task 5 is an educational localhost project and should not be considered production-grade secure messaging software.
* Real or sensitive passwords should not be used while testing the Chat Application.

---

## Author

**Simran Sharma**

Python Programming Internship
**OASIS INFOBYTE**

```
