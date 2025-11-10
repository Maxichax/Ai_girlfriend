from rvc_converter import *
import chatgpt
import memory
import screen
import librosa
import sounddevice
import threading
from time import sleep
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

class Model:
    #-----------Initialisation-------------

    def __init__(self,json_setting = "settings.json"):
        #- self.client
        #- self.description
        #- self.text_model
        #- self.name
        self.json_file = json_setting
        self.model_loaded = False

        self.client,self.description,self.text_model,self.name = chatgpt.get_openai_settings(json_setting)

        memory.euthanize_model(json_setting)
        memory.add_memory("chatlogs",self.name) #makes an empty memory file
    
    def update_settings(self,json_setting = None):
        if json_setting == None:
            json_setting = self.json_file
        else:
            self.json_file = json_setting

        self.client,self.description,self.text_model,self.name = chatgpt.get_openai_settings(json_setting)

    def load_model(self):
        load_rvc_settings(self.json_file)
        self.model_loaded = True
    def unload_model(self):
        unload_rvc_settings()
        self.model_loaded = False

    def delete_memory(self):
        memory.euthanize_model(self.json_file)

    def reset_cache(self,file_path):
        memory.clean_directory_cache(file_path)

    def run_stream_audio_chat(self):
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

        self.load_model()
        print("##############################\n########-Chat started-########\n##############################\n")
        print("[INFO] type ':q' to quit")
        while True:
            user = input("You: ")
            if user == ':q':
                self.unload_model
                print("[INFO] exiting chat")
                break
            self.reset_cache("./audio_input")
            self.reset_cache("./audio_output")
            
            text,nb = chatgpt.stream_chat_voice(self.client,self.description,self.text_model,user,self.name)
            play_audios(self.name,nb)
            print("---------------ALL DONE--------------")
            memory.add_memory("chatlogs",self.name,"\n[user]:"+user+"\n[You]:"+text)

    def run_chat(self):
        print("##############################\n########-Chat started-########\n##############################\n")
        print("[INFO] type ':q' to quit")
        while True:
            user = input("You: ")
            if user == ':q':
                self.unload_model
                print("[INFO] exiting chat")
                break
            print(f"{self.name} : ",end="")
            response = chatgpt.chat(self.client,self.description,self.text_model,user,self.name)
            memory.add_memory("chatlogs",self.name,response)
            print('\n')
"""
    def __str__(self):
        with open(self.json_file, "r") as f:
            settings = json.load(f)

        print(f"------{self.name}------")
        print(f"Using: {self.json_file}")
        print(f"Language model: {self.text_model}")
        print(f"model loaded in memory: {self.model_loaded}\n")
        
        print(f"------RVC settings------")
        print(f"index_rate = {settings["model_settings"]["index_rate"]}")
        print(f"filter_radius = {settings["model_settings"]["filter_radius"]}")
        print(f"protect = {settings["model_settings"]["protect"]}")
        print(f"f0method = {settings["model_settings"]["f0method"]}")
        print(f"f0up_key = {settings["model_settings"]["f0up_key"]}")
        print(f"resample_sr = {settings["model_settings"]["resample_sr"]}")
        print(f"rms_mix_rate = {settings["model_settings"]["rms_mix_rate"]}")
        
        print(f"----model description---")
        print(self.description,end="\n\n")
"""

        
    
    