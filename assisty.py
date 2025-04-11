import subprocess
import pyaudio
import wave
import requests
import os
import time
import signal
import threading
import queue

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 8
WAKE_SECONDS = 3
AUDIO_FILE = "input.wav"
WAKE_WORD = "hey god"

# Set espeak-ng data path
os.environ["ESPEAK_DATA_PATH"] = "/usr/lib/x86_64-linux-gnu/espeak-ng-data"

# Global variables for interrupt and context
stop_event = threading.Event()
conversation = []

def record_audio(seconds):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    frames = [stream.read(CHUNK) for _ in range(0, int(RATE / CHUNK * seconds))]
    stream.stop_stream()
    stream.close()
    p.terminate()
    with wave.open(AUDIO_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    return True

def speech_to_text():
    cmd = ["./whisper.cpp/build/bin/whisper-cli", "-m", "./whisper.cpp/models/ggml-base.bin", "-f", AUDIO_FILE]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip().lower()

def get_ollama_response(text):
    context = "\n".join([f"User: {q}\nAI: {a}" for q, a in conversation[-3:]]) + f"\nUser: {text}"
    url = "http://localhost:11434/api/generate"
    payload = {"model": "llama3.1:8b", "prompt": context, "stream": False}
    response = requests.post(url, json=payload)
    return response.json()["response"]

def text_to_speech(text):
    if stop_event.is_set():
        return
    cmd = ["./piper/build/piper", "--model", "./piper_models/lessac.onnx", "--output_file", "output.wav"]
    result = subprocess.run(cmd, input=text.encode(), text=False, capture_output=True)
    if result.returncode == 0 and not stop_event.is_set():
        print(f"Speaking: {text}")
        play_process = subprocess.Popen(["aplay", "output.wav"], preexec_fn=os.setsid)
        while play_process.poll() is None and not stop_event.is_set():
            time.sleep(0.1)
        if stop_event.is_set():
            os.killpg(os.getpgid(play_process.pid), signal.SIGTERM)
    else:
        print(f"Piper error: {result.stderr}")

def interrupt_handler(signum, frame):
	print("Interrupt recieved, stopping speech...")
	stop_event.set()
	time.sleep(0.5)
	stop_event.clear()

def main():
    signal.signal(signal.SIGINT, interrupt_handler)  # Add this for Ctrl+C
    print("Assistant is listening for wake word 'Hey God'... (Ctrl+C to interrupt speech)")
    while True:
        record_audio(WAKE_SECONDS)
        text = speech_to_text()
        if WAKE_WORD in text:
            print("Wake word detected!")
            text_to_speech("Yes Master")  # Wake response
            print("Recording command... (8s)")
            record_audio(RECORD_SECONDS)
            command = speech_to_text()
            print(f"You said: {command}")
            if "exit" in command:
                print("Exiting...")
                text_to_speech("Bye Mother Fucker")
                break
            response = get_ollama_response(command)
            print(f"AI: {response}")
            conversation.append((command, response))  # Fixed indent (4 spaces)
            text_to_speech(response)
        os.remove(AUDIO_FILE)  # Fixed indent (4 spaces)
        if os.path.exists("output.wav"):
            os.remove("output.wav")
        time.sleep(0.1)

if __name__ == "__main__":
   # subprocess.Popen(["ollama", "serve"])  #uncomment to start ollama if ollama not currently running
   # time.sleep(2)                          #same as above
    main()
