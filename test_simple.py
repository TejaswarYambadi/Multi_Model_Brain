import streamlit as st

st.title("Simple Test")

uploaded_file = st.file_uploader("Test upload", type=['txt'])

if uploaded_file:
    st.write(f"File name: {uploaded_file.name}")
    st.write(f"File size: {uploaded_file.size}")
    
    if st.button("Test Process"):
        content = uploaded_file.read().decode('utf-8')
        st.write(f"Content: {content[:100]}...")
        st.success("Processing works!")