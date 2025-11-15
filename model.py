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
import wave
import random
import struct

class BackgroundTask:
    """
    Makes a function in an other thread\n
    exemple_ | exemple = BackgroundTask(function,var1=var,var2=var,var3=var)
    """
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
        #- self.voice_description
        #- self.text_model
        #- self.name
        #- self.stream
        #- self.reasoning
        self.json_file = json_setting
        self.model_loaded = False

        self.client,self.description,self.voice_description,self.text_model,self.name,self.stream,self.reasoning = chatgpt.get_openai_settings(json_setting)

        memory.euthanize_model(json_setting)
        memory.add_memory("chatlogs",self.name) #makes an empty memory file
    

    #################################################################################
    ################################## UTILITY ######################################
    #################################################################################


    def update_settings(self,json_setting = None):

        if json_setting == None:
            json_setting = self.json_file
        else:
            self.json_file = json_setting

        self.client,self.description,self.text_model,self.name = chatgpt.get_openai_settings(json_setting)

    def delete_memory(self):
        memory.euthanize_model(self.json_file)

    def reset_audio_cache(self):
        memory.clean_directory_cache("./audio_input")
        memory.clean_directory_cache("./audio_output")


    def load_model(self):
        load_rvc_settings(self.json_file)
        
        with wave.open("./audio_input/model_loader.wav","wb") as f:
            f.setnchannels(1)         # mono
            f.setsampwidth(2)         # 16-bit
            f.setframerate(44100)

            # Generate gibberish: random 16-bit signed samples
            frames = b"".join(
                struct.pack("<h", random.randint(-32768, 32767))
                for _ in range(44100)
            )

            f.writeframes(frames)

        convertToAI("./audio_input/model_loader.wav","./audio_output/model_loader.wav")
        #self.reset_audio_cache()
        
        self.model_loaded = True

    def unload_model(self):
        unload_rvc_settings()
        self.model_loaded = False

    def run_stream_audio_chat(self):
        """
        [DEPRECATED]
        """
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
            self.reset_audio_cache()
            
            text,nb = chatgpt.stream_chat_voice(self.client,self.description,self.text_model,user,self.name)
            play_audios(self.name,nb)
            print("---------------ALL DONE--------------")
            memory.add_memory("chatlogs",self.name,"\n[user]:"+user+"\n[You]:"+text)


    ##########################################################################################
    ################################## CHAT FUNCTIONS ########################################
    ##########################################################################################


    def run_chat(self,additional_instruction: str = ""):
        print("##############################\n########-Chat started-########\n##############################\n")
        print("[INFO] type ':q' to quit")
        while True:
            user = input("You: ")
            if user == ':q':
                print("[INFO] exiting chat")
                break
            print(f"{self.name} : ",end="")
            if self.stream == True:
                temp_str = ""
                response = chatgpt.chat(self.client,self.description,self.text_model,user,self.name,streaming = self.stream,additional_instructions=additional_instruction,reason=self.reasoning)
                while True:
                    try:
                        temp = next(response)
                        print(temp,end="")
                        temp_str += temp
                    except StopIteration:
                        memory.add_memory("chatlogs",self.name,temp_str)
                        break
            else:
                response = chatgpt.chat(self.client,self.description,self.text_model,user,self.name,streaming = self.stream)
                print(response)
                memory.add_memory("chatlogs",self.name,response)
            print('\n')
    



    def run_chat_voice(self,additional_instruction: str = ""):
        self.load_model()
        print("##############################\n########-Chat started-########\n##############################\n")
        print("[INFO] type ':q' to quit")
        while True:
            user = input("You: ")
            if user == ':q':
                print("[INFO] exiting chat")
                break
            print(f"{self.name} : ",end="")
            if self.stream == True:
                temp_str = ""
                response = chatgpt.chat(self.client,self.description,self.text_model,user,self.name,streaming = self.stream,additional_instructions=additional_instruction,reason=self.reasoning)
                while True:
                    try:
                        temp = next(response)
                        print(temp,end="")
                        temp_str += temp
                    except StopIteration:
                        memory.add_memory("chatlogs",self.name,f"[USER] {user}\n[YOU] {temp_str}\n")
                        break
            else:
                response = chatgpt.chat(self.client,self.description,self.text_model,user,self.name,streaming = self.stream)
                print(response)
                memory.add_memory("chatlogs",self.name,f"[USER] {user}\n[YOU] {response}\n")


            print("\n///////////////Generating voice...///////////////")
            self.reset_audio_cache()
            if self.stream == True:
                print("[INFO] not made yet for stream using conventional method")
                chatgpt.voice(self.client,temp_str,self.voice_description,self.name)
                convertToAI()
                audio, sr = librosa.load(f"./audio_output/{self.name}.wav", sr=None)
                sounddevice.play(audio, sr)
                sounddevice.wait()
            else:
                chatgpt.voice(self.client,response,self.voice_description,self.name)
                convertToAI()
                audio, sr = librosa.load(f"./audio_output/{self.name}.wav", sr=None)
                sounddevice.play(audio, sr)
                sounddevice.wait()
        
    
    