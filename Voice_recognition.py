import google.generativeai as genai
import os
import time
import speech_recognition as sr
import nltk
from nltk.tokenize import word_tokenize
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from gtts import gTTS
import playsound
from flask_sqlalchemy import SQLAlchemy
from models import db, Commodity

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Flask App
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ration_mitraa.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db.init_app(app)

# AI Chatbot Instructions
SYSTEM_INSTRUCTION = (
    "You are 'Ration Mitraa', an AI assistant for an Indian rural-based ration vending machine. "
    "Your goal is to provide clear, efficient, and context-aware responses about ration distribution, eligibility, pricing, "
    "machine operation, government schemes, and public distribution policies. "
    "Keep responses simple and understandable for rural users, and ensure relevance to ration vending services."
)

# Speech Recognition
recognizer = sr.Recognizer()

# NLP for extracting commodities and quantities
nltk.download('punkt')

# Function to Fetch & Update Stock
def update_stock(item, quantity):
    commodity = Commodity.query.filter_by(name=item).first()
    
    if commodity and commodity.stock >= quantity:
        commodity.stock -= quantity
        db.session.commit()
        return f"Stock updated! {quantity} kg of {item} dispensed. Remaining stock: {commodity.stock} kg."
    else:
        return f"Sorry, insufficient stock for {item}. Available: {commodity.stock} kg." if commodity else "Item not found."

# AI Chatbot Response with Stock Update
def ration_mitraa_chatbot(user_input):
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content([
        {"role": "user", "parts": [{"text": SYSTEM_INSTRUCTION + "\nUser Query: " + user_input}]},
    ]).text

    # Extract multiple commodities & quantities
    user_id = "demo_user"  # Replace with real authentication logic
    orders = parse_ration_request(user_input)

    if orders:
        return update_stock(user_id, orders)  # Confirm the deduction first
    
    return response


# Convert Text to Speech
def speak_response(text):
    audio_file = "static/response.mp3"
    tts = gTTS(text=text, lang="en")
    tts.save(audio_file)

    time.sleep(1)
    playsound.playsound(audio_file, True)
    os.remove(audio_file)
    return audio_file

# Capture Voice Input
def listen_to_voice():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            print(f"✅ You said: {text}")
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return None

# Routes
@app.route("/")
def home():
    return render_template("index.html")

from helpers import parse_ration_request, update_stock

def ration_mitraa_chatbot(user_input):
    user_id = "demo_user"  # Replace with actual authentication logic
    orders = parse_ration_request(user_input)  # Extract ration request details

    if orders:  
        return update_stock(user_id, orders)  # ✅ PRIORITY: Handle stock update first

    # If no valid ration request is found, use AI response
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content([
        {"role": "user", "parts": [{"text": SYSTEM_INSTRUCTION + "\nUser Query: " + user_input}]},
    ]).text

    return response  # Return AI-generated response **only if no ration request**



@app.route("/chat_voice", methods=["POST"])
def chat_voice():
    user_message = listen_to_voice()
    
    if not user_message:
        return jsonify({"response": "Sorry, could not understand your voice. Try again.", "audio": None})

    bot_reply = ration_mitraa_chatbot(user_message)
    audio_file = speak_response(bot_reply)

    return jsonify({"response": bot_reply, "audio": audio_file})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
