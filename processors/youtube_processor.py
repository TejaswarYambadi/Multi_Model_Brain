import re
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

class YouTubeProcessor:
    """Handles processing of YouTube videos for transcript extraction"""
    
    def process(self, youtube_url: str) -> str:
        """
        Process a YouTube URL and extract content
        
        Args:
            youtube_url: YouTube video URL
            
        Returns:
            Video metadata and transcript
        """
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(youtube_url)
            if not video_id:
                raise ValueError("Invalid YouTube URL")
            
            # Get video metadata
            video_info = self._get_video_info(youtube_url)
            
            # Get transcript
            transcript = self._get_transcript(video_id)
            
            # Combine metadata and transcript
            content = f"YouTube Video: {video_info['title']}\n"
            content += f"Channel: {video_info['channel']}\n"
            content += f"URL: {youtube_url}\n\n"
            
            if transcript:
                content += f"Transcript:\n{transcript}"
            else:
                content += "Transcript not available for this video."
            
            return content
            
        except Exception as e:
            raise Exception(f"Error processing YouTube video {youtube_url}: {str(e)}")
    
    def _extract_video_id(self, url: str) -> str:
        """
        Extract video ID from YouTube URL
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID or empty string if not found
        """
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:v=)([0-9A-Za-z_-]{11})',
            r'^([0-9A-Za-z_-]{11})$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return ""
    
    def _get_video_info(self, url: str) -> dict:
        """
        Get video metadata using pytube
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary with video information
        """
        try:
            yt = YouTube(url)
            return {
                'title': yt.title or 'Unknown Title',
                'channel': yt.author or 'Unknown Channel',
                'description': yt.description or '',
                'length': yt.length or 0
            }
        except Exception as e:
            # Return minimal info if metadata extraction fails
            return {
                'title': 'YouTube Video',
                'channel': 'Unknown Channel',
                'description': '',
                'length': 0
            }
    
    def _get_transcript(self, video_id: str) -> str:
        """
        Get video transcript using youtube_transcript_api
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video transcript text
        """
        try:
            # Try to get English transcript first
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            
            # Join all transcript segments
            transcript_text = ' '.join([entry['text'] for entry in transcript_list])
            
            return transcript_text
            
        except (TranscriptsDisabled, NoTranscriptFound):
            try:
                # Try to get any available transcript
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Get the first available transcript
                transcript = next(iter(transcript_list))
                transcript_data = transcript.fetch()
                
                transcript_text = ' '.join([entry['text'] for entry in transcript_data])
                
                return transcript_text
                
            except Exception:
                return ""
        except Exception:
            return ""
