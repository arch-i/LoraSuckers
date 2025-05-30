# 🎬 BrollGen - AI-Powered B-Roll Video Generation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Hackathon Project](https://img.shields.io/badge/hackathon-2025-orange.svg)](https://github.com/arch-i/LoraSuckers)

> Transform any video into engaging content with AI-generated B-roll footage

## 🚀 Overview

BrollGen is an intelligent pipeline that automatically generates contextual B-roll footage for videos. By analyzing video transcripts, identifying key moments, and generating relevant visual content, it enhances storytelling and viewer engagement.

## 🎯 Features

- **🎤 Smart Transcription**: Convert speech to text using Whisper AI
- **🔍 Key Moment Detection**: Extract meaningful segments from transcripts
- **🎨 Dynamic Image Generation**: Create contextual images using AI prompts
- **🎬 Video Synthesis**: Transform images into smooth B-roll videos
- **🤖 Quality Assurance**: AI judge evaluates and refines output quality
- **⚡ Automated Pipeline**: End-to-end processing with minimal human intervention

## 🏗️ Architecture

```
Video Input → Transcription → Key Moment Extraction → Image Generation → Video Creation → Quality Check → Final Output
```

### Pipeline Components

1. **Transcription Service** - Converts audio to text using Whisper
2. **Content Analyzer** - Identifies key moments and themes
3. **Image Generator** - Creates contextual visuals using AI
4. **Video Synthesizer** - Transforms images to video sequences using AI
5. **Quality Judge** - Evaluates output and triggers regeneration if needed

## 📁 Project Structure

```
brollGen/
├── config/               # Configuration files, if any
├── data/                 # Input/output data
├── docs/                 # Documentation
├── src/                  # Core application code
└── utils/                # Utility scripts
```

## 🔧 Tech Stack

- **AI/ML**: OpenAI Whisper, (image models, as yet undecided), LLMs
- **Backend**: Python
- **Video Processing**: FFmpeg, OpenCV
- **Infrastructure**: Supabase
- **API Integration**: OpenAI, ElevenLabs

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/arch-i/LoraSuckers.git
cd brollGen

# Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the application
python src/main.py
```

## 📖 Usage

### Command Line Interface
```bash
# Generate B-roll for a video
python src/main.py --input video.mp4 --output output/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- OpenAI for Whisper and GPT models
- Media generation models

- **Repository**: [github.com/arch-i/LoraSuckers](https://github.com/arch-i/LoraSuckers)