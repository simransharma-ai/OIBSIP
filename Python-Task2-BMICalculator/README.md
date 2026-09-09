# BMI Calculator

## Overview

This project is a Python-based BMI Calculator developed as part of the OASIS INFOBYTE Python Programming Internship.

The application calculates Body Mass Index (BMI) using the user's weight and height, classifies the BMI category, stores records in a local SQLite database, displays BMI history, and shows BMI trends using a graph.

## Features

### Beginner Features

- Accepts user weight in kilograms
- Accepts user height in centimeters
- Calculates BMI using the formula:

  BMI = weight / height²

- Classifies BMI as:
  - Underweight
  - Normal
  - Overweight
  - Obese
- Handles invalid or missing input
- Simple graphical user interface using Tkinter

### Advanced Features

- User name based BMI records
- Save BMI results locally
- SQLite database storage
- View BMI history
- BMI trend visualization using Matplotlib
- Color-coded BMI category
- Database error handling
- Input validation
- Clear form functionality

## Technologies Used

- Python
- Tkinter
- SQLite
- Matplotlib
- datetime

## Installation

Install the required package using:

```bash
pip install -r requirements.txt