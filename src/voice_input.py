# voice_input.py - Captures voice using sounddevice and converts to text
# FIX: All sounddevice / scipy imports are deferred and wrapped in try/except
# so that importing this module on Streamlit Cloud (no audio device) does NOT
# crash the app at startup.  The caller (app.py) also guards the call.

import io
import os
import speech_recognition as sr


def get_voice_input(duration: int = 5,
                    auto_stop: bool = False,
                    silence_threshold: int = 500,
                    silence_duration: float = 1.0):
    """
    Record audio from the system microphone and return transcribed text.

    Parameters
    - duration: maximum seconds to record (upper bound)
    - auto_stop: if True, stop earlier when silence is detected
    - silence_threshold: RMS threshold for silence detection (int16 scale)
    - silence_duration: seconds of continuous silence required to stop early

    Returns transcribed text or a friendly error message when mic/service unavailable.
    """
    fs = 44100       # Sample rate
    filename = "/tmp/temp_voice_medisense.wav"

    try:
        # Lazy-import hardware-dependent libraries so a missing sounddevice
        # package does not crash the module on import.
        import sounddevice as sd
        import numpy as np
        import scipy.io.wavfile as wav
    except ImportError:
        return "Microphone not available in this environment."

    try:
        print(f"Listening... Speak your symptoms clearly (max {duration} s).")
        # prefer 16kHz for VAD compatibility
        fs = 16000
        seconds = duration
        recording = None

        # RMS-based chunked silence detection (simple and dependency-free)
        fs = 16000
        seconds = duration
        if auto_stop:
            chunk_seconds = 0.5
            chunk_samples = int(fs * chunk_seconds)
            recorded = []
            silent_chunks = 0
            max_silent_chunks = max(1, int(silence_duration / chunk_seconds))
            elapsed = 0.0
            while elapsed < seconds and silent_chunks < max_silent_chunks:
                rec = sd.rec(chunk_samples, samplerate=fs, channels=1, dtype='int16')
                sd.wait()
                recorded.append(rec)
                rms = int((rec.astype('int32')**2).mean()**0.5)
                if rms < silence_threshold:
                    silent_chunks += 1
                else:
                    silent_chunks = 0
                elapsed += chunk_seconds
            if len(recorded) == 0:
                return ""
            recording = np.concatenate(recorded, axis=0)
        else:
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()

        wav.write('temp_voice.wav', fs, recording)
        # transcribe using speech_recognition if available
        try:
            r = sr.Recognizer()
            with sr.AudioFile('temp_voice.wav') as source:
                audio = r.record(source)
            text = r.recognize_google(audio)
            return text
        except Exception:
            return ''
    except Exception:
        return 'Voice input unavailable on this system.'


# Test the module
if __name__ == "__main__":
    result = get_voice_input()
    print("Final Captured Text:", result)