# 🤖 Multimodal Data Processing System

A comprehensive Streamlit-based application that processes various file types (documents, images, audio, video, YouTube) and provides intelligent question-answering using Gemini AI and vector search capabilities.

## 🌟 Features

- **📄 Document Processing**: PDF, DOCX, PPTX, MD, TXT files
- **🖼️ Image Analysis**: PNG, JPG image content analysis using Gemini Vision
- **🎵 Audio Transcription**: MP3 audio file transcription
- **🎬 Video Processing**: MP4 video content analysis and audio transcription
- **📺 YouTube Support**: Automatic transcript extraction from YouTube videos
- **🔍 Semantic Search**: FAISS-powered vector database for intelligent content retrieval using TF-IDF
- **🤖 AI-Powered Q&A**: Natural language question answering using Gemini AI
- **🌐 Web Interface**: Clean, intuitive Streamlit UI

## 📋 Prerequisites

Before installing this application, ensure you have the following:

- **Python 3.11 or higher** (Python 3.11, 3.12 recommended)
- **Google Gemini API Key** (free tier available at https://aistudio.google.com/apikey)
- **Internet connection** for API calls and package installation
- **Operating System**: Windows, macOS, or Linux

### System Requirements

- **RAM**: Minimum 4GB (8GB recommended for video processing)
- **Disk Space**: At least 2GB free space
- **ffmpeg**: Required for audio/video processing (installation instructions below)

## 🚀 Complete Installation & Deployment Guide

Follow these step-by-step instructions to deploy this application on another PC:

### Step 1: Install Python

1. **Download Python**:
   - Visit https://www.python.org/downloads/
   - Download Python 3.11 or higher for your operating system
   - During installation, **check "Add Python to PATH"**

2. **Verify Installation**:
   ```bash
   python --version
   # Should show Python 3.11.x or higher
   
   pip --version
   # Should show pip version
   ```

### Step 2: Install ffmpeg (Required for Audio/Video Processing)

#### Windows:
1. Download ffmpeg from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH:
   - Right-click "This PC" → Properties → Advanced System Settings
   - Environment Variables → System Variables → Path → Edit
   - Add `C:\ffmpeg\bin`

#### macOS:
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ffmpeg
brew install ffmpeg
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

**Verify ffmpeg Installation**:
```bash
ffmpeg -version
```

### Step 3: Download the Project

**Option A: If you have a ZIP file**
1. Extract the ZIP file to your desired location
2. Navigate to the extracted folder

**Option B: If using Git**
```bash
git clone <repository-url>
cd multimodal-data-processing-system
```

### Step 4: Set Up Python Environment

1. **Open Terminal/Command Prompt** in the project directory

2. **Create a Virtual Environment** (Recommended):
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Upgrade pip**:
   ```bash
   python -m pip install --upgrade pip
   ```

### Step 5: Install Required Packages

Install all dependencies using pip:

```bash
pip install streamlit google-genai PyPDF2 python-docx python-pptx Pillow pytube youtube-transcript-api SpeechRecognition pydub moviepy faiss-cpu scikit-learn numpy
```

**Alternative: Install from requirements.txt** (if provided):
```bash
pip install -r requirements.txt
```

### Step 6: Get Your Gemini API Key

1. Visit https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the generated API key (starts with "AIza...")
5. Keep it safe - you'll need it in the next step

### Step 7: Configure Environment Variables

Create a `.env` file in the project root directory or set environment variables:

**Option A: Create .env file** (Recommended)
Create a file named `.env` in the project root:
```env
GEMINI_API_KEY=your_api_key_here
```

**Option B: Set System Environment Variable**

#### Windows:
```cmd
setx GEMINI_API_KEY "your_api_key_here"
```

#### macOS/Linux:
```bash
export GEMINI_API_KEY="your_api_key_here"

# To make it permanent, add to ~/.bashrc or ~/.zshrc:
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 8: Verify Project Structure

Ensure your project has the following structure:

```
multimodal-data-processing-system/
├── app.py                          # Main application file
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── processors/
│   ├── document_processor.py       # PDF, DOCX, PPTX, TXT processing
│   ├── image_processor.py          # Image analysis
│   ├── audio_processor.py          # Audio transcription
│   ├── video_processor.py          # Video processing
│   └── youtube_processor.py        # YouTube transcript extraction
├── database/
│   └── vector_db.py                # Vector database for search
├── utils/
│   ├── gemini_client.py            # Gemini AI client
│   └── file_utils.py               # File utilities
├── README.md                       # This file
└── requirements.txt                # Python dependencies (optional)
```

### Step 9: Run the Application

1. **Ensure you're in the project directory** with your virtual environment activated

2. **Start the Application**:
   ```bash
   streamlit run app.py --server.port 5000
   ```

3. **Access the Application**:
   - The application will automatically open in your default web browser
   - If not, navigate to: http://localhost:5000
   - You should see the "Multimodal Data Processing System" interface

### Step 10: Test the Application

1. **Upload a Test File**:
   - Click "Browse files" in the sidebar
   - Upload a PDF, image, or text file
   - Click "🔄 Process Files"

2. **Ask a Question**:
   - After processing, enter a question about your content
   - Click "🔍 Search & Answer"
   - View the AI-generated response

## 📖 How to Use

### Processing Files

1. **Supported File Types**:
   - Documents: `.pdf`, `.docx`, `.pptx`, `.md`, `.txt`
   - Images: `.png`, `.jpg`, `.jpeg`
   - Audio: `.mp3`
   - Video: `.mp4`
   - YouTube: Enter video URL in the input field

2. **Upload and Process**:
   - Click "Browse files" in the sidebar
   - Select one or multiple files
   - For YouTube videos, paste the URL
   - Click "🔄 Process Files"
   - Wait for processing to complete

### Asking Questions

1. Once files are processed, they appear in the "Processed Files" list
2. Enter your question in the main area
3. Click "🔍 Search & Answer"
4. The system will:
   - Search through your knowledge base
   - Retrieve relevant content
   - Generate an AI-powered answer using Gemini
   - Show source documents used

### Managing Your Knowledge Base

- **View Processed Files**: Expand files in the sidebar to see content previews
- **Clear All Files**: Click "🗑️ Clear All" to reset the knowledge base
- **Statistics**: View file counts and types in the sidebar

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. "ModuleNotFoundError"
**Problem**: Missing Python packages
**Solution**:
```bash
pip install <missing-package-name>
# Or reinstall all dependencies
pip install -r requirements.txt
```

#### 2. "GEMINI_API_KEY not found"
**Problem**: API key not configured
**Solution**: 
- Check your `.env` file exists and contains the key
- Or set the environment variable as shown in Step 7

#### 3. "ffmpeg not found" (Audio/Video processing fails)
**Problem**: ffmpeg not installed or not in PATH
**Solution**: 
- Reinstall ffmpeg following Step 2
- Verify with `ffmpeg -version`

#### 4. "Speech recognition failed"
**Problem**: Audio quality too poor or no internet connection
**Solution**:
- Ensure good audio quality
- Check internet connection (Google Speech Recognition requires internet)

#### 5. Port 5000 already in use
**Problem**: Another application is using port 5000
**Solution**:
```bash
streamlit run app.py --server.port 8501
```

#### 6. YouTube transcript not available
**Problem**: Video doesn't have captions
**Solution**: 
- Only videos with captions/transcripts can be processed
- Try a different video

## 🔐 Security & Privacy

- **API Keys**: Never commit your `.env` file or API keys to version control
- **Local Processing**: All file processing happens locally on your machine
- **API Calls**: Image analysis and question answering use Google's Gemini API
- **Data Storage**: Processed content is stored in memory (session-based, not persistent)

## 📦 Dependencies

### Core Dependencies
- `streamlit` - Web interface framework
- `google-genai` - Gemini AI integration
- `faiss-cpu` - Vector similarity search
- `scikit-learn` - TF-IDF vectorization for semantic search

### Document Processing
- `PyPDF2` - PDF text extraction
- `python-docx` - Word document processing
- `python-pptx` - PowerPoint processing
- `Pillow` - Image handling

### Media Processing
- `pytube` - YouTube video downloading
- `youtube-transcript-api` - YouTube transcript extraction
- `SpeechRecognition` - Audio transcription
- `pydub` - Audio file handling
- `moviepy` - Video processing
- `ffmpeg` - Media encoding/decoding (system dependency)

### Utilities
- `numpy` - Numerical operations

## 🌐 Deployment Options

### Local Development
```bash
streamlit run app.py --server.port 5000
```

### Network Access (Allow other devices on your network)
```bash
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```
Access from other devices: `http://<your-ip-address>:5000`

### Production Deployment

For production deployment, consider:
- **Streamlit Cloud**: Free hosting at https://streamlit.io/cloud
- **Docker**: Containerize the application
- **Cloud Platforms**: Deploy to AWS, Google Cloud, Azure, etc.

## 💡 Tips for Best Results

1. **File Quality**:
   - Use high-quality PDFs with selectable text (not scanned images)
   - Ensure images are clear and well-lit
   - Audio files should have minimal background noise

2. **Question Formulation**:
   - Be specific in your questions
   - Reference context from your uploaded files
   - Ask one question at a time for best results

3. **Performance**:
   - Process files in smaller batches
   - Large video files may take time to process
   - Clear old files regularly to maintain performance

## 🛠️ Advanced Configuration

### Streamlit Configuration

Edit `.streamlit/config.toml` to customize:

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Gemini Model Selection

Edit `utils/gemini_client.py` to change models:
- Default: `gemini-2.5-flash` (fast, cost-effective)
- Pro: `gemini-2.5-pro` (higher quality, slower)

## 📝 System Architecture

### Processing Pipeline

1. **File Upload** → User uploads file via Streamlit
2. **File Type Detection** → System identifies file type
3. **Content Extraction** → Appropriate processor extracts content
4. **Vectorization** → Content converted to TF-IDF vectors
5. **Storage** → Vectors stored in FAISS index
6. **Query** → User asks question
7. **Search** → Vector similarity search finds relevant content
8. **AI Response** → Gemini generates answer from context

### Components

- **Frontend**: Streamlit web interface
- **Processors**: Specialized modules for each file type
- **Vector Database**: FAISS for fast similarity search
- **AI Engine**: Google Gemini for image analysis and Q&A
- **Storage**: In-memory session storage

## 🆘 Getting Help

If you encounter issues:

1. Check this README's Troubleshooting section
2. Verify all prerequisites are installed
3. Ensure your API key is valid and has quota remaining
4. Check Python and package versions match requirements
5. Look for error messages in the terminal

## 📄 License

This project is provided as-is for educational and commercial use.

## 🙏 Acknowledgments

- **Google Gemini**: AI-powered image analysis and question answering
- **Streamlit**: Modern web framework for Python
- **FAISS**: Efficient similarity search
- **Open Source Community**: All the amazing libraries that make this possible

---

**Built with ❤️ for Multimodal Data Processing**

Last Updated: October 2025
