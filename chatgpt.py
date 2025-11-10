"""
This module provides functions to interact with the OpenAI API for chat and voice synthesis, including streaming responses and memory integration.
Functions:
    - get_openai_settings(settings_file: str = "settings.json"):
        Loads OpenAI API credentials and model settings from a JSON file, validates the API key, and returns the client and model information.
    - chat(client: openai.OpenAI=None, description: str=None, text_model: str=None, user_input: str=None, name: str=None, useMemory: bool=True) -> str:
        Sends a chat request to the OpenAI API using the provided client and model settings, optionally including previous chat memory, and returns the generated response text.
    - voice(client: openai.OpenAI=None, text: str=None, name: str="speech") -> None:
        Generates an audio file from the provided text using OpenAI's text-to-speech (TTS) API and saves it to the specified file.
    - stream_chat(client: openai.OpenAI=None, description: str=None, text_model: str=None, user_input: str=None, name: str=None, useMemory: bool=True) -> str:
        Streams chat responses from the OpenAI API in real-time, processes each segment for voice synthesis and audio conversion in background threads, and returns the concatenated response text.
    - Requires a valid OpenAI API key and appropriate model settings in 'settings.json'.
    - Integrates with external modules for memory management and audio conversion.
    - Designed for interactive applications with real-time feedback and audio output.
"""

import openai
import json
import os
from memory import get_memory

#imports---------------------------------------------------------------

def get_openai_settings(settings_file: str = "settings.json"):
    """_summary_
    gets the needed info for openai api uses from the .json, checks if the api key is valid and creates a model name.
    
    Args:
        settings_file (str, optional): _description_. Defaults to "settings.json".

    Returns:
        tuple (client,description,text_model,name):  _description_ | client: openAI client object| description: model description | text_model: openAI's text model name | name: name of the model
    """
    #check if the settings file exists
    
    try:
        with open(settings_file, "r") as f:
            pass
    except FileNotFoundError:
        assert False, f"File does not exist: {settings_file}"
        
    # Opening user api_key and description settings form json
    with open(settings_file, "r") as f:
            settings = json.load(f)

    #gets the needed info for openai api uses from the .json
    client = openai.OpenAI(api_key=settings["user"]["openAI_apiKey"])
    description = "\n".join(settings["model_description"])
    text_model = settings["model_settings"]["openAI_text_model"]
    name = os.path.splitext(settings["model_files"]["name"])[0]
    
    #Makes a request to see if the api_key is valid
    try:
        response = client.responses.create(
            model="gpt-5-nano", #least expensive model
            instructions=" ",
            input=" ",
            max_output_tokens=16 #minimum tokrn value
        )
        print("API key is valid!")
    except Exception as e:
        assert False, f"An error occurred: {e}"
    
    return client,description,text_model,name

def chat(client: openai.OpenAI=None, description: str=None,text_model: str=None,user_input: str=None,name : str = None,useMemory : bool = True) -> str:
    
    #assertions
    if client == None:
        assert False, "missing api_key"
    elif description == None:
        assert False, "missing description"
    elif text_model == None:
        assert False, "missing model"
    elif user_input == None or user_input == "":
        assert False, "missing user input"
    
     #send a request with user texts to openai
    if useMemory == True:
        response = client.responses.create(
        model=text_model,
        instructions=description,
        input=[
        {
            "role": "assistant",
            "content": get_memory("chatlogs",name)
        },
        {
            "role": "user",
            "content": user_input
        }],
        reasoning={"effort": "minimal"}, #for max speed
        )
    else:
        response = client.responses.create(
        model=text_model,
        instructions=description,
        input=[
        {
            "role": "user",
            "content": user_input
        }],
        reasoning={"effort": "minimal"},
        )
    text = response.output_text
    print(text)
    
    return text



def voice(client: openai.OpenAI=None, text: str=None,name : str = "speech") -> None:
    """_summary_
    Makes an audio file with the openAI's tts
    Args:
        client (openai.OpenAI): _description_. The api_key found in the .json file should use '_get_openai_settings()'.
        text (str): _description_. The text to be used for the tts should be made by 'chat()'.
        name (str): _description_. The name of the model used to make the audio file. Found in the .json file should use '_get_openai_settings()'. defaults to 'speech.wav'

    Output:
        "./audio_input/{name}.wav": _description_. The audio made from openAi tts
        
    """
    if client == None:
        assert False, "missing api_key"
    if text == None:
        assert False, "missing text for tts"
        
    #with output text creates a tss with openai-tts
    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        instructions="Speak like a tsundere but not too angry more like in a moking way. Speak only in english even foreign words",
    ) as response:
        response.stream_to_file(f"./audio_input/{name}.wav")


