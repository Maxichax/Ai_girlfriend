import os
import json
import shutil

def get_memory(type :str = "chatlogs",name : str = None) -> str:
    assert name != None or name != "", "missing model name"
    
    if type == "chatlogs":

        try:
            with open(f"./memory/{name}.txt", "r", encoding="utf-8") as memory: #returns the text in memory if it exists
                return memory.read()
        except FileNotFoundError:
            with open(f"./memory/{name}.txt", "w", encoding="utf-8") as memory: #checks if the model already has a memory if not creates it
                memory.write("")
            print(f"./memory/{name}.txt does not exists, creating file")
            return ""
    elif type == "screenlogs":
        try:
            with open(f"./memory/{name}Screen.txt", "r", encoding="utf-8") as memory: #returns the text in memory if it exists
                return memory.read()
        except FileNotFoundError:
            with open(f"./memory/{name}Screen.txt", "w", encoding="utf-8") as memory: #checks if the model already has a memory if not creates it
                memory.write("")
            print(f"./memory/{name}Screen.txt does not exists, creating file")
            return ""
        
def add_memory(type : str = "chatlogs",name : str = None,text: str = "") -> None: 
    """
    Adds new text to a memory file of the specified type and name.
    Parameters:
        type (str): The type of memory to update. Defaults to "chatlogs". Supported types are "chatlogs" and "screenlogs".
        name (str): The name of the memory file (without extension). Must not be None or empty.
        text (str): The text to append to the memory file. Defaults to an empty string.
    Raises:
        AssertionError: If 'name' is None or an empty string.
    Notes:
        - The function retrieves the existing memory content using `get_memory`, then appends the new text.
        - The memory file is stored in the "./memory/" directory with a ".txt" extension.
    """
    
    assert name != None or name != "", "missing model name"
            
    if type == "chatlogs":
        #checks if the file exists and write the text in it
        old_memory = get_memory(type,name)
        with open(f"./memory/{name}.txt", "w", encoding="utf-8") as memory:
                memory.write(old_memory + text)
        
        
    elif type == "screenlogs":
        #checks if the file exists and write the text in it
        old_memory = get_memory(type,name)
        with open(f"./memory/{name}Screen.txt", "w", encoding="utf-8") as memory:
                memory.write(old_memory + text)
        
    
    

def euthanize_model(settings_file: str = "settings.json"):
    """_summary_
    deletes the memory of the model. she loved you :(
    Args:
        settings_file (str, optional): _description_. Defaults to "settings.json".
    """
    try:
        with open(settings_file, "r") as f:
            pass
    except FileNotFoundError:
        assert False, f"File does not exist: {settings_file}"
        
    with open("settings.json", "r") as f:
        settings = json.load(f)
        
    name = os.path.splitext(settings["model_files"]["name"])[0]
    
    try:
        os.remove(f"./memory/{name}.txt")
        print(f"File /memory/{name}.txt deleted successfully. she loved you.")
    except:
        pass
    try:
        os.remove(f"./memory/{name}Screen.txt")
        print(f"File /memory/{name}Screen.txt deleted successfully.")
    except:
        pass

def clean_directory_cache(folder_path, keep_filename = ""):
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