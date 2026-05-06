from flask import Flask, render_template, request, url_for, redirect
from flask_dropzone import Dropzone
import pandas as pd
from sqlalchemy import create_engine
import sqlite3
import os
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.generators import Sine
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask import send_file
import ast
from openai import OpenAI
from dotenv import load_dotenv
import glob

 

# ============================#
#            API_AI           #
# ============================#
#Chargement clé API
load_dotenv()
client_ai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Fonction génération automatique
def chat_with_gpt(theme, nb_words, lang1, lang2):
    try:
        response = client_ai.chat.completions.create(
            model="gpt-5-mini", 
            messages=[{
                "role": "user",
                "content": f"Generate a Python list of dictionaries for vocabulary learning. Requirements: Each dictionary must have exactly two keys: 'lang1' and 'lang2', 'lang1' = {lang1}, 'lang2' = {lang2}, Theme: {theme}, Number of word pairs: {nb_words}, Words must be simple, common, and relevant to the theme, No duplicates Output format example: [{{'lang1': ...., 'lang2': ...}},{{'lang1': ..., 'lang2': ....}}] Return ONLY valid Python code (no explanations, no comments)"}])
        chat_response = response.choices[0].message.content

        return chat_response

    except Exception as e:
        print("API ERROR:", e)
        return None 



# ============================#
#            SETUP            #
# ============================#
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "dev-key")
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config.update(
    UPLOAD_FOLDER="uploads/",
    #only excel files DROPZONE_ALLOWED_FILE_TYPE="xls,xlsx", 
    DROPZONE_MAX_FILE_SIZE=1024,  # MB
)
dropzone = Dropzone(app)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)




class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Register")

    def validate_username(self, username):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", (username.data,))
        existing = cursor.fetchone()
        conn.close()
        if existing:
            raise ValidationError("Username already exists")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)])
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)])
    submit = SubmitField("Login")


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return User(*row)
    return None




######################################## ============================ ################################################################
########################################       Génération audio       ################################################################
######################################## ============================ ################################################################


# Dictionnaire des voix
VOICES = {
    "cmn-CN": { # Chinois Mandarin (Chine)
        "female": "cmn-TW-Standard-A",
        "male": "cmn-CN-Wavenet-B"
    },
    "en-GB": { #Anglais (Royaume-Uni)
        "female": "en-GB-Chirp3-HD-Leda",
        "male": "en-GB-Chirp3-HD-Alnilam"
    },
    "fr-FR": { # Français
        "female": "fr-FR-Chirp-HD-O",
        "male": "fr-FR-Chirp3-HD-Algenib"
    },
    "es-ES": { # Espagnol
        "female": "es-ES-Chirp-HD-F",
        "male": "es-ES-Chirp-HD-D"
    },
    "de-DE": {  # Allemand
        "female": "de-DE-Chirp3-HD-Aoede",
        "male": "de-DE-Chirp3-HD-Charon"
    },
    "it-IT": {  # Italien
        "female": "it-IT-Chirp3-HD-Aoede",
        "male": "it-IT-Chirp3-HD-Charon"
    },
    "pt-BR": {  # Portugais (Brésil)
        "female": "pt-BR-Chirp3-HD-Aoede",
        "male": "pt-BR-Chirp3-HD-Charon"
    },
    "ru-RU": {  # Russe
        "female": "ru-RU-Chirp3-HD-Aoede",
        "male": "ru-RU-Chirp3-HD-Charon"
    },
    "ja-JP": {  # Japonais
        "female": "ja-JP-Chirp3-HD-Autonoe",
        "male": "ja-JP-Chirp3-HD-Charon"
    },
    "ko-KR": {  # Coréen
        "female": "ko-KR-Chirp3-HD-Aoede",
        "male": "ko-KR-Chirp3-HD-Charon"
    },
    "hi-IN": {  # Hindi
        "female": "hi-IN-Chirp3-HD-Aoede",
        "male": "hi-IN-Chirp3-HD-Charon"
    },
    "ar-XA": {  # Arabe
        "female": "ar-XA-Chirp3-HD-Achernar",
        "male": "ar-XA-Chirp3-HD-Alnilam"
    },
    "nl-NL": {  # Néerlandais
        "female": "nl-NL-Chirp3-HD-Aoede",
        "male": "nl-NL-Chirp3-HD-Charon"
    }
}

