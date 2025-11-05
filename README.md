# 🤖 Multimodal Brain

> A comprehensive multimodal processing system that accepts YouTube links, documents, images, audio, and video files to build an intelligent knowledge base with AI-powered question answering.

## ✨ Features

- **📺 YouTube Processing**: Extract transcripts AND lyrics from YouTube videos
- **📄 Document Processing**: PDF, DOCX, PPTX, MD, TXT files
- **🖼️ Image Analysis**: PNG, JPG image content analysis using Gemini Vision
- **🎵 Audio Transcription**: MP3 audio file transcription
- **🎬 Video Processing**: MP4 video content analysis and audio transcription
- **🔍 Semantic Search**: FAISS-powered vector database for intelligent content retrieval
- **🤖 AI-Powered Q&A**: Natural language question answering using Gemini AI
- **🌐 Web Interface**: Clean, intuitive Streamlit UI

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Gemini API Key
- ffmpeg (for audio/video processing)

### Installation
```bash
# Clone repository
git clone https://github.com/TejaswarYambadi/Multi_Model_Brain.git
cd Multi_Model_Brain

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install streamlit google-genai PyPDF2 python-docx python-pptx Pillow pytube youtube-transcript-api SpeechRecognition pydub moviepy faiss-cpu scikit-learn numpy requests beautifulsoup4

# Set API key
echo GEMINI_API_KEY=your_api_key_here > .env

# Run application
streamlit run app.py --server.port 5000
```

## 📖 Usage

### 1. Upload Files
- **Documents**: PDF, DOCX, PPTX, MD, TXT
- **Media**: PNG, JPG, MP3, MP4
- **YouTube**: Paste any YouTube video URL

### 2. Process Content
Click "🔄 Process Files" to extract and index content

### 3. Ask Questions
Enter natural language questions about your content:
- "What is the main topic discussed?"
- "Summarize the key points"
- "What are the lyrics about?"

## 🧪 Test Cases for YouTube Links

### Test Case 1: Music Video with Lyrics
```
URL: https://www.youtube.com/watch?v=YQHsXMglC9A
Expected: Extract transcript + lyrics
Questions:
- "What is this song about?"
- "What are the main themes in the lyrics?"
- "Summarize the video content"
```

### Test Case 2: Educational Content
```
URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Expected: Extract transcript only
Questions:
- "What is the main topic?"
- "List the key points mentioned"
- "Who is the speaker?"
```

### Test Case 3: No Transcript Available
```
URL: [Video without captions]
Expected: Metadata only
Questions:
- "What information is available?"
- "Describe the video title and channel"
```

## 🏗️ Architecture

```
├── app.py                    # Main Streamlit application
├── processors/
│   ├── document_processor.py # PDF, DOCX, PPTX, TXT processing
│   ├── image_processor.py    # Image analysis with Gemini Vision
│   ├── audio_processor.py    # Audio transcription
│   ├── video_processor.py    # Video processing
│   └── youtube_processor.py  # YouTube transcript + lyrics extraction
├── database/
│   └── vector_db.py         # FAISS vector database
├── utils/
│   ├── gemini_client.py     # Gemini AI client
│   └── file_utils.py        # File utilities
└── README.md
```

## 🔧 Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Supported File Types
- **Documents**: .pdf, .docx, .pptx, .md, .txt
- **Images**: .png, .jpg, .jpeg
- **Audio**: .mp3
- **Video**: .mp4
- **YouTube**: Any valid YouTube video URL

## 🧪 Testing

### Run Test Cases
```bash
# Test individual processors
python -c "from processors.youtube_processor import YouTubeProcessor; print(YouTubeProcessor().process('https://www.youtube.com/watch?v=YQHsXMglC9A'))"

# Test full application
streamlit run app.py --server.port 5000
```

### Expected Outputs
- **Transcript**: Spoken content from video
- **Lyrics**: Song lyrics (for music videos)
- **Metadata**: Title, channel, URL
- **AI Answers**: Context-aware responses

## 🚀 Deployment

### 💻 Deploy on Another PC (Step-by-Step)

#### Step 1: System Requirements
```bash
# Check Python version (3.11+ required)
python --version

# Install Git (if not installed)
# Windows: Download from https://git-scm.com/
# Linux: sudo apt install git
# Mac: brew install git
```

#### Step 2: Install FFmpeg
```bash
# Windows (using chocolatey)
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
# Extract and add to PATH

# Linux
sudo apt update
sudo apt install ffmpeg

# Mac
brew install ffmpeg
```

#### Step 3: Clone and Setup Project
```bash
# Clone the repository
git clone https://github.com/TejaswarYambadi/Multi_Model_Brain.git
cd Multi_Model_Brain

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### Step 4: Install Dependencies
```bash
# Install all required packages
pip install streamlit google-genai PyPDF2 python-docx python-pptx Pillow pytube youtube-transcript-api SpeechRecognition pydub moviepy faiss-cpu scikit-learn numpy requests beautifulsoup4

# Or create requirements.txt and install
pip freeze > requirements.txt
pip install -r requirements.txt
```

#### Step 5: Configure Environment
```bash
# Create .env file
echo GEMINI_API_KEY=your_actual_api_key_here > .env

# Or manually create .env file with:
# GEMINI_API_KEY=your_actual_api_key_here
```

#### Step 6: Test Installation
```bash
# Test individual components
python -c "import streamlit; print('Streamlit OK')"
python -c "from processors.youtube_processor import YouTubeProcessor; print('YouTube processor OK')"

# Test FFmpeg
ffmpeg -version
```

#### Step 7: Run Application
```bash
# Start the application
streamlit run app.py --server.port 5000

# Access via browser:
# http://localhost:5000
```

#### Step 8: Network Access (Optional)
```bash
# To access from other devices on network
streamlit run app.py --server.port 5000 --server.address 0.0.0.0

# Access via: http://YOUR_PC_IP:5000
```

### 🐳 Docker Deployment
```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"]
```

```bash
# Build and run with Docker
docker build -t multimodal-brain .
docker run -p 5000:5000 -e GEMINI_API_KEY=your_key multimodal-brain
```

### ☁️ Cloud Deployment

#### Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0" > Procfile

# Deploy
heroku create your-app-name
heroku config:set GEMINI_API_KEY=your_key
git push heroku main
```

#### Railway/Render
```bash
# Create start command in platform:
streamlit run app.py --server.port $PORT --server.address 0.0.0.0

# Add environment variable:
GEMINI_API_KEY=your_key
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Google Gemini**: AI-powered analysis and Q&A
- **Streamlit**: Web framework
- **FAISS**: Vector similarity search
- **Lyrics.ovh**: Lyrics API
- **YouTube Transcript API**: Transcript extraction

---

**Built with ❤️ for Multimodal AI Processing**