from flask import Flask, render_template, request, url_for, redirect
from flask_dropzone import Dropzone
import pandas as pd
from sqlalchemy import create_engine
import sqlite3
#import tts_zoe_code
import os
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.generators import Sine



# ============================#
#            SETUP            #
# ============================#

app = Flask(__name__)
app.config.update(
    UPLOAD_FOLDER="uploads/",
    #only excel files DROPZONE_ALLOWED_FILE_TYPE="xls,xlsx", 
    DROPZONE_MAX_FILE_SIZE=1024,  # MB
)
dropzone = Dropzone(app)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)



######################################## ============================ ################################################################
########################################             ZOE              ################################################################
######################################## ============================ ################################################################


# Dictionnaire des voix#############
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



#Google Text to Speech API setup

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\\Projects\\Language app\\tts_service_account.json"
client = texttospeech.TextToSpeechClient()

#
# Dossiers pour stockage audio
BASE_DIR = "audio" 
WORDS_DIR = f"{BASE_DIR}/words"
TRANS_DIR = f"{BASE_DIR}/translations"
SILENCE_DIR = f"{BASE_DIR}/silence" #delay between words, dépend du choix de l'utilisateur
FINAL_DIR = f"{BASE_DIR}/final" #audios complets, fournis à l'utilisateur

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
def concatenate_audios(audio_files, output_file, num_loops):
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
    num_loops
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
    f"{delay_seconds}_"
    f"{num_loops}.wav"
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
        final_file,
        num_loops
    )

    return final_file





######################################## ============================ ################################################################
########################################             ANTO             ################################################################
######################################## ============================ ################################################################

engine = create_engine("sqlite:///./vocab.db")


@app.route("/",methods=["GET", "POST"])
def home():

    #initialize database
    conn = sqlite3.connect("vocab.db")
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS vocab (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lang1 TEXT NOT NULL,
                lang2 TEXT NOT NULL,
                status INTEGER
            )
            """)
    conn.commit()

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
        #      insert from an exel file    #
        ####################################

        f = request.files.get("file")
        if f:
            file_name=f"{app.config['UPLOAD_FOLDER']}/{f.filename}"
            f.save(file_name)

            data = pd.read_excel(file_name)
            data.columns = ["lang1", "lang2"]
            data["status"] = 1  #is included in the audio by default
            print(data.head())

            #initialize database
            data.to_sql('vocab', con=engine, if_exists='append', index=False)

        #add new word
        word = request.form.get("word")
        translation= request.form.get("translation")
        if word and translation:
            print("New word", word)
            print("New translation", translation)  
            #new entry
            new = {"lang1": word, "lang2": translation, "status": 1}
            new_data = pd.DataFrame([new])
            #check for duplicates
            existing_data = pd.read_sql("SELECT * FROM vocab", engine)
            new_data_to_insert = new_data[~new_data['lang1'].isin(existing_data['lang1'])]
            #insert 
            new_data_to_insert.to_sql("vocab", con=engine, if_exists="append", index=False)

        #resultat verif#####################################################################
        cursor.execute("SELECT * FROM vocab")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        conn.commit()
        ###################################################################################



        ####################################
        #         clear database           #
        ####################################

        clear= request.form.get("clear")
        if clear:
            cursor.execute("DELETE FROM vocab")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='vocab'")
            print('database cleared')
            conn.commit()


        ####################################
        #          upadate status          #
        ####################################

        update = request.form.get("update_settings")
        if update:
            status_list = []
            for i in range(1, len(rows)+1):
                check = request.form.get(f"check_{i}")
                word_id = request.form.get(f"word_id_{i}")
                status_list.append(1 if check else 0)
                new_status = 1 if check else 0
                cursor.execute("UPDATE vocab SET status = ? WHERE id = ?", (new_status, word_id))
            conn.commit()
            print(status_list)


        ####################################
        #     pause duration settings      #
        ####################################
        #pause_duration = request.form.get("pause_duration")
        #if pause_duration:
            #pause_duration = float(pause_duration)
            #print(f"Pause duration set to {pause_duration} s")


        ####################################
        #      gender_voice setting        #
        ####################################
        #gender_voice = request.form.get("gender_voice") 
        #if gender_voice:
            #gender_voice = str(gender_voice)
            #print(f"Gender voice: {gender_voice}")


        ####################################
        #        num_loops setting         #
        ####################################
        #num_loops = request.form.get("num_loops")
        #if num_loops:  
            #num_loops = int(num_loops)
            #print(f"Number of loops set to: {num_loops}")

#Language switch setting



################################################################################################################################################################""
        
        

        audio_generate = request.form.get("audio_generate")
        if audio_generate:
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
            df = pd.read_sql("SELECT lang1 AS word, lang2 AS translation FROM vocab WHERE status=1", engine)


            final_audio_all = AudioSegment.empty()
            for _ in range(num_loops): #nb de repetitions de chaque sequence
                #Génération audios complets pour chaque entrée => à adapter pour la BDD
                final_audio_all = AudioSegment.empty()
                bip = Sine(500).to_audio_segment(duration=300)

                for i, (index, row) in enumerate(df.iterrows()):
                    word = row["word"]
                    translation = row["translation"] 
                    
                    #check if the user has chosen num_loops, if not set to 1
                    #num_loops = int(request.form.get("num_loops", 1))

                    #Audio pour une ligne
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
                        index=index + 1,
                        num_loops=num_loops
                    )

                    #Ajout du segment mot à l'audio final
                    final_audio_all += AudioSegment.from_wav(final_audio_path)

                    #Ajout du bip entre les mots
                    if i < len(df) - 1:
                        final_audio_all += bip

            #Export de l'audio final complet
            final_audio_all.export(
                f"{FINAL_DIR}/final_output.mp3",
                format="mp3"
            )
            print('Audio generation completed. File saved as final_output.mp3')
                                    
        #Display database content
        cursor.execute("SELECT * FROM vocab")
        rows = cursor.fetchall()
        conn.close()

    


    return render_template('index.html', rows=rows, pause_duration=pause_duration, gender_voice=gender_voice, num_loops=num_loops, language1=language1, language2=language2)





if __name__ == "__main__":
    app.run(debug=True)


#$env:FLASK_APP = "main.py"
#$env:FLASK_DEBUG = "1"
#python -m flask run