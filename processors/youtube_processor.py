import re
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import requests
from bs4 import BeautifulSoup
import json

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
                if '/results?' in youtube_url or 'search_query=' in youtube_url:
                    raise ValueError("Please provide a specific YouTube video URL, not a search results page. Example: https://www.youtube.com/watch?v=VIDEO_ID")
                else:
                    raise ValueError("Invalid YouTube URL. Please use format: https://www.youtube.com/watch?v=VIDEO_ID")
            
            # Get video metadata
            video_info = self._get_video_info(youtube_url)
            
            # Get transcript
            transcript = self._get_transcript(video_id)
            
            # Get lyrics
            lyrics = self._get_lyrics(video_info['title'], video_info['channel'])
            
            # Combine metadata, transcript, and lyrics
            content = f"YouTube Video: {video_info['title']}\n"
            content += f"Channel: {video_info['channel']}\n"
            content += f"URL: {youtube_url}\n\n"
            
            if transcript:
                content += f"Transcript:\n{transcript}\n\n"
            else:
                content += "Transcript not available for this video.\n\n"
            
            if lyrics:
                content += f"Lyrics:\n{lyrics}"
            else:
                content += "Lyrics not available for this video."
            
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
        # Check if it's a search results URL
        if '/results?' in url or 'search_query=' in url:
            return ""
        
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
        Get video metadata using web scraping fallback
        
        Args:
            url: YouTube URL
            
        Returns:
            Dictionary with video information
        """
        try:
            response = requests.get(url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('meta', property='og:title')
            title = title_tag['content'] if title_tag else 'YouTube Video'
            
            # Extract channel
            channel_tag = soup.find('link', {'itemprop': 'name'})
            channel = channel_tag['content'] if channel_tag else 'Unknown Channel'
            
            # Extract description
            desc_tag = soup.find('meta', property='og:description')
            description = desc_tag['content'] if desc_tag else ''
            
            print(f"Extracted: {title} by {channel}")
            
            return {
                'title': title,
                'channel': channel,
                'description': description,
                'length': 0
            }
        except Exception as e:
            print(f"Metadata extraction failed: {e}")
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
            api = YouTubeTranscriptApi()
            transcript_obj = api.fetch(video_id, languages=['en'])
            transcript_data = transcript_obj.to_raw_data()
            transcript_text = ' '.join([entry['text'] for entry in transcript_data])
            print(f"Successfully extracted English transcript ({len(transcript_text)} chars)")
            return transcript_text
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            print(f"English transcript not available: {e}")
            try:
                # Try to get any available transcript
                api = YouTubeTranscriptApi()
                transcript_list = api.list(video_id)
                transcript = next(iter(transcript_list))
                transcript_obj = transcript.fetch()
                transcript_data = transcript_obj.to_raw_data()
                transcript_text = ' '.join([entry['text'] for entry in transcript_data])
                print(f"Successfully extracted transcript in {transcript.language}: ({len(transcript_text)} chars)")
                return transcript_text
                
            except Exception as e2:
                print(f"No transcripts available: {e2}")
                return ""
        except Exception as e:
            print(f"Transcript extraction failed: {e}")
            return ""
    
    def _get_lyrics(self, title: str, artist: str) -> str:
        """
        Get song lyrics using multiple sources
        
        Args:
            title: Video/song title
            artist: Channel/artist name
            
        Returns:
            Song lyrics text
        """
        try:
            # Clean title and artist for better search
            clean_title = self._clean_search_term(title)
            clean_artist = self._clean_search_term(artist)
            
            print(f"Searching lyrics for: '{clean_title}' by '{clean_artist}'")
            
            # Skip lyrics search for educational/tutorial content
            if any(term in clean_title.lower() for term in ['tutorial', 'lesson', 'course', 'learn', 'guide', 'how to', 'java', 'features']):
                print("Skipping lyrics search for educational content")
                return ""
            
            # Try Lyrics.ovh API with timeout handling
            lyrics = self._get_lyrics_from_ovh(clean_artist, clean_title)
            if lyrics:
                return lyrics
            
            print("No lyrics found from any source")
            return ""
            
        except Exception as e:
            print(f"Lyrics extraction failed: {e}")
            return ""
    
    def _clean_search_term(self, term: str) -> str:
        """
        Clean search terms for better lyrics matching
        
        Args:
            term: Raw search term
            
        Returns:
            Cleaned search term
        """
        # Remove common video suffixes
        term = re.sub(r'\s*\(.*?\)', '', term)  # Remove parentheses content
        term = re.sub(r'\s*\[.*?\]', '', term)  # Remove brackets content
        term = re.sub(r'\s*-\s*(official|music|video|lyric|audio|ft\.|feat\.|featuring).*$', '', term, flags=re.IGNORECASE)
        term = re.sub(r'\s*(official|music|video|lyric|audio|ft\.|feat\.|featuring)\s*', ' ', term, flags=re.IGNORECASE)
        term = re.sub(r'\s*(4K|HD|HQ|remaster|remastered)\s*', ' ', term, flags=re.IGNORECASE)
        term = re.sub(r'\s+', ' ', term).strip()  # Clean multiple spaces
        
        # For artist names, remove common suffixes
        if 'VEVO' in term:
            term = re.sub(r'VEVO$', '', term, flags=re.IGNORECASE).strip()
        
        return term
    
    def _get_lyrics_from_ovh(self, artist: str, title: str) -> str:
        """
        Get lyrics from Lyrics.ovh API
        
        Args:
            artist: Artist name
            title: Song title
            
        Returns:
            Lyrics text or empty string
        """
        try:
            url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                lyrics = data.get('lyrics', '').strip()
                if lyrics:
                    print(f"Found lyrics from Lyrics.ovh ({len(lyrics)} chars)")
                    return lyrics
            
        except requests.exceptions.Timeout:
            print(f"Lyrics.ovh API timeout - skipping lyrics search")
        except Exception as e:
            print(f"Lyrics.ovh API failed: {e}")
        
        return ""
    
    def _scrape_lyrics_genius(self, artist: str, title: str) -> str:
        """
        Scrape lyrics from Genius.com as fallback
        
        Args:
            artist: Artist name
            title: Song title
            
        Returns:
            Lyrics text or empty string
        """
        try:
            # Search for the song on Genius
            search_query = f"{artist} {title}".replace(' ', '%20')
            search_url = f"https://genius.com/search?q={search_query}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return ""
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the first song link
            song_links = soup.find_all('a', class_='mini_card')
            if not song_links:
                return ""
            
            song_url = 'https://genius.com' + song_links[0].get('href')
            
            # Get lyrics from the song page
            song_response = requests.get(song_url, headers=headers, timeout=10)
            if song_response.status_code != 200:
                return ""
            
            song_soup = BeautifulSoup(song_response.content, 'html.parser')
            
            # Find lyrics container (Genius uses different selectors)
            lyrics_containers = song_soup.find_all('div', {'data-lyrics-container': 'true'})
            
            if lyrics_containers:
                lyrics_text = ''
                for container in lyrics_containers:
                    lyrics_text += container.get_text(separator='\n', strip=True) + '\n'
                
                if lyrics_text.strip():
                    print(f"Found lyrics from Genius.com ({len(lyrics_text)} chars)")
                    return lyrics_text.strip()
            
        except Exception as e:
            print(f"Genius scraping failed: {e}")
        
        return ""
