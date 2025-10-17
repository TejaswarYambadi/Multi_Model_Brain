import os
import tempfile
import streamlit as st
from pathlib import Path

def get_file_type(filename: str) -> str:
    """
    Determine the file type category based on file extension
    
    Args:
        filename: Name of the file
        
    Returns:
        File type category (document, image, audio, video)
    """
    extension = Path(filename).suffix.lower()
    
    document_extensions = ['.pdf', '.docx', '.pptx', '.md', '.txt']
    image_extensions = ['.png', '.jpg', '.jpeg']
    audio_extensions = ['.mp3']
    video_extensions = ['.mp4']
    
    if extension in document_extensions:
        return 'document'
    elif extension in image_extensions:
        return 'image'
    elif extension in audio_extensions:
        return 'audio'
    elif extension in video_extensions:
        return 'video'
    else:
        return 'unknown'

def save_uploaded_file(uploaded_file) -> str:
    """
    Save uploaded file to temporary directory
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Path to saved temporary file
    """
    try:
        # Create temporary file with original extension
        suffix = Path(uploaded_file.name).suffix
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        
        # Write uploaded file content to temporary file
        temp_file.write(uploaded_file.getvalue())
        temp_file.close()
        
        return temp_file.name
        
    except Exception as e:
        raise Exception(f"Error saving uploaded file: {str(e)}")

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted file size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def validate_file_type(filename: str, allowed_types: list) -> bool:
    """
    Validate if file type is allowed
    
    Args:
        filename: Name of the file
        allowed_types: List of allowed file extensions
        
    Returns:
        True if file type is allowed, False otherwise
    """
    extension = Path(filename).suffix.lower()
    return extension in allowed_types

def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove null bytes and other problematic characters
    text = text.replace('\x00', '').replace('\r', '\n')
    
    # Normalize line breaks
    text = text.replace('\n\n\n', '\n\n')
    
    return text.strip()
