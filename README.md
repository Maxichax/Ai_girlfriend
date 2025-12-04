# Work in progress may not work yet
-------------------------------------------
# Description
a simple program that generates a text and voice with chatgpt given a description
and converting the voice to your character of choice with Mangio-RVC.

## To use the program you first need to make your setting.json file in ./settings/
## And put your trained model.pth and .index trainned by Mangio-RVC in ./models/

## Run these commands in the main to start a chat session TUI
First initialize the model:
```python
yourModel = Model("./settings/yourSetting.json")
```

Simple chat no voice:
```python
yourModel.run_chat()
```

Chat with voice:
```python
yourModel.run_chat_voice()
```
