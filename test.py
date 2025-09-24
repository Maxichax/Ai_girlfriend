from openai import OpenAI
import chatgpt
import screen
client,description,text_model,name = chatgpt.get_openai_settings()
import rvc_converter
import memory
import librosa, sounddevice
import threading
import os
import shutil
import time

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
def truc():
    a = screen.summarize_images(client,temp,name)
    memory.add_memory("screenlogs",name,a)
    
while True:
    for i in range(60):
        screen.screenshot()
        time.sleep(0.50)

    temp = screen.filter_pictures()
    thread = BackgroundTask(truc)
    thread.start()
