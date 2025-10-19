import streamlit as st
from processors.document_processor import DocumentProcessor
import tempfile
import os

st.title("PDF Test")

uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])

if uploaded_file:
    st.write(f"File: {uploaded_file.name}")
    
    if st.button("Test PDF Processing"):
        try:
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(uploaded_file.getvalue())
                temp_path = tmp.name
            
            # Process with document processor
            processor = DocumentProcessor()
            content = processor.process(temp_path)
            
            st.success("PDF processed successfully!")
            st.write(f"Content length: {len(content)}")
            st.text_area("Content preview:", content[:500], height=200)
            
            # Cleanup
            os.unlink(temp_path)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback
            st.error(traceback.format_exc())