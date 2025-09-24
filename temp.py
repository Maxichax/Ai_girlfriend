from openai import OpenAI
import chatgpt
import screen
client,description,text_model,name = chatgpt._get_openai_settings()
import rvc_converter
import memory
import librosa, sounddevice
import threading
import time
import os

#rvc_converter.load_rvc_settings()

nb = 3
def play_audios(name,nb):
    for i in range(nb):
        filename = f"./audio_output/{name}{i}.wav"
        
        it = 0
        while not os.path.exists(filename):
            time.sleep(0.5)  # sleep to avoid busy-waiting
            it += 1
            if it == 360:  # wait about 3min before break to avoid infinite loop
                break
        if it == 240:
            print(f"File: '{filename}' does not exists for more than 3min. Stopping sound playing loop")
            break

        audio, sr = librosa.load(filename, sr=None)
        print(f"-------- Playing {filename} ------------")
        sounddevice.play(audio, sr)
        sounddevice.wait()
        
play_audios(name,nb)