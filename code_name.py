import streamlit as st
import speech_recognition as sr
import tempfile
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting

# Function to initialize the model
def initialize_model():
    vertexai.init(project="gemini-clone-426505", location="us-central1")
    model = GenerativeModel(model_name="gemini-1.5-flash-002")
    return model

# Function to convert audio file to WAV format using pydub
def convert_to_wav(input_path, output_path):
    from pydub import AudioSegment
    try:
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format='wav')
        return output_path
    except Exception as e:
        st.error(f"Error converting audio file: {e}")
        return None

# Function to transcribe audio and generate content with Generative AI
def process_audio(audio_path, model):
    wav_path = convert_to_wav(audio_path, audio_path.replace('.m4a', '.wav'))
    
    if not wav_path:
        st.error("Failed to convert audio file. Exiting...")
        return

    # Create the prompt
    prompt = '''
    Extract keywords from the following text: answer in such a way that it feels like 
    I'm not using any AI. It should seem like an ML model printing only key words in a bullet list.
    Don't use words like "generated response", just simply print key words.
    '''

    try:
        # Transcribe the audio
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        st.write("Transcribed Text:\n" + text)

        # Pass the prompt and the transcribed text to Gemini
        response = model.generate_content([prompt + text])
        st.write("Keywords:\n" + response.text)

    except Exception as e:
        st.error(f"Error during transcription or content generation: {e}")

# Streamlit UI
st.set_page_config(page_title="Audio File Processor", layout="wide")
st.markdown("""
    <style>
    .stApp {
        background-color: #E0F7FA; /* Light Blue background */
        color: #01579B; /* Deep blue text */
    }
    .stButton>button {
        background-color: #0097A7; /* Cyan */
        color: white; /* Setting text color to white for all buttons */
        font-size: 16px;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        width: 100%;
        transition: background-color 0.3s, transform 0.3s;
    }
    .stButton>button:hover {
        background-color: #00ACC1;
        transform: scale(1.05);
    }
    .stButton>button:focus, .stButton>button:active {
        color: white; /* Keeps text color white even when clicked */
        box-shadow: none;
    }
    .stTextInput>div>input, .stSlider>div>input {
        border-radius: 5px;
        border: 2px solid #0288D1; /* Darker blue border for inputs */
        padding: 10px;
        background-color: #B3E5FC; /* Lighter blue for input fields */
        color: #01579B;
    }
    </style>
""", unsafe_allow_html=True)

st.title("SIH-2024")
st.header("Audio File Processor")

st.subheader("Upload your audio file for transcription and keyword extraction:")
uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3', 'm4a'])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        audio_path = temp_file.name

    st.success("File uploaded successfully.")

    # Initialize the model
    model = initialize_model()

    # Process the uploaded audio
    process_audio(audio_path, model)

    # Clean up temporary files
    os.remove(audio_path)
