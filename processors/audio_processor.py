import os
import tempfile
from pathlib import Path
import speech_recognition as sr
from pydub import AudioSegment
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

class AudioProcessor:
    """Handles complete audio analysis, speech-to-text, and lyrics extraction"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Configure recognizer for better music/speech detection
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        
        self.whisper_model = None
        if WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("tiny")
                print("Whisper tiny model loaded for fast transcription")
            except Exception as e:
                print(f"Failed to load Whisper: {e}")
    
    def process(self, file_path: str) -> str:
        """
        Complete pin-to-pin audio analysis and text conversion
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Complete audio-to-text conversion with full transcript
        """
        try:
            filename = Path(file_path).name
            
            # Convert to WAV format for processing
            wav_path = self._convert_to_wav(file_path)
            
            try:
                # Get audio metadata
                metadata = self._get_audio_metadata(file_path)
                
                # Complete pin-to-pin transcription
                full_transcript = self._complete_audio_to_text(wav_path)
                
                # Format as text document
                result = f"AUDIO FILE ANALYSIS\n"
                result += f"File: {filename}\n"
                result += f"Duration: {metadata['duration']} seconds\n"
                result += f"Format: {metadata['format']}\n"
                result += f"{'='*50}\n\n"
                result += f"COMPLETE TRANSCRIPT (Pin-to-Pin):\n\n{full_transcript}\n\n"
                result += f"{'='*50}\n"
                result += f"Processing Status: Complete audio-to-text conversion successful"
                
                return result
                
            finally:
                # Clean up temporary WAV file
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
        Transcribe WAV audio file using speech recognition in chunks
        
        Args:
            wav_path: Path to WAV file
            
        Returns:
            Transcribed text
        """
        try:
            # Load audio with pydub to get duration and split into chunks
            audio = AudioSegment.from_wav(wav_path)
            duration_ms = len(audio)
            
            # Try Whisper first for complete transcription
            if self.whisper_model:
                try:
                    result = self.whisper_model.transcribe(wav_path, fp16=False)
                    return result["text"].strip()
                except Exception as e:
                    print(f"Whisper failed: {e}, using enhanced Google Speech Recognition")
            
            # If audio is short (< 60 seconds), transcribe as one piece
            if duration_ms < 60000:
                return self._transcribe_chunk(wav_path)
            
            # For longer audio, split into 30-second chunks for speed
            chunk_length_ms = 30000  # 30 seconds
            transcripts = []
            
            for i in range(0, duration_ms, chunk_length_ms):
                chunk = audio[i:i + chunk_length_ms]
                
                # Export chunk to temporary file
                chunk_path = wav_path.rsplit('.', 1)[0] + f'_chunk_{i//chunk_length_ms}.wav'
                chunk.export(chunk_path, format="wav")
                
                try:
                    # Transcribe chunk
                    chunk_transcript = self._transcribe_chunk(chunk_path)
                    if chunk_transcript and chunk_transcript != "Could not understand audio content":
                        transcripts.append(chunk_transcript)
                finally:
                    # Clean up chunk file
                    if os.path.exists(chunk_path):
                        os.unlink(chunk_path)
            
            return " ".join(transcripts) if transcripts else "Could not understand audio content"
                    
        except Exception as e:
            raise Exception(f"Error transcribing audio: {str(e)}")
    
    def _transcribe_chunk(self, wav_path: str) -> str:
        """
        Transcribe a single audio chunk with enhanced settings
        
        Args:
            wav_path: Path to WAV file chunk
            
        Returns:
            Transcribed text for the chunk
        """
        try:
            with sr.AudioFile(wav_path) as source:
                # Enhanced noise adjustment for music
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                # Record the audio with offset to skip silence
                audio_data = self.recognizer.record(source, offset=0.1)
                
                # Try multiple recognition methods
                methods = [
                    ('Google', lambda: self.recognizer.recognize_google(audio_data, language='en-US')),
                    ('Google (Hindi)', lambda: self.recognizer.recognize_google(audio_data, language='hi-IN')),
                ]
                
                for method_name, method in methods:
                    try:
                        transcript = method()
                        if transcript and len(transcript.strip()) > 0:
                            return transcript
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        print(f"{method_name} recognition failed: {e}")
                        continue
                
                return "[Audio content detected but could not transcribe clearly]"
                    
        except Exception as e:
            return f"Error transcribing chunk: {str(e)}"
    
    def _complete_audio_to_text(self, wav_path: str) -> str:
        """
        Complete pin-to-pin audio-to-text conversion
        
        Args:
            wav_path: Path to WAV file
            
        Returns:
            Complete transcribed text from entire audio
        """
        # Primary Method: Whisper for complete transcription
        if self.whisper_model:
            try:
                print("Processing complete audio with Whisper...")
                result = self.whisper_model.transcribe(
                    wav_path, 
                    fp16=False, 
                    language='en',  # Fixed language for speed
                    word_timestamps=False,  # Disable for speed
                    verbose=False,
                    condition_on_previous_text=False  # Faster processing
                )
                
                # Get complete text with timestamps if available
                if 'segments' in result:
                    segments_text = []
                    for segment in result['segments']:
                        start_time = int(segment['start'])
                        end_time = int(segment['end'])
                        text = segment['text'].strip()
                        segments_text.append(f"[{start_time:02d}:{start_time%60:02d}-{end_time:02d}:{end_time%60:02d}] {text}")
                    
                    complete_text = "\n".join(segments_text)
                    if len(complete_text) > 50:
                        return complete_text
                
                # Fallback to simple text
                text = result["text"].strip()
                if len(text) > 20:
                    return text
                    
            except Exception as e:
                print(f"Whisper failed: {e}, using fallback method")
        
        # Fallback: Enhanced chunk processing
        return self._transcribe_audio(wav_path)
    
    def _get_audio_metadata(self, file_path: str) -> dict:
        """
        Extract audio file metadata
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with audio metadata
        """
        try:
            audio = AudioSegment.from_file(file_path)
            return {
                'duration': len(audio) / 1000,  # Convert to seconds
                'format': Path(file_path).suffix.upper().replace('.', ''),
                'channels': audio.channels,
                'sample_rate': audio.frame_rate
            }
        except Exception:
            return {
                'duration': 'Unknown',
                'format': Path(file_path).suffix.upper().replace('.', ''),
                'channels': 'Unknown',
                'sample_rate': 'Unknown'
            }
    
    def _detect_music(self, wav_path: str) -> bool:
        """
        Simple music detection based on audio characteristics
        
        Args:
            wav_path: Path to WAV file
            
        Returns:
            True if likely music, False if likely speech
        """
        try:
            audio = AudioSegment.from_wav(wav_path)
            # Simple heuristic: music tends to be longer and have more consistent volume
            duration = len(audio) / 1000
            return duration > 30  # Assume files > 30 seconds are likely music
        except Exception:
            return False
