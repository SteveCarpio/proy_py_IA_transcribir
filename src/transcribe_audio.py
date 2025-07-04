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

def resumir_ollama(texto, modelo="mistral"):
    url = "http://localhost:11434/api/generate"
    prompt = (
        "Créame un resumen profesional del siguiente texto que está escrito en español."
        "Crea un listado muy breve de los puntos hablados."
        "Hazlo claro, sintético y solo con la información importante."
        "Al final traduce solo el resumen en varios idiomas: Inglés, Francés y Italiano."
        
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

def procesar_audio(audio_file, model_dir, modelo_ollama="mistral"):
    # Transcribir
    texto = transcribe(audio_file, model_dir)
    # Guardar transcripción
    base, _ = os.path.splitext(audio_file)
    txt_path = base + ".txt"
    save_txt(texto, txt_path)
    print(f"\nTranscripción guardada en: {txt_path}")
    print(f"{texto}")

    # Resumir
    resumen = resumir_ollama(texto, modelo=modelo_ollama)
    resumen_path = base + "_resumen.txt"
    save_txt(resumen, resumen_path)
    print(f"\nResumen guardado en: {resumen_path}")
    print(f"{resumen}")

if __name__ == "__main__":
    audio_file = "C:\\MisCompilados\\audios\\Reunion.m4a"
   #model_dir  = "C:\\MisCompilados\\utils\\model\\vosk-model-small-es-0.42"
    model_dir  = "C:\\MisCompilados\\utils\\model\\vosk-model-es-0.42"
    procesar_audio(audio_file, model_dir, modelo_ollama="mistral")