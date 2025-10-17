import os
import tempfile
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
from processors.audio_processor import AudioProcessor
from utils.gemini_client import GeminiClient

class VideoProcessor:
    """Handles processing of video files for content extraction"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.gemini_client = GeminiClient()
    
    def process(self, file_path: str) -> str:
        """
        Process a video file and extract content
        
        Args:
            file_path: Path to the video file
            
        Returns:
            Video analysis and audio transcript
        """
        try:
            content_parts = []
            filename = Path(file_path).name
            
            # First, try to analyze the video directly with Gemini (if supported)
            try:
                video_analysis = self.gemini_client.analyze_video(file_path)
                if video_analysis:
                    content_parts.append(f"Video Analysis:\n{video_analysis}")
            except Exception as e:
                print(f"Direct video analysis failed: {e}")
            
            # Extract audio and transcribe
            try:
                audio_transcript = self._extract_and_transcribe_audio(file_path)
                if audio_transcript:
                    content_parts.append(f"Audio Transcript:\n{audio_transcript}")
            except Exception as e:
                print(f"Audio extraction failed: {e}")
            
            # Combine all content
            if content_parts:
                full_content = f"Video: {filename}\n\n" + "\n\n".join(content_parts)
                return full_content
            else:
                return f"Video: {filename}\n\nUnable to extract content from video file."
                
        except Exception as e:
            raise Exception(f"Error processing video {file_path}: {str(e)}")
    
    def _extract_and_transcribe_audio(self, video_path: str) -> str:
        """
        Extract audio from video and transcribe it
        
        Args:
            video_path: Path to video file
            
        Returns:
            Audio transcript
        """
        temp_audio_path = None
        try:
            # Load video and extract audio
            video = VideoFileClip(video_path)
            
            # Create temporary audio file
            temp_audio_path = video_path.rsplit('.', 1)[0] + '_temp_audio.wav'
            
            # Extract audio to temporary file
            video.audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
            video.close()
            
            # Transcribe the audio
            transcript = self.audio_processor._transcribe_audio(temp_audio_path)
            
            return transcript
            
        except Exception as e:
            raise Exception(f"Error extracting audio from video: {str(e)}")
        finally:
            # Clean up temporary audio file
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass
