import chatgpt
import memory
import screen
from rvc_converter import convertToAI,load_rvc_settings
import librosa
import sounddevice
import threading
from time import sleep
import os
import shutil
import time

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
        

def clean_directory(folder_path, keep_filename = ""):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Skip the file we want to keep
        if filename == keep_filename:
            continue

        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)   # remove file or symlink
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # remove directory and contents
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

class BackgroundTask:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._thread = None

    def _run(self):
        self.func(*self.args, **self.kwargs)  # run on*ce

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
            print("Background task started")
        





def run():
    client,description,text_model,name = chatgpt.get_openai_settings()
    load_rvc_settings()
    memory.euthanize_model()
    while True:
        user = input()
        clean_directory("./audio_input")
        clean_directory("./audio_output")
        
        text,nb = chatgpt.stream_chat(client,description,text_model,user,name)
        play_audios(name,nb)
        print("---------------ALL DONE--------------")
        print('You:',end="")
        memory.add_memory("chatlogs",name,"\n[user]:"+user+"\n[You]:"+text)
        
run()




