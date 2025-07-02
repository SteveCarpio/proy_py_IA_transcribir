# pip install vosk pydub
# pip install ffmpeg-python
# https://alphacephei.com/vosk/models   # -- descargar el modelos  (por ejemplo “vosk-model-small-es-0.42”).
# Descomprime el archivo ZIP y copiar la carpeta en una ruta y ponerlo en el programa
# Agregar al path la ruta con la carpeta ..../bin del directorio zapeado. 

import os
from vosk import Model, KaldiRecognizer
import wave
from pydub import AudioSegment

def convert_to_wav(audio_path):
    # Convierte cualquier formato a WAV PCM 16kHz mono
    sound = AudioSegment.from_file(audio_path)
    sound = sound.set_channels(1).set_frame_rate(16000)
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
                results.append(rec.Result())
        results.append(rec.FinalResult())
    os.remove(wav_path)
    return "\n".join(results)

if __name__ == "__main__":
    audio_file = "C:\\MisCompilados\\audios\\Paco.m4a"  # o .wav, .ogg, etc
    model_dir = "C:\\Users\\scarpio\\Documents\\GitHub\\proy_py_pdf_lector\\model\\vosk-model-small-es-0.42" 
    texto = transcribe(audio_file, model_dir)
    print(texto)