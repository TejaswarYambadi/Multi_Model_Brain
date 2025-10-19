from processors.audio_processor import AudioProcessor

processor = AudioProcessor()

# Test the enhanced audio processing
print("Testing enhanced audio processor...")
print("Whisper available:", hasattr(processor, 'whisper_model') and processor.whisper_model is not None)

# You can test with any audio file
test_file = "test_audio.mp3"  # Replace with your actual audio file
if __name__ == "__main__":
    print("Enhanced audio processor ready for complete lyrics extraction!")