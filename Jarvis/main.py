import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import pywhatkit as kit
import tkinter as tk
from threading import Thread
from PIL import Image, ImageTk, ImageSequence, ImageDraw
import os

# Initialize pyttsx3 engine
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)  # Change to voices[1].id for a different voice
engine.setProperty("rate", 130)  # Slightly slower rate for clarity

# GUI setup (smaller size)
root = tk.Tk()
root.title("Jarvis AI Assistant")
root.geometry("600x600")  # Reduced size
root.config(bg="#2E3B4E")
root.resizable(False, False)

# Fonts (smaller fonts)
title_font = ("Helvetica", 18, "bold")
status_font = ("Helvetica", 12, "bold")
chat_font = ("Arial", 10)

# Title
title_label = tk.Label(
    root,
    text="Jarvis AI Assistant",
    font=title_font,
    bg="#2E3B4E",
    fg="#FFD700"
)
title_label.pack(pady=5)

# Bot animation with GIF (smaller canvas)
bot_frame = tk.Canvas(root, width=180, height=180, bg="#2E3B4E", highlightthickness=0)
bot_frame.pack(pady=10)

# Load and process GIF for circular masking
gif_image = Image.open("bot.gif")  # Replace with the path to your GIF
gif_frames = []

for frame in ImageSequence.Iterator(gif_image):
    frame = frame.resize((120, 120)).convert("RGBA")  # Smaller GIF
    mask = Image.new("L", (120, 120), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 120, 120), fill=255)
    frame.putalpha(mask)
    gif_frames.append(ImageTk.PhotoImage(frame))

gif_index = 0

# Dynamic circle color
circle_colors = ["#FFD700", "#00FF00", "#FF4500", "#1E90FF"]
color_index = 0


def update_gif():
    """Updates GIF and circle animations."""
    global gif_index, color_index
    bot_frame.delete("all")
    bot_frame.create_oval(
        30, 30, 150, 150, outline=circle_colors[color_index], width=10  # Increased width to 10
    )
    bot_frame.create_image(90, 90, image=gif_frames[gif_index])
    gif_index = (gif_index + 1) % len(gif_frames)
    color_index = (color_index + 1) % len(circle_colors)
    root.after(100, update_gif)


update_gif()

# Chat display area (smaller height)
chat_display = tk.Text(
    root,
    wrap=tk.WORD,
    width=60,
    height=15,  # Reduced height
    font=chat_font,
    bg="#1E2A37",
    fg="white",
    bd=0,
    padx=10,
    pady=10,
    state=tk.DISABLED,
)
chat_display.pack(pady=10)

# Scrollbar for chat box
scrollbar = tk.Scrollbar(root, command=chat_display.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
chat_display.config(yscrollcommand=scrollbar.set)

# Listening and recognizing status (smaller label)
status_label = tk.Label(
    root,
    text="",
    font=status_font,
    bg="#2E3B4E",
    fg="#00FF00"
)
status_label.pack(pady=5)

# Place the status label below the circle and above the chat box
status_label.pack()

def update_status(text):
    """Update the listening/recognizing status on the GUI."""
    print(f"[Status] {text}")  # Print status to the terminal
    status_label.config(text=text)
    root.update()


def speak(audio):
    """Converts text to speech and animates the circle."""
    animate_text(audio, sender="Jarvis")
    animate_circle("speaking")
    engine.say(audio)
    engine.runAndWait()


def animate_text(text, sender="Jarvis"):
    """Displays text in the chat box."""
    chat_display.config(state=tk.NORMAL)
    if sender == "User":
        chat_display.insert(tk.END, f"User: {text}\n", ("user_text",))
    else:
        chat_display.insert(tk.END, f"Jarvis: {text}\n", ("bot_text",))
    chat_display.tag_config("user_text", foreground="#FFD700", font=chat_font)
    chat_display.tag_config("bot_text", foreground="#00FF00", font=chat_font)
    chat_display.yview(tk.END)
    chat_display.config(state=tk.DISABLED)


def animate_circle(state):
    """Adds dynamic animations to the circle when listening or speaking."""
    if state == "speaking":
        circle_colors = ["#FF4500", "#FFD700", "#1E90FF", "#00FF00"]
    elif state == "listening":
        circle_colors = ["#FFD700", "#00FF00", "#1E90FF", "#FF4500"]
    else:
        return  # No animation when not speaking/listening

    # Animate the circle with changing colors
    global color_index
    for color in circle_colors:
        bot_frame.itemconfig("circle", outline=color if state == "listening" else "#2E3B4E")
        root.after(200)

def takeCommand():
    """Listens for a command and returns the recognized speech."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        update_status("Listening...")
        animate_circle("listening")
        r.pause_threshold = 1
        audio = r.listen(source)
    update_status("Recognizing...")
    try:
        query = r.recognize_google(audio)
        update_status("Recognized")
        animate_text(query, sender="User")
        print(f"[User] {query}")  # Log user query in terminal
        return query.lower()
    except Exception as e:
        update_status("Could not recognize.")
        print(f"[Error] {e}")
        return None


def wishMe():
    """Greets the user based on the time of day."""
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        speak("Good Morning!")
    elif hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("Ready to comply. What can I do for you?")

def executeQuery(query):
    """Executes commands based on user input."""
    if "hello" in query or "hi" in query:
        speak("Hello! How can I assist you today?")
    elif "how are you" in query:
        speak("I am just a bunch of code, but I am functioning perfectly. How about you?")
    elif "who are you" in query:
        speak("I am Jarvis, your AI assistant, here to help you with anything you need.")
    elif "thank you" in query:
        speak("You're welcome!")
    elif "search on youtube" in query:
        query = query.replace("search on youtube", "").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    elif "open google" in query:
        speak("What should I search?")
        query = takeCommand()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")
    elif "play song" in query:
        query = query.replace("play song", "").strip()
        kit.playonyt(query)
    elif "exit" in query or "bye" in query:
        speak("Goodbye! Have a great day!")
        root.quit()
    elif "open notepad" in query:
        os.system("notepad.exe")
        speak("Opening Notepad.")
    elif "open calculator" in query:
        os.system("calc.exe")
        speak("Opening Calculator.")
    elif "close chrome" in query:
        os.system("taskkill /f /im chrome.exe")
        speak("Closing Chrome.")
    elif "time" in query:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        speak(f"The time is {current_time}.")
    elif "date" in query:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        speak(f"Today's date is {current_date}.")
    else:
        speak("I am sorry, I didn't understand that. Could you please repeat?")

def runJarvis():
    """Runs Jarvis in a continuous loop."""
    wishMe()
    while True:
        query = takeCommand()
        if query:
            executeQuery(query)


# Start Jarvis
Thread(target=runJarvis, daemon=True).start()

root.mainloop()