def stream_chat_voice(client: openai.OpenAI=None, description: str=None,text_model: str=None,user_input: str=None,name : str = None,useMemory : bool = True) -> str:
    """
    Streams chat responses from an OpenAI client, processes the output in real-time, and generates and converts voice audio for each response segment.
        client (openai.OpenAI): The OpenAI client instance to use for generating responses. Must not be None.
        description (str): System instructions or description for the assistant. Must not be None.
        text_model (str): The model name to use for generating responses. Must not be None.
        user_input (str): The user's input message. Must not be None or empty.
        name (str): The name used for audio file naming and memory retrieval.
        useMemory (bool): Whether to include previous chat logs in the prompt. Defaults to True.
    Returns:
        str: The concatenated text output generated by the model.
    Raises:
        AssertionError: If any of the required arguments (`client`, `description`, `text_model`, or `user_input`) are missing or invalid.
        - Streams and prints model output in real-time.
        - For each line of output, generates a voice audio file and processes it in a background thread.
        - Calls external functions for voice synthesis and audio conversion.
        - May read from and write to files in './audio_input/' and './audio_output/' directories.
    Notes:
        - Needs the rvc settings loaded with 'load_rvc_settings()' before the calling of this function or else it will not work
        - Designed for interactive or streaming applications where immediate feedback and audio output are desired.
    """
    #assertions
    if client == None:
        assert False, "missing api_key"
    elif description == None:
        assert False, "missing description"
    elif text_model == None:
        assert False, "missing model"
    elif user_input == None or user_input == "":
        assert False, "missing user input"
    
    #imports
    from rvc_converter import convertToAI
    import threading
    
    #--------------------Functions needed to be in a thread-----------------------------
    
    class BackgroundTask:
        """
        A class to run a function as a background task in a separate thread.
        Args:
            func (callable): The function to execute in the background.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        Methods:
            start():
                Starts the background task if it is not already running.
        Example:
            def my_task(x, y):
                print(x + y)
            task = BackgroundTask(my_task, 2, 3)
            task.start()
        """
        def __init__(self, func, *args, **kwargs):
            self.func = func
            self.args = args
            self.kwargs = kwargs
            self._thread = None

        def _run(self):
            self.func(*self.args, **self.kwargs)  # run once

        def start(self):
            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(target=self._run, daemon=True)
                self._thread.start()
                print("Background task started")

    def start_voice(text: list,i,client:openai.OpenAI=None,name: str = None):
        """
        Generates and converts a voice audio file from a given text input.

        Side Effects:
            - Calls the `voice` function to generate a voice audio file from the specified text.
            - Prints status messages to the console.
            - Calls the `convertToAI` function to process the generated audio file.
            - Saves audio files in the './audio_input/' and './audio_output/' directories.
        """
        voice(client,text[i],f"{name}{i}") # create a voice with tts
        print("voice done")
        convertToAI(f"./audio_input/{name}{i}.wav",f"./audio_output/{name}{i}.wav") # converts it with rvc
        print(f"-------convertion {i} done-------")
        
    #-----------------------------------Main script----------------------------------------------
    if useMemory == True:    
        # creates a stream of text using the memory in the memory file for the model and user input
        stream = client.responses.create(
            model=text_model,
            instructions=description,
            input=[
            {
                "role": "assistant",
                "content": get_memory("chatlogs",name)
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
            reasoning={"effort": "minimal"},
            stream=True
        )
    else:
        # creates a stream of text only with user input
        stream = client.responses.create(
            model=text_model,
            instructions=description,
            input=[
            {
                "role": "user",
                "content": user_input
            }
        ],
            reasoning={"effort": "minimal"}, #for max speed
            stream=True
        )

    # global variables needed for real time convertion
    texts = []
    temp_text = ""
    nb = 0

    # loop for real time convertion
    for event in stream:
        if event.type == "response.output_text.delta":
            # checks every characters in the stream
            for char in event.delta:
                temp_text += char # adds it to a temporary memory
                if char == '\n': # checks if the sentence can be cutted without causing the tts model to sound weird
                    if temp_text == '\n': # avoid empty soundfiles
                        temp_text = ""
                        continue
                    else: # converts the text in memory, resets it and add it to the returned value of the function: 'texts'
                        print("[-----------append text------------")
                        print(repr(temp_text))
                        print("-----------append text------------]")
                        texts.append(temp_text+'\n')
                        thread = BackgroundTask(start_voice,texts,nb,client,name)
                        thread.start()
                        temp_text = ""
                        nb += 1
        # When stream completed converts the text in memory with the remaining characters and add it to the returned value
        elif event.type == "response.completed":
            print("[-----------append text------------")
            print(repr(temp_text))
            print("-----------append text------------]")
            texts.append(temp_text+'\n')
            thread = BackgroundTask(start_voice,texts,nb,client,name)
            thread.start()
            print("--- Stream completed ---")
            nb += 1
            
        elif event.type == "response.error":
            print(f"\n[Error] {event.error}")


    text = "".join(texts) # combines the segmented script into a single string
    return text,nb

