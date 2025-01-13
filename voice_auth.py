import sounddevice as sd
import soundfile as sf
import numpy as np
from transformers import pipeline
from scipy import signal
import librosa
import pyttsx3
import time
import sys
import ctypes
import os

class VoiceAuthenticator:
    def __init__(self):
        self.asr_pipeline = pipeline("automatic-speech-recognition", 
                                   model="facebook/wav2vec2-base-960h")
        self.sample_rate = 16000
        self.duration = 10  # Recording duration in seconds
        self.engine = pyttsx3.init()
        # Load reference audio once during initialization
        self.reference_audio = self.load_reference_audio()
        self.ref_features = self.extract_features(self.reference_audio)
        
    def lock_windows(self):
        """Lock Windows screen using Windows API"""
        user32 = ctypes.WinDLL('user32')
        user32.LockWorkStation()
        
    def record_audio(self, duration=None):
        """Record audio from microphone and return the recording"""
        if duration is None:
            duration = self.duration
            
        print(f"Recording for {duration} seconds...")
        recording = sd.rec(int(duration * self.sample_rate),
                         samplerate=self.sample_rate,
                         channels=1)
        sd.wait()
        return recording.flatten()
        
    def detect_lock_word(self, audio_data):
        """Detect if the word 'lock' is in the audio"""
        try:
            result = self.asr_pipeline({"sampling_rate": self.sample_rate, "raw": audio_data})
            transcription = result['text'].lower()
            print(f"Detected speech: {transcription}")
            return 'lock' in transcription
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return False
        
    def load_reference_audio(self):
        """Load the reference audio file"""
        if not os.path.exists('sharad.wav'):
            print("Error: Reference file 'sharad.wav' not found!")
            print("Please run record_reference.py first to create your voice reference.")
            sys.exit(1)
        
        audio_data, _ = sf.read('sharad.wav')
        return audio_data
        
    def extract_features(self, audio_data):
        """Extract audio features with primary focus on tone characteristics"""
        # Convert to float32 if not already
        y = audio_data.astype(np.float32)
        
        # Extract comprehensive tone features
        # Spectral centroid - brightness/sharpness of the sound
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=self.sample_rate)[0]
        # Spectral rolloff - distribution of frequencies
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=self.sample_rate, roll_percent=0.85)[0]
        # Spectral bandwidth - spread of frequencies around centroid
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=self.sample_rate)[0]
        
        # Get average tone characteristics
        tone_features = {
            'centroid': np.mean(spectral_centroids),      # Voice brightness
            'rolloff': np.mean(spectral_rolloff),         # Frequency distribution
            'bandwidth': np.mean(spectral_bandwidth)       # Frequency spread
        }
        
        # Extract minimal frequency features (reduced importance)
        mel_spec = librosa.feature.melspectrogram(y=y, sr=self.sample_rate, 
                                                n_mels=64, fmax=8000)  # Reduced mel bands
        freq_features = np.mean(mel_spec, axis=1)
        
        return {
            'tone': tone_features,
            'frequency': freq_features
        }
    
    def compare_features(self, features1, features2, threshold=0.75):
        """Compare audio features with primary focus on tone characteristics"""
        # Compare tone features (85% weight)
        tone_sims = {
            'centroid': 1 - abs(features1['tone']['centroid'] - features2['tone']['centroid']) / features1['tone']['centroid'],
            'rolloff': 1 - abs(features1['tone']['rolloff'] - features2['tone']['rolloff']) / features1['tone']['rolloff'],
            'bandwidth': 1 - abs(features1['tone']['bandwidth'] - features2['tone']['bandwidth']) / features1['tone']['bandwidth']
        }
        
        # Weight tone aspects (total 85%)
        tone_similarity = (
            tone_sims['centroid'] * 0.35 +     # Voice brightness (35%)
            tone_sims['rolloff'] * 0.30 +      # Frequency distribution (30%)
            tone_sims['bandwidth'] * 0.20      # Frequency spread (20%)
        )
        
        # Compare frequency features (15% weight - reduced importance)
        freq_similarity = np.corrcoef(features1['frequency'], features2['frequency'])[0,1]
        
        # Calculate total similarity (85-15 split)
        total_similarity = (
            tone_similarity * 0.85 +    # Primary tone weight
            freq_similarity * 0.15      # Minimal frequency weight
        )
        
        # Print simplified characteristics and similarities
        print(f"\nVoice Tone Characteristics:")
        print(f"Voice Brightness - Ref: {features1['tone']['centroid']:.2f} Hz, Input: {features2['tone']['centroid']:.2f} Hz")
        print(f"Frequency Distribution - Ref: {features1['tone']['rolloff']:.2f} Hz, Input: {features2['tone']['rolloff']:.2f} Hz")
        print(f"Frequency Spread - Ref: {features1['tone']['bandwidth']:.2f} Hz, Input: {features2['tone']['bandwidth']:.2f} Hz")
        
        print(f"\nSimilarity Scores:")
        print(f"Tone Similarity: {tone_similarity:.2%}")
        print(f"├─ Voice Brightness: {tone_sims['centroid']:.2%}")
        print(f"├─ Frequency Distribution: {tone_sims['rolloff']:.2%}")
        print(f"└─ Frequency Spread: {tone_sims['bandwidth']:.2%}")
        print(f"Overall Frequency Similarity: {freq_similarity:.2%}")
        print(f"Total Similarity: {total_similarity:.2%}")
        
        return total_similarity > threshold
    
    def speak_response(self, voice_matched, lock_word_detected):
        """Speak the response using text-to-speech"""
        if voice_matched and lock_word_detected:
            text = "Lock"
            self.engine.say(text)
            self.engine.runAndWait()
            print("\nVoice matched and lock command detected! Locking screen...")
            time.sleep(1)  # Wait for speech to finish
            self.lock_windows()  # Lock the screen using Windows API
            sys.exit(0)  # Terminate the program
        elif not voice_matched:
            print("Voice doesn't match. Continuing to listen...")
        elif not lock_word_detected:
            print("Lock command not detected. Continuing to listen...")
    
    def run(self):
        """Main loop to continuously listen and check for voice match and lock command"""
        print("Listening for your voice saying 'lock'...")
        print("Press Ctrl+C to exit")
        
        while True:
            try:
                # Record audio
                audio_sample = self.record_audio(duration=5)  # Listen for 5 seconds
                
                # First check if the voice matches
                input_features = self.extract_features(audio_sample)
                voice_matched = self.compare_features(self.ref_features, input_features)
                # Then check for lock word if voice matches
                lock_word_detected = False
                if voice_matched:
                    lock_word_detected = self.detect_lock_word(audio_sample)
                
                # Handle the response
                self.speak_response(voice_matched, lock_word_detected)
                
                time.sleep(0.1)  # Small delay to prevent CPU overuse
                
            except KeyboardInterrupt:
                print("\nExiting...")
                sys.exit(0)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)  # Wait a bit before retrying

if __name__ == "__main__":
    authenticator = VoiceAuthenticator()
    authenticator.run() 
