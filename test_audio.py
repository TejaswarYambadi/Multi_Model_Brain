from processors.audio_processor import AudioProcessor
import os

processor = AudioProcessor()

# Test with any audio file you have
audio_files = []
for ext in ['.mp3', '.wav', '.m4a']:
    for file in os.listdir('.'):
        if file.endswith(ext):
            audio_files.append(file)

if audio_files:
    print(f"Found audio files: {audio_files}")
    for audio_file in audio_files[:1]:  # Test first one
        try:
            result = processor.process(audio_file)
            print(f"\nProcessing {audio_file}:")
            print("=" * 50)
            print(result)
        except Exception as e:
            print(f"Error processing {audio_file}: {e}")
else:
    print("No audio files found in current directory")