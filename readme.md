# Vocodio 🎧📚

[A little video of the project](https://github.com/Achotna/Vocodio/blob/main/static/video/Vocodio.mp4)

Vocodio is a web application built with Python and Flask that helps users learn vocabulary through automatically generated audio lessons.

Users can create vocabulary lists manually, import Excel files, or generate vocabulary automatically with AI. They can then listen to bilingual audio lessons generated locally using open-source text-to-speech technology.

---

## Features

- User authentication system (register/login/logout)
- Import vocabulary from Excel files
- Add vocabulary manually
- AI-generated vocabulary lists using Ollama and Qwen
- Automatic audio generation using Piper TTS
- Multiple supported languages and voices
- Configurable pauses and repetitions
- Download generated audio lessons
- SQLite database for storing users and vocabulary
- Automatic audio concatenation with pydub
- Open-source AI and text-to-speech tools

---

## Technologies Used 🛠️

### Backend

- Python
- Flask

### Database

- SQLite
- SQLAlchemy

### AI

- Ollama
- Qwen3

### Audio Processing

- Piper TTS
- pydub
- FFmpeg

### Authentication

- Flask-Login
- Flask-Bcrypt
- Flask-WTF

---

## Project Structure 📁

```text
Vocodio/
│
├── static/
│   ├── images/
│   ├── video/
│   ├── script.js
│   ├── style.css
│   └── audio/
│       └── final/
│
├── templates/
│   ├── download_audio.html
│   ├── home.html
│   ├── index.html
│   ├── login.html
│   └── register.html
│
├── uploads/
│
├── audio/
│   ├── words/
│   ├── translations/
│   └── silence/
│
├── main.py
├── requirements.txt
├── users.db
└── vocab.db
```

---

## Installation ⚙️

### 1. Clone the repository

```bash
git clone https://github.com/Achotna/Vocodio.git
cd Vocodio
```

---

### 2. Create a virtual environment

Python 3.12 is recommended.

```bash
python -m venv .venv
```

Activate it:

#### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

#### Windows Command Prompt

```cmd
.venv\Scripts\activate.bat
```

#### macOS / Linux

```bash
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Install Ollama 🤖

Vocodio uses Ollama to run an open-source language model locally.

Download Ollama:

https://ollama.com/download

After installation, download the Qwen model:

```bash
ollama pull qwen3:4b-instruct
```

Check that the model is installed:

```bash
ollama list
```

You should see:

```text
qwen3:4b-instruct
```

You can test it with:

```bash
ollama run qwen3:4b-instruct
```

Ollama normally runs in the background and provides a local API that Vocodio uses to generate vocabulary.

---

## Piper Text-to-Speech 🔊

Vocodio uses Piper TTS for local text-to-speech generation.

Piper is installed with the Python dependencies:

```bash
pip install piper-tts
```

The required voice models are downloaded automatically when they are first used.

---

## Install FFmpeg 🎵

FFmpeg is required by pydub to process and export audio files.

### Windows

You can install FFmpeg with Winget:

```powershell
winget install Gyan.FFmpeg
```

After installation, restart your terminal.

Verify the installation:

```bash
ffmpeg -version
```

If FFmpeg is correctly installed, information about the installed FFmpeg version will be displayed.

---

## Environment Variables 🔑

Create a `.env` file in the project root:

```env
SECRET_KEY=your_secret_key
```

The `.env` file should not be uploaded to GitHub.

Add it to `.gitignore`:

```gitignore
.env
```

---

## Running the Application 🚀

Make sure:

1. Your virtual environment is activated.
2. Ollama is installed and running.
3. The Qwen model is installed.
4. FFmpeg is installed.

Then start Vocodio.

### Option 1

```bash
python main.py
```

### Option 2

```bash
python -m flask --app main run
```

For Flask debug mode:

```bash
python -m flask --app main run --debug
```

The application will normally be available at:

```text
http://127.0.0.1:5000
```

---

## Supported Languages 🌍

Vocodio currently supports:

- English
- French
- Spanish
- German
- Italian
- Portuguese
- Russian
- Japanese
- Korean
- Hindi
- Arabic
- Dutch
- Chinese Mandarin

Voice availability depends on the Piper models available for each language.

---

## How It Works 🎵

1. Add vocabulary manually, import it from Excel, or generate it using AI.
2. Choose:
   - Source language
   - Translation language
   - Voice gender
   - Pause duration
   - Number of repetitions
3. Select the vocabulary you want to include.
4. Click the button update settings.
5. Generate the audio lesson.
6. Listen to or download the final MP3 file.

The generated audio follows this structure:

```text
Word → Pause → Translation → Beep → Next word
```

The sequence can be repeated several times depending on the user's settings.

---

## AI Vocabulary Generation 🤖

Vocodio can automatically generate vocabulary based on a theme.

The model runs locally through Ollama.

---

## Excel File Format 📊

The Excel file must contain exactly two columns.

Example:

| lang1 | lang2 |
|------|------|
| hello | bonjour |
| cat | chat |
| water | eau |

The first column contains the words in the target language and the second column contains their translations.

---

## Requirements 📋

Main requirements include:

```text
Python 3.12
Flask
SQLite
SQLAlchemy
Ollama
Qwen3
Piper TTS
pydub
FFmpeg
pandas
openpyxl
```

All required Python packages are listed in `requirements.txt`.

Install them with:

```bash
pip install -r requirements.txt
```

---

## Authors 👨‍💻

Created by **Antonina Savchenko and Elisa Salignon**.

---

## License 📄

This project is licensed under the MIT License.
