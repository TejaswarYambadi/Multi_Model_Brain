import streamlit as st
from processors.document_processor import DocumentProcessor
from utils.file_utils import save_uploaded_file, get_file_type

st.title("Debug File Processing")

uploaded_file = st.file_uploader("Upload a file", type=['pdf', 'txt', 'docx'])

if uploaded_file and st.button("Debug Process"):
    st.write("=== DEBUG INFO ===")
    st.write(f"File name: {uploaded_file.name}")
    st.write(f"File size: {uploaded_file.size}")
    
    try:
        # Step 1: Save file
        st.write("Step 1: Saving file...")
        temp_path = save_uploaded_file(uploaded_file)
        st.write(f"✅ Saved to: {temp_path}")
        
        # Step 2: Get file type
        st.write("Step 2: Getting file type...")
        file_type = get_file_type(uploaded_file.name)
        st.write(f"✅ File type: {file_type}")
        
        # Step 3: Process file
        st.write("Step 3: Processing file...")
        if file_type == 'document':
            processor = DocumentProcessor()
            content = processor.process(temp_path)
            st.write(f"✅ Content extracted: {len(content)} characters")
            st.text_area("Content preview:", content[:500], height=200)
        else:
            st.write(f"❌ Unsupported file type for this test: {file_type}")
            
        # Cleanup
        import os
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            st.write("✅ Temp file cleaned up")
            
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        import traceback
        st.error(traceback.format_exc())