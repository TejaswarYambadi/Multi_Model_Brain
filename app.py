import streamlit as st
import os
import tempfile
from pathlib import Path
import traceback
import time

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
    st.session_state.processed_files = []

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
    
    # Debug: Clear session button
    if st.button("🔄 Reset Session", help="Clear all session data"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Session cleared! Please refresh the page.")
        st.rerun()
    
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
            try:
                processed_count = 0
                
                # Process uploaded files
                for uploaded_file in uploaded_files or []:
                    # Check if file already processed
                    existing_files = [f['name'] for f in st.session_state.processed_files]
                    
                    if uploaded_file.name not in existing_files:
                        with st.spinner(f"Processing {uploaded_file.name}..."):
                            try:
                                # Save uploaded file temporarily
                                temp_path = save_uploaded_file(uploaded_file)
                                
                                # Get file type and process
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
                                
                                if content and len(content.strip()) > 10:
                                    # Add to vector database
                                    st.session_state.vector_db.add_document(
                                        content, 
                                        metadata={'filename': uploaded_file.name, 'type': file_type}
                                    )
                                    
                                    # Add to processed files
                                    st.session_state.processed_files.append({
                                        'name': uploaded_file.name,
                                        'type': file_type,
                                        'content_preview': content[:200] + "..." if len(content) > 200 else content
                                    })
                                    processed_count += 1
                                
                                # Clean up temp file
                                if os.path.exists(temp_path):
                                    os.unlink(temp_path)
                                    
                            except Exception as e:
                                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                    
                # Process YouTube URL
                if youtube_url and youtube_url not in [f['name'] for f in st.session_state.processed_files]:
                    with st.spinner("Processing YouTube video..."):
                        try:
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
                                processed_count += 1
                        except Exception as e:
                            st.error(f"Error processing YouTube URL: {str(e)}")
                
                # Show results
                if processed_count > 0:
                    st.success(f"✅ Successfully processed {processed_count} file(s)!")
                    st.rerun()
                else:
                    st.error("❌ No files were processed. Please check file format and try again.")
                    
            except Exception as e:
                st.error(f"❌ Error during processing: {str(e)}")
        else:
            st.warning("📁 Please upload files or provide a YouTube URL first.")

    # Show delete message if exists with auto-clear after 5 seconds
    if hasattr(st.session_state, 'delete_message') and hasattr(st.session_state, 'delete_time'):
        current_time = time.time()
        if current_time - st.session_state.delete_time < 5:
            st.success(st.session_state.delete_message)
        else:
            del st.session_state.delete_message
            del st.session_state.delete_time
    
    # Display processed files
    if st.session_state.processed_files:
        st.subheader("📋 Processed Files")
        # Sort files by type and name for consistent ordering
        sorted_files = sorted(st.session_state.processed_files, key=lambda x: (x['type'], x['name'].lower()))
        for i, file_info in enumerate(sorted_files):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                with st.expander(f"📄 {file_info['name']} ({file_info['type']})"):
                    st.text(file_info['content_preview'])
            
            with col2:
                if st.button("🗑️", key=f"delete_{i}", help=f"Delete {file_info['name']}"):
                    filename_to_delete = file_info['name']
                    file_type = file_info['type']
                    
                    # Remove from processed files list
                    st.session_state.processed_files = [
                        f for f in st.session_state.processed_files 
                        if f['name'] != filename_to_delete
                    ]
                    
                    # Remove from vector database
                    remaining_docs = []
                    remaining_metadata = []
                    
                    for j, metadata in enumerate(st.session_state.vector_db.metadata):
                        if metadata.get('filename') != filename_to_delete:
                            remaining_docs.append(st.session_state.vector_db.documents[j])
                            remaining_metadata.append(metadata)
                    
                    # Clear and rebuild database
                    st.session_state.vector_db.clear_all()
                    for doc, meta in zip(remaining_docs, remaining_metadata):
                        st.session_state.vector_db.add_document(doc, meta)
                    
                    # Store success message in session state
                    type_messages = {
                        'document': f"Document '{filename_to_delete}' removed successfully!",
                        'image': f"Image '{filename_to_delete}' removed successfully!",
                        'audio': f"Audio '{filename_to_delete}' removed successfully!",
                        'video': f"Video '{filename_to_delete}' removed successfully!",
                        'youtube': f"YouTube video removed successfully!"
                    }
                    
                    st.session_state.delete_message = type_messages.get(file_type, f"'{filename_to_delete}' removed successfully!")
                    st.session_state.delete_time = time.time()
                    st.rerun()
        
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
    # Default question suggestions
    st.markdown("**💡 Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Summarize Content", key="summary_btn"):
            st.session_state.suggested_query = "Please provide a comprehensive summary of all the uploaded content."
    
    with col2:
        if st.button("🔍 Key Points", key="keypoints_btn"):
            st.session_state.suggested_query = "What are the main key points and important information from the content?"
    
    with col3:
        if st.button("📊 Main Topics", key="topics_btn"):
            st.session_state.suggested_query = "What are the main topics and themes discussed in the uploaded files?"
    
    st.markdown("---")
    
    # Query input with auto-fill from suggestions
    default_value = getattr(st.session_state, 'suggested_query', '')
    query = st.text_input(
        "Enter your question:",
        value=default_value,
        placeholder="What is the main topic discussed in the documents?",
        help="Ask any question about your uploaded content"
    )
    
    # Clear suggestion after use
    if hasattr(st.session_state, 'suggested_query'):
        del st.session_state.suggested_query
    
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