#Nettoyage du dossier audio avant chaque nouvelle génération
def clear_audio_cache():
    folders = [WORDS_DIR, TRANS_DIR, SILENCE_DIR, FINAL_DIR]

    for folder in folders:
        files = glob.glob(os.path.join(folder, "*"))
        for f in files:
            try:
                os.remove(f)
            except Exception as e:
                print("Skip file:", f, e)



#Google Text to Speech clé API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "E:\\Projects\\Vocodio\\tts_service_account.json"
client = texttospeech.TextToSpeechClient()

# Dossiers pour stockage audio
BASE_DIR = "audio" 
WORDS_DIR = f"{BASE_DIR}/words"
TRANS_DIR = f"{BASE_DIR}/translations"
SILENCE_DIR = f"{BASE_DIR}/silence" #delay between words, dépend du choix de l'utilisateur
FINAL_DIR = "static/audio/final" #audios complets, fournis à l'utilisateur


for d in [WORDS_DIR, TRANS_DIR, SILENCE_DIR, FINAL_DIR]:
    os.makedirs(d, exist_ok=True) #pour ne pas avoir d'erreur si le dossier existe déjà 


# Fonction générique Text-to-Speech
def text_to_speech(
    text: str,
    output_file: str,
    language_code: str,
    voice_name: str
):
    if not text.strip():
        raise ValueError("Input text is empty.")

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open(output_file, "wb") as out:
        out.write(response.audio_content)


# Génération du silence
def generate_silence(duration_seconds: float) -> str:
    filename = f"{SILENCE_DIR}/{duration_seconds:.1f}s.wav"

    if os.path.exists(filename):
        return filename

    silence = AudioSegment.silent(
        duration=int(duration_seconds * 1000)
    )

    silence.export(filename, format="wav")
    return filename


# Assemblage des audios
def concatenate_audios(audio_files, output_file):
    final_audio = AudioSegment.empty()
     
    for file in audio_files:
        final_audio += AudioSegment.from_wav(file)

    final_audio.export(output_file, format="wav")


# Génération audio pour une entrée
def generate_audio_for_entry(
    entry,
    delay_seconds,
    target_lang,
    translation_lang,
    target_gender,
    translation_gender,
    index,
):
    word = entry["word"]
    translation = entry["translation"]

    target_voice_name = VOICES[target_lang][target_gender]
    translation_voice_name = VOICES[translation_lang][translation_gender]

    target_file = (
        f"{WORDS_DIR}/{index}_{target_lang}_{target_gender}.wav"
    )

    translation_file = (
        f"{TRANS_DIR}/{index}_{translation_lang}_{translation_gender}.wav"
    )

    final_file = (
    f"{FINAL_DIR}/"
    f"{index}_"
    f"{target_lang}_{target_gender}_"
    f"{translation_lang}_{translation_gender}_"
    f"{delay_seconds}.wav"
)

    if os.path.exists(final_file):
        return final_file

    if not os.path.exists(target_file):
        text_to_speech(
            word,
            target_file,
            target_lang,
            target_voice_name
        )

    if not os.path.exists(translation_file):
        text_to_speech(
            translation,
            translation_file,
            translation_lang,
            translation_voice_name
        )

    silence_file = generate_silence(delay_seconds)

    concatenate_audios(
        [target_file, silence_file, translation_file],
        final_file,)

    return final_file



######################################## ============================ ################################################################
########################################     Comptes utilisateurs     ################################################################
######################################## ============================ ################################################################

#creation compte
@app.route("/register", methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (form.username.data, hashed_password)
            )
        except sqlite3.IntegrityError:
            return "Username already exists"
        conn.commit()
        conn.close()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


#se connecter
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    message_login = None
    if form.validate_on_submit():
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM users WHERE username=?", (form.username.data,))
        row = cursor.fetchone()
        conn.close()
        if row:
            user = User(*row)
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                message_login = "Password is incorrect"
        else:
            message_login = "User not found"
    return render_template('login.html', form=form, message_login=message_login)

#se déconncter
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login')) 


