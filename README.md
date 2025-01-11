# Voice Authentication Lock System

A voice-based authentication system that locks your Windows PC when it recognizes your voice saying "lock". The system uses advanced voice characteristics matching focusing on tone and frequency patterns.

## Features

- Voice recognition using tone matching
- Continuous listening for the "lock" command
- Secure Windows lock mechanism
- Real-time voice characteristics comparison
- Detailed similarity scoring

## Requirements

```
torch==2.0.1
torchaudio==2.0.2
transformers==4.35.2
sounddevice==0.4.6
soundfile==0.12.1
numpy==1.23.5
scipy==1.11.3
numba==0.58.1
pyttsx3==2.90
librosa==0.10.1
```

## Setup

1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Record your voice reference:
```bash
python record_reference.py
```

3. Run the voice authentication system:
```bash
python voice_auth.py
```

## Usage

1. First time setup: Run `record_reference.py` to create your voice reference file
2. Run `voice_auth.py` to start the authentication system
3. Speak the word "lock" to attempt screen locking
4. The system will:
   - Compare your voice characteristics with the reference
   - Lock the screen if your voice matches and "lock" is detected
   - Continue listening if no match or no "lock" word detected

## How it Works

The system uses three main characteristics for voice matching:
- Tone (70% weight): Voice brightness and frequency distribution
- Frequency (25% weight): Overall voice timbre
- Pitch (5% weight): Basic pitch matching

## Files

- `voice_auth.py`: Main authentication system
- `record_reference.py`: Utility to record voice reference
- `requirements.txt`: Required Python packages
- `voice_lock.bat`: Windows batch file to run the system 
