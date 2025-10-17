import os
import tempfile
from pathlib import Path
import speech_recognition as sr
from pydub import AudioSegment

class AudioProcessor:
    """Handles processing of audio files for transcription"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def process(self, file_path: str) -> str:
        """
        Process an audio file and extract transcript
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Audio transcript
        """
        try:
            # Convert to WAV format for speech recognition
            wav_path = self._convert_to_wav(file_path)
            
            try:
                # Transcribe audio
                transcript = self._transcribe_audio(wav_path)
                
                # Add file metadata to transcript
                filename = Path(file_path).name
                return f"Audio: {filename}\n\nTranscript:\n{transcript}"
                
            finally:
                # Clean up temporary WAV file if it was created
                if wav_path != file_path and os.path.exists(wav_path):
                    os.unlink(wav_path)
                    
        except Exception as e:
            raise Exception(f"Error processing audio {file_path}: {str(e)}")
    
    def _convert_to_wav(self, file_path: str) -> str:
        """
        Convert audio file to WAV format for speech recognition
        
        Args:
            file_path: Path to original audio file
            
        Returns:
            Path to WAV file
        """
        file_extension = Path(file_path).suffix.lower()
        
        # If already WAV, return as-is
        if file_extension == '.wav':
            return file_path
        
        try:
            # Load audio file with pydub
            if file_extension == '.mp3':
                audio = AudioSegment.from_mp3(file_path)
            else:
                audio = AudioSegment.from_file(file_path)
            
            # Convert to WAV
            wav_path = file_path.rsplit('.', 1)[0] + '_temp.wav'
            audio.export(wav_path, format="wav")
            
            return wav_path
            
        except Exception as e:
            raise Exception(f"Error converting audio to WAV: {str(e)}")
    
    def _transcribe_audio(self, wav_path: str) -> str:
        """
        Transcribe WAV audio file using speech recognition
        
        Args:
            wav_path: Path to WAV file
            
        Returns:
            Transcribed text
        """
        try:
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Record the audio
                audio_data = self.recognizer.record(source)
                
                # Recognize speech using Google's speech recognition
                try:
                    transcript = self.recognizer.recognize_google(audio_data)
                    return transcript
                except sr.UnknownValueError:
                    return "Could not understand audio content"
                except sr.RequestError as e:
                    return f"Could not request results from speech recognition service: {e}"
                    
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")