#page d'accueil
@app.route("/")
def welcome():
    return render_template('home.html')


######################################## ============================ ################################################################
########################################        Base de donnée        ################################################################
######################################## ============================ ################################################################
def initialize_databases():
    #initialize database vocab
    engine = create_engine("sqlite:///./vocab.db")
    conn = sqlite3.connect("vocab.db")
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS vocab (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                lang1 TEXT NOT NULL,
                lang2 TEXT NOT NULL,
                status INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """)
    conn.commit()
    print("Vocab database initialized")

    #initialise db users
    engine = create_engine("sqlite:///./users.db")
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            """)
    conn.commit()
    print("Users database initialized")




######################################## ============================ ################################################################
########################################            Vocodio           ################################################################
######################################## ============================ ################################################################

@app.route("/home",methods=["GET", "POST"])
@login_required
def index():
    print(f"Current user: {current_user.username}")

    engine = create_engine("sqlite:///./vocab.db")

   #inizialization of settings
    rows = []
    pause_duration = float(request.form.get("pause_duration", 2.0))
    gender_voice = request.form.get("gender_voice", "female")
    num_loops = int(request.form.get("num_loops", 1))
    language1 = request.form.get("language1", "en-GB")
    language2 = request.form.get("language2", "en-GB")

    #insert data into database
    if request.method == "POST":


        ####################################
        #              EXCEL               #
        ####################################

        f = request.files.get("file")
        print("File received:", f)
        if f:
            file_name=f"{app.config['UPLOAD_FOLDER']}/{f.filename}"
            f.save(file_name)
            data = pd.read_excel(file_name)
            data.columns = ["lang1", "lang2"]
            data["status"] = 1  #is included in the audio by default
            print('Fichier excel :')
            print(data.head())
            #insert
            data["user_id"] = current_user.id
            data.to_sql('vocab', con=engine, if_exists='append', index=False)
            print("Data from excel file inserted into database")


        ####################################
        #              MANUEL              #
        ####################################
        word = request.form.get("word")
        translation= request.form.get("translation")
        if word and translation:
            print("New word", word)
            print("New translation", translation)  
            #new entry
            new = {"user_id": current_user.id, "lang1": word, "lang2": translation, "status": 1}
            new_data = pd.DataFrame([new])
            new_data['user_id'] = current_user.id
            #check for duplicates > lang1
            existing_data = pd.read_sql("SELECT * FROM vocab WHERE user_id = ?", engine, params=(current_user.id,))
            new_data_to_insert = new_data[~new_data['lang1'].isin(existing_data['lang1'])]
            #insert 
            new_data_to_insert.to_sql("vocab", con=engine, if_exists="append", index=False)

        #resultat verif#####################################################################
        conn = sqlite3.connect("vocab.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vocab WHERE user_id = ?", (current_user.id,))
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        conn.commit()
        ###################################################################################


        ####################################
        #              AUTO                #
        ####################################
        vocab_auto = request.form.get("vocab_auto")
        if vocab_auto:
            theme = request.form.get("theme")
            print('theme ', theme)
            nb_words = request.form.get("nb_words")
            print('nb_word ', nb_words)

            reponse_ai = chat_with_gpt(theme, nb_words, language1, language2)

            if not reponse_ai:
                print("GPT failed")

            data = ast.literal_eval(reponse_ai)
            print(data)
            new_entry_df = pd.DataFrame(data)
            new_entry_df["user_id"] = current_user.id
            #check for duplicates > lang1
            existing_data_2 = pd.read_sql("SELECT * FROM vocab WHERE user_id = ?", engine, params=(current_user.id,))
            new_entry_df_to_insert = new_entry_df[~new_entry_df['lang1'].isin(existing_data_2['lang1'])]
            #insert
            new_entry_df_to_insert.to_sql("vocab", con=engine, if_exists="append", index=False)
            print("Auto vocab inserted")






        ############################################################################################################################
        #         clear database           #########################################################################################
        ############################################################################################################################

        clear= request.form.get("clear")
        if clear:
            # vocab
            conn_vocab = sqlite3.connect("vocab.db")
            cursor_vocab = conn_vocab.cursor()
            cursor_vocab.execute("DELETE FROM vocab")
            cursor_vocab.execute("DELETE FROM sqlite_sequence WHERE name='vocab'")
            conn_vocab.commit()
            conn_vocab.close()

            # users
            conn_users = sqlite3.connect("users.db")
            cursor_users = conn_users.cursor()
            cursor_users.execute("DELETE FROM users")
            cursor_users.execute("DELETE FROM sqlite_sequence WHERE name='users'")
            conn_users.commit()
            conn_users.close()

            # audios
            conn_audios = sqlite3.connect("audios.db")
            cursor_audios = conn_audios.cursor()
            cursor_audios.execute("DELETE FROM audios")
            cursor_audios.execute("DELETE FROM sqlite_sequence WHERE name='audios'")
            conn_audios.commit()
            conn_audios.close()

            print("Databases cleared")






        ####################################
        #           update status          #
        ####################################

        update = request.form.get("update_settings")
        if update:
            i = 1
            while True:
                word_id = request.form.get(f"word_id_{i}")
                if not word_id:
                    break
                # If checkbox unchecked, get() returns None → default to 0
                new_status = int(request.form.get(f"check_{i}", 0))
                cursor.execute("UPDATE vocab SET status = ? WHERE id = ?", (new_status, word_id))
                i += 1
            conn.commit()
        


        audio_generate = request.form.get("audio_generate")
        if audio_generate:
            clear_audio_cache()
            # ============================
            # Configuration utilisateur
            # ============================
            USER_CONFIG = {
                "target_lang": language1,
                "translation_lang": language2,
                "target_gender": gender_voice,
                "translation_gender": gender_voice,
                "delay_seconds": pause_duration
            }

            # ============================
            # Génération audio complet
            # ============================

            #Récupération des données depuis la BDD
            df = pd.read_sql(f"SELECT lang1 AS word, lang2 AS translation FROM vocab WHERE status=1 AND user_id = {current_user.id}", engine)


            final_audio_all = AudioSegment.empty()
            for _ in range(num_loops): #nb de repetitions de chaque sequence
                #Génération audios complets pour chaque entrée => à adapter pour la BDD
                bip = Sine(500).to_audio_segment(duration=300)
                silence_bip=AudioSegment.silent(duration=700)

                for i, row in enumerate(df.itertuples(), start=1):
                    word = row.word
                    translation = row.translation

                    final_audio_path = generate_audio_for_entry(
                        entry={
                            "word": word,
                            "translation": translation
                        },
                        delay_seconds=USER_CONFIG["delay_seconds"],
                        target_lang=USER_CONFIG["target_lang"],
                        translation_lang=USER_CONFIG["translation_lang"],
                        target_gender=USER_CONFIG["target_gender"],
                        translation_gender=USER_CONFIG["translation_gender"],
                        index=i,  # clean index
                    )

                    #Ajout du segment mot à l'audio final
                    final_audio_all += AudioSegment.from_wav(final_audio_path)

                    #Ajout du bip entre les mots
                    if i < len(df):
                        final_audio_all = final_audio_all + silence_bip + bip + silence_bip

            #Export de l'audio final complet
            final_audio_all.export(f"{FINAL_DIR}/final_output.mp3",format="mp3")
            print('Audio generation completed. File saved as final_output.mp3')
                                    
        #Display database content
        cursor.execute("SELECT id, lang1, lang2, status FROM vocab WHERE user_id = ?", (current_user.id,))
        
        rows = cursor.fetchall()
        conn.commit()
        
        print(rows)
        conn.close()

    return render_template('index.html', rows=rows, pause_duration=pause_duration, gender_voice=gender_voice, num_loops=num_loops, language1=language1, language2=language2, username=current_user.username)


#télécharger audio
@app.route('/download_audio')
def download_audio():
    if not os.path.exists("audio/final/final_output.mp3"):
        return "File not found. Generate audio first."
    else:
        return send_file("audio/final/final_output.mp3", as_attachment=True)


#run flask
if __name__ == "__main__":
    initialize_databases()
    app.run(debug=True)
    

#First time running? use this
#$env:FLASK_APP = "main.py"
#$env:FLASK_DEBUG = "1"
#python -m flask run

#activate the env
# .\.venv\Scripts\Activate.ps1    