import streamlit as st
import os
import tempfile
from pathlib import Path
import traceback

from processors.document_processor import DocumentProcessor
from processors.image_processor import ImageProcessor
from processors.audio_processor import AudioProcessor
from processors.video_processor import VideoProcessor
from processors.youtube_processor import YouTubeProcessor
from database.vector_db import VectorDatabase
from utils.gemini_client import GeminiClient
from utils.file_utils import get_file_type, save_uploaded_file

# Initialize session state
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = VectorDatabase()
if 'gemini_client' not in st.session_state:
    st.session_state.gemini_client = GeminiClient()
if 'processed_files' not in st.session_state:
    # Rebuild processed files list from database metadata
    processed_files = []
    for i, metadata in enumerate(st.session_state.vector_db.metadata):
        filename = metadata.get('filename', f'Document {i+1}')
        file_type = metadata.get('type', 'unknown')
        chunk_id = metadata.get('chunk_id', 0)
        
        # Only add unique files (first chunk of each)
        if chunk_id == 0 or 'chunk_id' not in metadata:
            if filename not in [f['name'] for f in processed_files]:
                # Get the content for preview
                content_idx = i
                if content_idx < len(st.session_state.vector_db.documents):
                    content = st.session_state.vector_db.documents[content_idx]
                    processed_files.append({
                        'name': filename,
                        'type': file_type,
                        'content_preview': content[:200] + "..." if len(content) > 200 else content
                    })
    st.session_state.processed_files = processed_files

# Initialize processors
@st.cache_resource
def get_processors():
    return {
        'document': DocumentProcessor(),
        'image': ImageProcessor(),
        'audio': AudioProcessor(),
        'video': VideoProcessor(),
        'youtube': YouTubeProcessor()
    }

processors = get_processors()

st.title("🤖 Multimodal Data Processing System")
st.markdown("Upload files or provide YouTube URLs to build your knowledge base, then ask questions!")

# Sidebar for file uploads
with st.sidebar:
    st.header("📁 Upload Files")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'docx', 'pptx', 'md', 'txt', 'png', 'jpg', 'jpeg', 'mp3', 'mp4'],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, PPTX, MD, TXT, PNG, JPG, MP3, MP4"
    )
    
    # YouTube URL input
    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Enter a YouTube video URL to extract transcript"
    )
    
    # Process files button
    if st.button("🔄 Process Files", type="primary"):
        if uploaded_files or youtube_url:
            with st.spinner("Processing files..."):
                try:
                    # Process uploaded files
                    for uploaded_file in uploaded_files or []:
                        if uploaded_file.name not in [f['name'] for f in st.session_state.processed_files]:
                            # Save uploaded file temporarily
                            temp_path = save_uploaded_file(uploaded_file)
                            
                            try:
                                file_type = get_file_type(uploaded_file.name)
                                content = ""
                                
                                if file_type == 'document':
                                    content = processors['document'].process(temp_path)
                                elif file_type == 'image':
                                    content = processors['image'].process(temp_path)
                                elif file_type == 'audio':
                                    content = processors['audio'].process(temp_path)
                                elif file_type == 'video':
                                    content = processors['video'].process(temp_path)
                                
                                if content:
                                    # Add to vector database
                                    st.session_state.vector_db.add_document(
                                        content, 
                                        metadata={'filename': uploaded_file.name, 'type': file_type}
                                    )
                                    
                                    st.session_state.processed_files.append({
                                        'name': uploaded_file.name,
                                        'type': file_type,
                                        'content_preview': content[:200] + "..." if len(content) > 200 else content
                                    })
                                    
                            finally:
                                # Clean up temp file
                                if os.path.exists(temp_path):
                                    os.unlink(temp_path)
                    
                    # Process YouTube URL
                    if youtube_url and youtube_url not in [f['name'] for f in st.session_state.processed_files]:
                        content = processors['youtube'].process(youtube_url)
                        if content:
                            st.session_state.vector_db.add_document(
                                content,
                                metadata={'filename': youtube_url, 'type': 'youtube'}
                            )
                            
                            st.session_state.processed_files.append({
                                'name': youtube_url,
                                'type': 'youtube',
                                'content_preview': content[:200] + "..." if len(content) > 200 else content
                            })
                    
                    st.success(f"✅ Processed {len(uploaded_files or []) + (1 if youtube_url else 0)} items successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error processing files: {str(e)}")
                    st.error(traceback.format_exc())
        else:
            st.warning("Please upload files or provide a YouTube URL first.")

    # Display processed files
    if st.session_state.processed_files:
        st.subheader("📋 Processed Files")
        for file_info in st.session_state.processed_files:
            with st.expander(f"📄 {file_info['name']} ({file_info['type']})"):
                st.text(file_info['content_preview'])
        
        if st.button("🗑️ Clear All"):
            st.session_state.processed_files = []
            st.session_state.vector_db.clear_all()
            st.success("All files cleared from database!")
            st.rerun()

# Main content area for queries
st.header("❓ Ask Questions")

if not st.session_state.processed_files:
    st.info("👆 Please upload and process some files first to start asking questions.")
else:
    query = st.text_input(
        "Enter your question:",
        placeholder="What is the main topic discussed in the documents?",
        help="Ask any question about your uploaded content"
    )
    
    if st.button("🔍 Search & Answer", type="primary") or query:
        if query:
            with st.spinner("Searching knowledge base and generating answer..."):
                try:
                    # Search for relevant content
                    results = st.session_state.vector_db.search(query, top_k=3)
                    
                    if results:
                        # Prepare context for Gemini
                        context = "\n\n".join([
                            f"Source: {result['metadata']['filename']}\n{result['content']}" 
                            for result in results
                        ])
                        
                        # Generate answer using Gemini
                        answer = st.session_state.gemini_client.answer_question(query, context)
                        
                        # Display answer
                        st.subheader("🤖 Answer")
                        st.write(answer)
                        
                        # Display sources
                        st.subheader("📚 Sources")
                        for i, result in enumerate(results, 1):
                            with st.expander(f"Source {i}: {result['metadata']['filename']} (Score: {result['score']:.3f})"):
                                st.text(result['content'][:500] + "..." if len(result['content']) > 500 else result['content'])
                    else:
                        st.warning("No relevant content found for your query. Try rephrasing or adding more content.")
                        
                except Exception as e:
                    st.error(f"❌ Error processing query: {str(e)}")
                    st.error(traceback.format_exc())
        else:
            st.warning("Please enter a question.")

# Statistics
if st.session_state.processed_files:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Statistics")
    st.sidebar.metric("Files Processed", len(st.session_state.processed_files))
    
    # Count by type
    type_counts = {}
    for file_info in st.session_state.processed_files:
        type_counts[file_info['type']] = type_counts.get(file_info['type'], 0) + 1
    
    for file_type, count in type_counts.items():
        st.sidebar.metric(f"{file_type.title()} Files", count)
