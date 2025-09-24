"""
This module provides functionality for speech-to-speech conversion using RVC (Retrieval-based Voice Conversion).
It initializes a global RVCInference object, loads model and conversion settings from a JSON file, and processes
audio files in a specified input directory, saving the converted results to an output directory.
Functions:
    load_rvc_settings(settings_file="./settings.json"):
        Loads RVC model and conversion parameters from a JSON settings file and applies them to the global RVCInference object.
    convertToAI():
        Converts all '.wav' audio files in the './audio_input' directory using the loaded RVC model and settings,
        saving the converted files to the './audio_output' directory.
"""
from rvc_python.infer import RVCInference
import json
#imports---------------------------------------------------------------------------

# makes the rvc object global
rvc = RVCInference(models_dir="./model",device="cuda:0")

def load_rvc_settings(settings_file="./settings.json"):
    """_summary_
    loads all the settings needed for rvc speech to speech converstion
    Args:
        settings_file (str, optional): _description_. Defaults to "./settings.json".
    """
    with open(settings_file, "r") as f:
        settings = json.load(f)
        
    rvc.load_model(model_path_or_name="models/"+settings["model_files"]["name"],
                   index_path="models/"+settings["model_files"]["index"])
    
    rvc.set_params(index_rate = settings["model_settings"]["index_rate"],
                   filter_radius = settings["model_settings"]["filter_radius"],
                   protect = settings["model_settings"]["protect"],
                   f0method = settings["model_settings"]["f0method"],
                   f0up_key = settings["model_settings"]["f0up_key"],
                   resample_sr = settings["model_settings"]["resample_sr"],
                   rms_mix_rate = settings["model_settings"]["rms_mix_rate"])
    
def convertToAI(input_path=None,output_path=None):
    """_summary_
    Using the loaded settings convert the audios with ai in '.wav' in "./audio_input" to "./audio_output"
    Can also convert a single file if the file path is specified
    """
    if input_path == None or output_path == None:
        rvc.infer_dir(input_dir="./audio_input",output_dir="./audio_output")
    else:
        rvc.infer_file(input_path,output_path)