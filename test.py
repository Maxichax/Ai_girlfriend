import wave,struct,random


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