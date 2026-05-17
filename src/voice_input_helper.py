import io
import speech_recognition as sr


def get_voice_input_from_file(uploaded_file):
    """Transcribe an uploaded audio file via Google SpeechRecognition."""
    recognizer = sr.Recognizer()
    try:
        uploaded_file.seek(0)
        audio_bytes = uploaded_file.read()
        audio_stream = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_stream) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "Speech service unavailable. Check your internet."
    except Exception as e:
        return f"An error occurred: {str(e)}"
