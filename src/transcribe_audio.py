# Primera vez: crear :  py -3.12 -m venv venv312
# .\venv312\Scripts\activate

# pip install pydub
# pip install vosk 
# pip install ffmpeg-python
# pip install requests
# pip freeze > requirements.txt

# https://alphacephei.com/vosk/models   # -- descargar el modelos  (por ejemplo “vosk-model-small-es-0.42”).
# Descomprime el archivo ZIP y copiar la carpeta en una ruta y ponerlo en el programa
# Agregar al path la ruta con la carpeta ..../bin del directorio zapeado..

import os
import json
from vosk import Model, KaldiRecognizer
import wave
from pydub import AudioSegment
import requests

def convert_to_wav(audio_path):
    sound = AudioSegment.from_file(audio_path)
    sound = sound.set_channels(1).set_frame_rate(16000) # (frecuencia de muestreo en Hz)
    wav_path = "temp.wav"
    sound.export(wav_path, format="wav")
    return wav_path

def transcribe(audio_path, model_path):
    wav_path = convert_to_wav(audio_path)
    model = Model(model_path)
    results = []
    with wave.open(wav_path, "rb") as wf:
        rec = KaldiRecognizer(model, wf.getframerate())
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                # Solo texto puro
                result_json = json.loads(rec.Result())
                results.append(result_json.get("text", ""))
        final_json = json.loads(rec.FinalResult())
        results.append(final_json.get("text", ""))
    os.remove(wav_path)
    return "\n".join(results).strip()

def save_txt(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def resumir_ollama(texto, modelo="llama3:instruct"):
    url = "http://localhost:11434/api/generate"
    prompt2 = (
        "Créame un acta profesional de la reunión que mantuvimos, el texto que está escrito en español y se debe respetar ese idioma."
        "Indica el día y hora de la reunión y si existe el lugar también."
        "Describe los participantes."
        "Crea un listado muy breve de los puntos hablados."
        "Si quedan puntos por hablar indícalo como puntos pendientes."
        f"\n\n{texto}\n\n"
    )

    prompt = (
    "A continuación tienes la transcripción de una reunión en español, posiblemente sin puntuación ni formato."
    "Tu tarea es redactar un acta profesional de la reunión, respetando el idioma español."
    "\n\nPor favor, sigue estas instrucciones:"
    "\n- Indica la fecha, hora y lugar de la reunión (si esos datos aparecen en el texto; si no, deja un espacio para completarlos)."
    "\n- Presenta una breve descripción de los participantes, indicando nombre completo y, si es posible, su empresa o rol."
    "\n- Haz un listado breve y claro de los puntos tratados en la reunión."
    "\n- Si quedan temas pendientes o para la próxima reunión, indícalos como 'Puntos pendientes'."
    "\n- Mantén una redacción clara, profesional y estructurada."
    "\n\nTranscripción de la reunión:"
    f"\n\n{texto}\n\n"
)

    data = {
        "model": modelo,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=data)
    response.raise_for_status()
    return response.json()["response"].strip()

def procesar_audio(audio_file, model_dir, modelo_ollama="llama3:instruct"):
    # Transcribir
    texto = transcribe(audio_file, model_dir)
    # Guardar transcripción
    base, _ = os.path.splitext(audio_file)
    txt_path = base + ".txt"
    save_txt(texto, txt_path)
    print(f"\n - Transcripción guardada en: {txt_path}")
    print(f"\n{texto}")

    # Resumir
    resumen = resumir_ollama(texto, modelo=modelo_ollama)
    resumen_path = base + "_resumen.txt"
    save_txt(resumen, resumen_path)
    print(f"\n\n - Resumen guardado en: {resumen_path}")
    print(f"\n{resumen}")

if __name__ == "__main__":
    audio_file = "C:\\MisCompilados\\audios\\REUNION.mp3"
    model_dir  = "C:\\MisCompilados\\utils\\model\\vosk-model-es-0.42"  # vosk-model-small-es-0.42
    procesar_audio(audio_file, model_dir, modelo_ollama="llama3:instruct")  #  llama3:instruct : mistral