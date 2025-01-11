import sounddevice as sd
import soundfile as sf
import time

def record_reference():
    duration = 10  # seconds
    sample_rate = 16000
    
    print("Get ready to record your reference voice...")
    time.sleep(1)
    print("Recording will start in:")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("\nRecording... Please speak for 10 seconds")
    recording = sd.rec(int(duration * sample_rate),
                      samplerate=sample_rate,
                      channels=1)
    
    # Wait for the recording to complete
    sd.wait()
    
    # Save the recording
    sf.write('sharad.wav', recording, sample_rate)
    print("\nReference voice saved as 'sharad.wav'")

if __name__ == "__main__":
    record_reference() 
