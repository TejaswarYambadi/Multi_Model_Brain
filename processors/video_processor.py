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
        Complete pin-to-pin video processing: video -> audio -> text
        
        Args:
            file_path: Path to the video file
            
        Returns:
            Complete video-to-text conversion with full transcript
        """
        try:
            filename = Path(file_path).name
            
            # Step 1: Extract video metadata
            video_metadata = self._get_video_metadata(file_path)
            
            # Step 2: Extract audio from video and convert to text (pin-to-pin)
            print(f"Processing video: {filename}")
            print("Step 1: Extracting audio from video...")
            audio_transcript = self._extract_and_transcribe_audio_complete(file_path)
            
            # Step 3: Format as complete text document
            result = f"VIDEO FILE ANALYSIS\n"
            result += f"File: {filename}\n"
            result += f"Duration: {video_metadata['duration']} seconds\n"
            result += f"Resolution: {video_metadata['resolution']}\n"
            result += f"{'='*50}\n\n"
            result += f"COMPLETE TRANSCRIPT (Video -> Audio -> Text):\n\n{audio_transcript}\n\n"
            result += f"{'='*50}\n"
            result += f"Processing Status: Complete video-to-text conversion successful"
            
            return result
                
        except Exception as e:
            raise Exception(f"Error processing video {file_path}: {str(e)}")
    
    def _extract_and_transcribe_audio_complete(self, video_path: str) -> str:
        """
        Complete video-to-audio-to-text conversion (pin-to-pin)
        
        Args:
            video_path: Path to video file
            
        Returns:
            Complete audio transcript from video
        """
        temp_audio_path = None
        video = None
        try:
            print("Step 2: Loading video file...")
            video = VideoFileClip(video_path)
            
            # Check if video has audio
            if video.audio is None:
                return "No audio track found in video - video contains no sound"
            
            print("Step 3: Extracting audio track...")
            # Create temporary audio file
            temp_audio_path = video_path.rsplit('.', 1)[0] + '_temp_audio.wav'
            
            # Extract complete audio to temporary file with optimized settings
            video.audio.write_audiofile(
                temp_audio_path, 
                logger=None, 
                verbose=False,
                codec='pcm_s16le',  # Fast codec
                ffmpeg_params=["-ac", "1", "-ar", "16000"]  # Mono, 16kHz for speed
            )
            
            print("Step 4: Converting audio to text (pin-to-pin)...")
            # Use complete audio-to-text conversion
            transcript = self.audio_processor._complete_audio_to_text(temp_audio_path)
            
            print("Step 5: Video-to-text conversion complete!")
            return transcript
            
        except Exception as e:
            raise Exception(f"Error in video-to-text conversion: {str(e)}")
        finally:
            # Close video file
            if video:
                try:
                    video.close()
                except:
                    pass
            
            # Clean up temporary audio file
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.unlink(temp_audio_path)
                except:
                    pass
    
    def _get_video_metadata(self, video_path: str) -> dict:
        """
        Extract video metadata
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video metadata
        """
        try:
            video = VideoFileClip(video_path)
            metadata = {
                'duration': video.duration,
                'resolution': f"{video.w}x{video.h}",
                'fps': video.fps,
                'has_audio': video.audio is not None
            }
            video.close()
            return metadata
        except Exception:
            return {
                'duration': 'Unknown',
                'resolution': 'Unknown',
                'fps': 'Unknown',
                'has_audio': 'Unknown'
            }
