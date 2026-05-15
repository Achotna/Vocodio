# Vocodio 🎧📚

Vocodio is a web application built with Python and Flask that helps users learn vocabulary through automatically generated audio lessons.\
Users can create vocabulary lists manually, import Excel files, or generate vocabulary automatically with AI, then listen to bilingual audio repetitions generated using Google Text-to-Speech.

---

## Features ✨

- 🔐 User authentication system (register/login/logout)
- 📂 Import vocabulary from Excel files
- ✍️ Add vocabulary manually
- 🤖 AI-generated vocabulary lists using the OpenAI API
- 🔊 Automatic audio generation with Google Cloud Text-to-Speech
- 🌍 Multiple supported languages and voices
- 🎵 Configurable pauses and repetitions
- 📥 Download generated audio lessons
- 🗄️ SQLite database for storing users and vocabulary
- 🎧 Automatic audio concatenation with pydub

---

## Technologies Used 🛠️

### Backend

- Python
- Flask

### Database

- SQLite
- SQLAlchemy

### AI

- OpenAI API

### Audio Processing

- Google Cloud Text-to-Speech
- pydub
- ffmpeg

### Authentication

- Flask-Login
- Flask-Bcrypt
- Flask-WTF

---

## Project Structure 📁

```bash
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
│   ├── silence/
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
git clone https://github.com/yourusername/vocodio.git
cd vocodio
```

---

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Install ffmpeg (required for pydub)

ffmpeg is required for audio processing with pydub.

Installation tutorial:\
[https://youtu.be/K7znsMo\_48I?si=HDwBQhz1esU0IP1](https://youtu.be/K7znsMo_48I?si=HDwBQhz1esU0IP1)\_

You can verify installation with:

```bash
ffmpeg -version
```

---

## Environment Variables 🔑

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
```

---

## Google Cloud Text-to-Speech Setup ☁️

1. Create a Google Cloud project
2. Enable the Text-to-Speech API
3. Create a service account
4. Download the JSON credentials file
5. Rename it:

```bash
tts_service_account.json
```

6. Place it in the root folder of the project

---

## Running the Application 🚀

### First launch

#### Windows PowerShell

```powershell
$env:FLASK_APP = "main.py"
$env:FLASK_DEBUG = "1"
python -m flask run
```

Or simply:

```bash
python main.py
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

---

## How It Works 🎵

1. Add vocabulary manually, with Excel, or AI generation
2. Choose:
   - Languages
   - Voice gender
   - Pause duration
   - Number of repetitions
3. Generate audio
4. Download the final MP3 lesson

The generated audio follows this structure:

```text
Word → Pause → Translation → Beep → Next word
```

---

## Excel File Format 📊

Your Excel file must contain exactly 2 columns:

| lang1 | lang2   |
| ----- | ------- |
| hello | bonjour |
| cat   | chat    |

##

---

## Authors 👨‍💻

Created by Antonina Savchenko, Elisa Salignon and Zoé Schmalz

Passionate about programming, AI, and educational technologies.

---

## License 📄

This project is licensed under the MIT License.

