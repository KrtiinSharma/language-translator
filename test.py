import streamlit as st
import speech_recognition as sr
import tempfile
import google.generativeai as genai
import os
from pydub import AudioSegment  # Import for audio conversion
from googletrans import Translator  # Import Google Translator for language translation

# Set the provided API key
GOOGLE_API_KEY = "API-KEY"  # Ensure this key is valid

# Configure the Generative AI API
genai.configure(api_key=GOOGLE_API_KEY)

# Function to convert audio file to WAV format using pydub
def convert_to_wav(input_path, output_path):
    try:
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format='wav')
        return output_path
    except Exception as e:
        st.error(f"Error converting audio file: {e}")
        return None

# Function to transcribe audio, translate to English, and generate content with Generative AI
def process_audio(audio_path):
    wav_path = convert_to_wav(audio_path, audio_path.replace('.m4a', '.wav'))
    
    if not wav_path:
        st.error("Failed to convert audio file. Exiting...")
        return

    # Initialize the Generative Model
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        st.error(f"Error loading the Gemini model: {e}")
        return

    # Create the prompt for keyword extraction
    prompt = '''
    Extract keywords from the following text and answer in such a way that it feels like 
    I'm not using any AI, it should seem like I'm using an ML model which prints only keywords in a bullet list.
    Do not use words like 'generated response', just simply print keywords.
    '''

    try:
        # Transcribe the audio
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language='hi-IN')  # Recognizing Hindi

        st.subheader("📝 Transcribed Text (Hindi Romanized):")
        st.success(text)

        # Translate the Romanized Hindi to English
        translator = Translator()
        translation = translator.translate(text, src='hi', dest='en')
        translated_text = translation.text

        st.subheader("🌍 Translated Text (English):")
        st.success(translated_text)

        # Pass the translated text to the generative model for keyword extraction
        response = model.generate_content(prompt + translated_text)

        st.subheader("🔑 Extracted Keywords:")
        st.info(response.text)

    except sr.RequestError as e:
        st.error(f"API request error during transcription: {e}")
    except sr.UnknownValueError:
        st.error("Google Speech Recognition could not understand the audio.")
    except Exception as e:
        st.error(f"Error during transcription or content generation: {e}")

# Streamlit UI
st.set_page_config(page_title="Keyword Extractor", page_icon="🔍", layout="centered")
st.markdown("""
    <style>
    .stApp {
        background-color: black;  /* Black background */
        color: #ffffff;  /* White text */
    }
    .stButton>button {
        background-color: #e91e63;  /* Pink button color */
        color: white;
        font-size: 16px;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        width: 100%;
        transition: background-color 0.3s, transform 0.3s;
    }
    .stButton>button:hover {
        background-color: #f06292;
        transform: scale(1.05);
    }
    .stButton>button:focus, .stButton>button:active {
        color: white;
        box-shadow: none;
    }
    .stFileUploader>div>button {
        background-color: #00bcd4 !important;  /* Cyan button */
        color: white !important;
        border-radius: 8px !important;
    }
    .stFileUploader>div>button:hover {
        background-color: #0097a7 !important;
    }
    .stTextInput>div>input, .stSlider>div>input {
        border-radius: 5px;
        border: 2px solid #0288d1;
        padding: 10px;
        background-color: #424242;  /* Dark gray input fields */
        color: white;
    }
    .stSubheader {
        color: #e91e63;  /* Pink for subheaders */
    }
    </style>
""", unsafe_allow_html=True)

# Main UI
st.title("🔍 Keyword Extractor")
st.subheader("Upload your audio file for transcription, translation, and keyword extraction:")
uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3', 'm4a'])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        audio_path = temp_file.name

    st.success("✅ File uploaded successfully!")

    # Process the uploaded audio
    process_audio(audio_path)

    # Clean up temporary files
    os.remove(audio_path)
