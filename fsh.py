import tkinter as tk
from tkinter import filedialog
import pygame
import speech_recognition as sr
import random
import os
import time
import threading
import google.generativeai as genai
import replicate
import http.server
import socketserver
import threading
import base64
import requests
# Replicate setup (replace with your API token)
replicate.Client(api_token="")

# Initialize Pygame for audio playback
pygame.mixer.init()

# Google Gemini setup (replace with your API key)
genai.configure(api_key="")
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
)
convo = model.start_chat(history=[])

# Global variables
selected_beat = None
current_filename = ""
is_recording = False

def choose_beat():
    global selected_beat
    filename = filedialog.askopenfilename(
        initialdir="./",
        title="Select a Beat",
        filetypes=(("MP3 files", "*.mp3"), ("all files", "*.*")),
    )
    selected_beat = filename
    beat_label.config(text=f"Selected Beat: {filename}")

def start_freestyle():
    global is_recording
    if not selected_beat:
        error_label.config(text="Please select a beat first!")
        return

    error_label.config(text="")
    start_button.config(state=tk.DISABLED)
    rate_button.config(state=tk.DISABLED)

    # Load and play the beat
    pygame.mixer.music.load(selected_beat)
    pygame.mixer.music.play()

    # Start recording in a separate thread
    is_recording = True
    recording_thread = threading.Thread(target=record_audio)
    recording_thread.start()

    # Monitor beat playback and process audio when finished
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    is_recording = False
    process_audio()

    start_button.config(state=tk.NORMAL)
    rate_button.config(state=tk.NORMAL)


def record_audio():
    global current_filename
    r = sr.Recognizer()

    # Save the recorded audio
    random_filename = str(random.randint(100000, 999999))
    current_filename = random_filename
    audio_file = f"freestyle_{current_filename}.wav"
    with sr.Microphone() as source:
        print("Recording started...")
        with open(audio_file, "wb") as f:
            while is_recording:
                try:
                    audio_data = r.listen(source, timeout=1)
                    f.write(audio_data.get_wav_data())
                except sr.WaitTimeoutError:
                    pass  # No audio detected within the timeout

    print("Recording finished.")


def process_audio():
    global current_filename
    audio_file = f"freestyle_{current_filename}.wav"

    # Transcribe the audio using Replicate
    output = transcribe_with_replicate(audio_file)
    text = output[0]['speaker'] + ": " + output[0]['text']

    print("Transcription: " + text)

    # Get AI feedback (using Google Gemini)
    convo.send_message(
        f"Here are some rap lyrics: {text}. Can you give me some feedback, analyzing things like rhyme scheme, flow, wordplay, and overall impression?"
    )
    feedback = convo.last.text
    print("AI Feedback: " + feedback)

    # Save freestyle and feedback to files
    save_freestyle(text, current_filename)
    save_feedback(feedback, current_filename)

def rate_premade_freestyle():
    filename = filedialog.askopenfilename(
        initialdir="./",
        title="Select a Freestyle MP3/WAV File",
        filetypes=(("Audio files", "*.mp3 *.wav"), ("all files", "*.*")),
    )

    if not filename:
        return
    
    # Transcribe the audio using Replicate
    output = transcribe_with_replicate(filename)
    text = output 
    print("Transcription: " + text)

    # Get AI feedback (using Google Gemini)
    convo.send_message(
        f"Here are some rap lyrics: {text}. Can you give me some feedback, analyzing things like rhyme scheme, flow, wordplay, and overall impression?"
    )
    feedback = convo.last.text
    print("AI Feedback: " + feedback)

    # Save feedback to a file
    save_feedback(feedback, f"feedback_for_{os.path.basename(filename)}")

def transcribe_with_replicate(audio_file):
    # Encode the audio file to base64
    with open(audio_file, "rb") as audio_content:
        encoded_audio = base64.b64encode(audio_content.read()).decode('utf-8')

    input = {
        "file": f"data:audio/wav;base64,{encoded_audio}",
        "prompt": "Transcribe this freestyle rap",
        "file_url": "",
        "num_speakers": 1
    }

    output = replicate.run(
        "thomasmol/whisper-diarization:b9fd8313c0d492bf1ce501b3d188f945389327730773ec1deb6ef233df6ea119",
        input=input
    )

    # Extract only the text from the segments
    text = ""
    for segment in output['segments']:
        text += segment['text'] + " " 

    return text.strip()   
    print(output)
    return output
def save_freestyle(text, random_filename):
    with open(f"freestyle_{random_filename}.txt", "w") as f:
        f.write(text)
    print(f"Freestyle saved to freestyle_{random_filename}.txt")


def save_feedback(feedback, random_filename):
    with open(f"feedback_{random_filename}.txt", "w") as f:
        f.write(feedback)
    print(f"Feedback saved to feedback_{random_filename}.txt")


# GUI setup
window = tk.Tk()
window.title("Freestyle Rap Practice")

# Beat selection
beat_label = tk.Label(window, text="No beat selected")
beat_label.pack()
choose_button = tk.Button(window, text="Choose Beat", command=choose_beat)
choose_button.pack()

# Start button
start_button = tk.Button(window, text="Start Freestyle", command=start_freestyle)
start_button.pack()

# Rate Premade Freestyle Button
rate_button = tk.Button(window, text="Rate Premade Freestyle", command=rate_premade_freestyle)
rate_button.pack()

# Error label (for displaying messages)
error_label = tk.Label(window, text="", fg="red")
error_label.pack()

window.mainloop()
